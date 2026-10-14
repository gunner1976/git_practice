// Casing design engine - JavaScript port of the Python `casingdesign` package.
// US oilfield units throughout: ft, psi, ppg, in, lb/ft, lbf. Pure functions; no DOM.
/* global CATALOG_DATA */
const Engine = (() => {
  const PSI_PER_FT_PER_PPG = 0.052, E_STEEL = 30e6, ELASTIC_CONST = 46.95e6, WALL_TOL = 0.875;
  const MIN_YIELD_FIT = 15000, STEEL_DENSITY = 0.2833;
  const ppg2grad = ppg => PSI_PER_FT_PER_PPG * ppg, grad2ppg = g => g / PSI_PER_FT_PER_PPG;
  const linspace = (a, b, n) => Array.from({length: n}, (_, i) => n === 1 ? a : a + (b - a) * i / (n - 1));
  // numpy.interp: clamped piecewise-linear on sorted xs
  function interp(x, xs, ys) {
    if (x <= xs[0]) return ys[0]; const n = xs.length; if (x >= xs[n - 1]) return ys[n - 1];
    let lo = 0, hi = n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (xs[m] <= x) lo = m; else hi = m; }
    const f = (x - xs[lo]) / (xs[hi] - xs[lo]); return ys[lo] + f * (ys[hi] - ys[lo]);
  }
  const interpArr = (arr, xs, ys) => arr.map(x => interp(x, xs, ys));
  const key = x => String(+(+x).toPrecision(10));  // matches Python '%g' for catalog ODs

  // ----------------------------------------------------------------- API 5C3 ratings
  const geom = (od, wall) => ({od, wall, id: od - 2 * wall, dt: od / wall,
    area: Math.PI / 4 * (od * od - (od - 2 * wall) ** 2)});
  const burstRating = (g, yp) => WALL_TOL * 2 * yp * g.wall / g.od;
  const bodyYield = (g, yp) => yp * g.area;
  function collapseConstants(yp) {
    const a = 2.8762 + 0.10679e-5 * yp + 0.21301e-10 * yp ** 2 - 0.53132e-16 * yp ** 3;
    const b = 0.026233 + 0.50609e-6 * yp;
    const c = -465.93 + 0.030867 * yp - 0.10483e-7 * yp ** 2 + 0.36989e-13 * yp ** 3;
    const ba = b / a, x = 3 * ba / (2 + ba);
    const f = ELASTIC_CONST * x ** 3 / (yp * (x - ba) * (1 - x) ** 2);
    return {a, b, c, f, g: f * ba};
  }
  function collapseRating(g, yp) {
    const dt = g.dt;
    if (yp < MIN_YIELD_FIT) return Math.min(2 * yp * (dt - 1) / dt ** 2, ELASTIC_CONST / (dt * (dt - 1) ** 2));
    const {a, b, c, f, g: gg} = collapseConstants(yp);
    const bc = b + c / yp;
    const dtYp = (Math.sqrt((a - 2) ** 2 + 8 * bc) + (a - 2)) / (2 * bc);
    const dtPt = yp * (a - f) / (c + yp * (b - gg)), dtTe = (2 + b / a) / (3 * b / a);
    if (dt <= dtYp) return 2 * yp * (dt - 1) / dt ** 2;
    if (dt <= dtPt) return yp * (a / dt - b) - c;
    if (dt <= dtTe) return yp * (f / dt - gg);
    return ELASTIC_CONST / (dt * (dt - 1) ** 2);
  }
  function axialAdjustedYield(yp, sa) { const r = sa / yp; return yp * (Math.sqrt(1 - 0.75 * r * r) - 0.5 * r); }
  function collapseWithAxial(g, yp, sa) {
    if (sa <= 0) return collapseRating(g, yp); if (sa >= yp) return 0;
    return collapseRating(g, axialAdjustedYield(yp, sa));
  }
  // triaxial
  function lame(g, pi, pe, r) { const ri = g.id / 2, ro = g.od / 2, d = ro * ro - ri * ri;
    const k = (pi * ri * ri - pe * ro * ro) / d, m = (pi - pe) * ri * ri * ro * ro / d; return [k - m / (r * r), k + m / (r * r)]; }
  const vme = (sr, st, sa) => Math.sqrt(0.5 * ((sa - st) ** 2 + (st - sr) ** 2 + (sr - sa) ** 2));
  function bendingStress(g, dls) { if (dls === 0) return 0; const R = 180 * 100 * 12 / (Math.PI * dls); return E_STEEL * (g.od / 2) / R; }
  function maxVme(g, pi, pe, F, dls) {
    const sa = F / g.area, sb = bendingStress(g, dls), ri = g.id / 2, ro = g.od / 2; const c = [];
    let [sr, st] = lame(g, pi, pe, ri); c.push(vme(sr, st, sa));
    [sr, st] = lame(g, pi, pe, ro); c.push(vme(sr, st, sa + sb), vme(sr, st, sa - sb));
    [sr, st] = lame(g, pi, pe, ri); c.push(vme(sr, st, sa + sb * ri / ro), vme(sr, st, sa - sb * ri / ro));
    return Math.max(...c);
  }
  // joints
  function roundThreadJoint(g, yp, up, L) { const D = g.od, ajp = Math.PI / 4 * ((D - 0.1425) ** 2 - g.id ** 2);
    const fracture = 0.95 * ajp * up, jump = 0.95 * ajp * L * (0.74 * D ** -0.59 * up / (0.5 * L + 0.14 * D) + yp / (L + 0.14 * D));
    return Math.min(fracture, jump); }
  function buttressJoint(g, yp, up, couplingOd) { const pipe = 0.95 * g.area * up * (1.008 - 0.0396 * (1.083 - yp / up) * g.od);
    if (couplingOd == null) couplingOd = CATALOG_DATA.btc_coupling_od[key(g.od)]; if (couplingOd == null) return pipe;
    return Math.min(pipe, 0.95 * Math.PI / 4 * (couplingOd ** 2 - g.od ** 2) * up); }

  // ----------------------------------------------------------------- catalog
  const grades = Object.fromEntries(CATALOG_DATA.grades.map(g => [g.name, g]));
  const connections = Object.fromEntries(CATALOG_DATA.connections.map(c => [c.name, c]));
  const pipes = CATALOG_DATA.pipes;
  function spec(od, weight, gradeName, connName = 'BTC') {
    const p = pipes.find(p => Math.abs(p.od - od) < 1e-6 && Math.abs(p.weight - weight) < 1e-6); if (!p) throw new Error(`no pipe ${od}" ${weight}#`);
    const gr = grades[gradeName]; if (!gr) throw new Error(`unknown grade ${gradeName}`);
    const cn = connections[connName]; if (!cn) throw new Error(`unknown connection ${connName}`);
    const g = geom(p.od, p.wall), tl = CATALOG_DATA.thread_lengths[`${key(od)}|${connName}`];
    if (cn.kind === 'round' && tl == null) throw new Error(`no ${connName} for ${od}"`);
    const joint = cn.kind === 'round' ? roundThreadJoint(g, gr.min_yield, gr.min_tensile, tl) : cn.kind === 'buttress' ? buttressJoint(g, gr.min_yield, gr.min_tensile) : bodyYield(g, gr.min_yield) * cn.te;
    const by = bodyYield(g, gr.min_yield);
    return {pipe: p, grade: gr, connection: cn, geometry: g, od: p.od, weight: p.weight, wall: p.wall, id: g.id, yield: gr.min_yield,
      label: `${p.od}" ${p.weight}# ${gr.name} ${cn.name}`, burst: burstRating(g, gr.min_yield) * cn.be, collapse: collapseRating(g, gr.min_yield) * cn.ce,
      body_yield: by, joint_strength: joint, tension_rating: Math.min(by, joint)};
  }
  const pipesForOd = od => pipes.filter(p => Math.abs(p.od - od) < 1e-6);
  function candidates(od, gradeNames, connName = 'BTC', sour = false) {
    const names = gradeNames && gradeNames.length ? gradeNames.filter(g => grades[g]) : Object.keys(grades); const out = [];
    for (const p of pipesForOd(od)) for (const gn of names) { if (sour && !grades[gn].sour) continue; try { out.push(spec(od, p.weight, gn, connName)); } catch { /* no such connection for this OD */ } }
    return out;
  }

  // ----------------------------------------------------------------- well helpers
  function trajectory(stations) {
    const st = [...stations].map(s => ({md: +s.md, inclination: +s.inclination, azimuth: +s.azimuth})).sort((a, b) => a.md - b.md).filter((s, i, a) => i === 0 || s.md !== a[i - 1].md);
    if (!st.length || st[0].md !== 0) st.unshift({md: 0, inclination: 0, azimuth: 0});
    const md = st.map(s => s.md), inc = st.map(s => s.inclination), tvd = [0], dls = [0];
    for (let i = 1; i < st.length; i++) { const i1 = inc[i - 1] * Math.PI / 180, i2 = inc[i] * Math.PI / 180, a1 = st[i - 1].azimuth * Math.PI / 180, a2 = st[i].azimuth * Math.PI / 180;
      const dmd = md[i] - md[i - 1]; const cosdl = Math.cos(i2 - i1) - Math.sin(i1) * Math.sin(i2) * (1 - Math.cos(a2 - a1)); const dl = Math.acos(Math.max(-1, Math.min(1, cosdl)));
      const rf = dl < 1e-9 ? 1 : 2 / dl * Math.tan(dl / 2); tvd.push(tvd[i - 1] + dmd / 2 * (Math.cos(i1) + Math.cos(i2)) * rf); dls.push(dmd > 0 ? dl * 180 / Math.PI / dmd * 100 : 0); }
    const n = md.length;
    const dlsAt = x => { let idx = 0; while (idx < n && md[idx] <= x) idx++; return dls[Math.min(Math.max(idx, 1), n - 1)]; };  // searchsorted(side=right) clipped
    return {stations: st, td: md[n - 1], tvd: x => interp(x, md, tvd), inclination: x => interp(x, md, inc), dls: dlsAt};
  }
  const profileAt = (pts, t) => interp(t, pts.map(p => p.tvd), pts.map(p => p.value));
  const profilePressure = (pts, t) => ppg2grad(profileAt(pts, t)) * t;
  const temperature = (f, t) => f.surface_temperature_f + f.geothermal_gradient_f_per_100ft * t / 100;
  function derateFactor(d, T) { if (!d || d.enabled === false) return 1; const slope = d.slope_per_f ?? 0.0003, ref = d.reference_f ?? 70, floor = d.floor ?? 0.8; return Math.max(floor, 1 - slope * Math.max(T - ref, 0)); }
  const isLiner = s => s.type === 'liner';
  function parentOf(well, liner) { if (!isLiner(liner)) return null; const hosts = well.strings.filter(s => s !== liner && s.od > liner.od && (s.hanger_md || 0) <= liner.hanger_md && liner.hanger_md < s.shoe_md); return hosts.length ? hosts.reduce((a, b) => a.od <= b.od ? a : b) : null; }
  const linersOf = (well, parent) => well.strings.filter(s => isLiner(s) && parentOf(well, s) === parent).sort((a, b) => a.hanger_md - b.hanger_md);
  function wellErrors(w) { const out = []; if ((w.trajectory.stations || []).length < 2) out.push('trajectory needs at least surface and TD');
    if (!w.formation.pore_pressure.points.length || !w.formation.fracture_gradient.points.length) out.push('pore pressure and fracture gradient need at least one point each');
    if (!w.strings.length) out.push('add at least one casing string');
    for (const s of w.strings) { const h = s.hanger_md || 0; if (s.toc_md > s.shoe_md) out.push(`${s.name}: top of cement (${s.toc_md}) is below the shoe (${s.shoe_md})`);
      if (h >= s.shoe_md) out.push(`${s.name}: shoe must be below the top of the string`); if (isLiner(s) && h <= 0) out.push(`${s.name}: a liner must hang below surface (liner top MD > 0)`);
      if (!isLiner(s) && h > 0) out.push(`${s.name}: only liners have a top MD (set 0 or change type to liner)`); if (s.hole_size <= s.od) out.push(`${s.name}: hole size must exceed the casing OD`); }
    return out; }
  function wellWarnings(w) { const out = [], traj = trajectory(w.trajectory.stations);
    for (const s of w.strings) { if (s.shoe_md > traj.td) out.push(`${s.name}: shoe ${s.shoe_md} ft is below the surveyed TD ${traj.td} ft`);
      if (isLiner(s)) { const p = parentOf(w, s); if (!p) out.push(`${s.name}: no parent casing found covering the hanger at ${s.hanger_md} ft`);
        else { if (s.toc_md > s.hanger_md) out.push(`${s.name}: TOC ${s.toc_md} ft is below the liner top ${s.hanger_md} ft (uncemented lap)`); if (p.shoe_md - s.hanger_md < 200) out.push(`${s.name}: only ${Math.round(p.shoe_md - s.hanger_md)} ft overlap inside ${p.name}`); } } }
    return out; }

  // ----------------------------------------------------------------- load cases
  const depthGrid = (s, step = 50) => { const h = s.hanger_md || 0, n = Math.max(2, Math.round((s.shoe_md - h) / step) + 1); return linspace(h, s.shoe_md, n); };
  const ctx = well => ({well, traj: trajectory(well.trajectory.stations), pp: well.formation.pore_pressure.points, fg: well.formation.fracture_gradient.points, gas: well.gas_gradient_psi_ft ?? 0.1});
  const mudHyd = (c, md, ppg) => md.map(m => ppg2grad(ppg) * c.traj.tvd(m));
  function annulusAsCemented(c, s, md) { const tocT = c.traj.tvd(s.toc_md), tailTopT = c.traj.tvd(Math.max(s.toc_md, s.shoe_md - s.tail_length));
    const gm = ppg2grad(s.mud_weight), gl = ppg2grad(s.cement_lead_ppg), gt = ppg2grad(s.cement_tail_ppg);
    return md.map(m => { const t = c.traj.tvd(m); return gm * Math.min(t, tocT) + gl * Math.min(Math.max(t - tocT, 0), tailTopT - tocT) + gt * Math.max(t - tailTopT, 0); }); }
  const burstBackup = (c, s, md) => md.map(m => { const t = c.traj.tvd(m), mud = ppg2grad(s.mud_weight) * t; return m >= s.toc_md ? Math.min(mud, profilePressure(c.pp, t)) : mud; });
  const collapseExternal = (c, s, md) => mudHyd(c, md, s.mud_weight);
  const via = (src, s) => src === s ? '' : ` (via ${src.name})`;
  function capProfile(c, s, md, internal, notes) { const shoeT = c.traj.tvd(s.shoe_md), pf = profilePressure(c.fg, shoeT); let pShoe;
    if (s.shoe_md <= md[md.length - 1]) pShoe = interp(s.shoe_md, md, internal); else { const t = md.map(m => c.traj.tvd(m)), n = md.length; const grad = (internal[n - 1] - internal[n - 2]) / Math.max(t[n - 1] - t[n - 2], 1e-9); pShoe = internal[n - 1] + grad * (shoeT - t[n - 1]); }
    if (pShoe > pf) { internal = internal.map(x => x - (pShoe - pf)); notes.push(`limited by frac at shoe (${pf.toFixed(0)} psi)`); }
    if (s.max_surface_pressure != null && internal[0] > s.max_surface_pressure) { const d = internal[0] - s.max_surface_pressure; internal = internal.map(x => x - d); notes.push(`capped at ${s.max_surface_pressure.toFixed(0)} psi BOP rating`); }
    return internal.map(x => Math.max(x, 0)); }
  const mk = (name, kind, md, internal, external, axialState, description) => ({name, kind, md, internal, external, axial_state: axialState, description,
    burst_load: internal.map((x, i) => Math.max(x - external[i], 0)), collapse_load: internal.map((x, i) => Math.max(external[i] - x, 0))});
  function pressureTest(c, s, md) { if (s.pressure_test == null) return null; const int = mudHyd(c, md, s.mud_weight).map(x => x + s.pressure_test);
    return mk('Pressure test', 'burst', md, int, annulusAsCemented(c, s, md), 'as_cemented', `${s.pressure_test.toFixed(0)} psi on ${s.mud_weight} ppg mud, green cement backup`); }
  function gasKick(c, s, md, cid, src) { src = src || s; if (!['surface', 'intermediate', 'liner'].includes(src.type) || src.kick_volume_bbl == null) return null;
    if (src.next_hole_mud_weight == null || src.next_section_td_md == null) return null;
    const h0 = s.hanger_md || 0; cid = cid ?? s.od - 0.9; const cap = cid * cid / 1029.4; let hMd = Math.min(src.kick_volume_bbl / cap, s.shoe_md - h0);
    const hT = c.traj.tvd(h0 + hMd) - c.traj.tvd(h0), tdT = c.traj.tvd(src.next_section_td_md), gMud = ppg2grad(src.next_hole_mud_weight), pForm = (gMud + ppg2grad(src.kick_intensity_ppg ?? 0.5)) * tdT;
    const t0 = c.traj.tvd(h0), pSurf = pForm - gMud * (tdT - t0 - hT) - c.gas * hT;
    let int = md.map(m => { const d = c.traj.tvd(m) - t0; return pSurf + (d <= hT ? c.gas * d : c.gas * hT + gMud * (d - hT)); });
    const notes = [`${src.kick_volume_bbl} bbl gas at top of casing (ID ${cid.toFixed(2)} in, ${hMd.toFixed(0)} ft), ${src.kick_intensity_ppg ?? 0.5} ppg intensity, formation ${pForm.toFixed(0)} psi at ${src.next_section_td_md.toFixed(0)} ft MD`];
    int = capProfile(c, src, md, int, notes); return mk('Gas kick' + via(src, s), 'burst', md, int, burstBackup(c, s, md), 'as_cemented', notes.join('; ')); }
  function gasToSurface(c, s, md, src) { src = src || s; if (!['surface', 'intermediate', 'liner'].includes(src.type)) return null; if (isLiner(src) && src.next_section_td_md == null) return null;
    if (src.kick_volume_bbl != null && !src.include_gas_to_surface) return null; const shoeT = c.traj.tvd(src.shoe_md), pf = profilePressure(c.fg, shoeT);
    let int = md.map(m => pf - c.gas * (shoeT - c.traj.tvd(m))); const notes = [`frac at shoe ${pf.toFixed(0)} psi, gas gradient ${c.gas} psi/ft, pore/mud backup`];
    int = capProfile(c, src, md, int, notes); return mk('Gas to surface' + via(src, s), 'burst', md, int, burstBackup(c, s, md), 'as_cemented', notes.join('; ')); }
  function tubingLeak(c, s, md, src) { src = src || s; if (!['production', 'liner'].includes(src.type) || src.shut_in_tubing_pressure == null) return null;
    const pf = src.packer_fluid_ppg ?? src.mud_weight, packerMd = src.packer_md ?? src.shoe_md, pT = c.traj.tvd(packerMd);
    const int = md.map(m => { const t = c.traj.tvd(m); let v = src.shut_in_tubing_pressure + ppg2grad(pf) * Math.min(t, pT); if (t > pT) v += ppg2grad(pf) * (t - pT); return v; });
    return mk('Tubing leak' + via(src, s), 'burst', md, int, burstBackup(c, s, md), 'as_cemented', `SITP ${src.shut_in_tubing_pressure.toFixed(0)} psi on ${pf} ppg packer fluid`); }
  function stimulation(c, s, md, src) { src = src || s; if (src.frac_surface_pressure == null) return null; const ff = src.frac_fluid_ppg ?? 8.5;
    const int = mudHyd(c, md, ff).map(x => x + src.frac_surface_pressure);
    return mk('Stimulation' + via(src, s), 'burst', md, int, burstBackup(c, s, md), 'as_cemented', `${src.frac_surface_pressure.toFixed(0)} psi surface treating pressure on ${ff} ppg frac fluid`); }
  const fullEvac = (c, s, md) => mk('Full evacuation', 'collapse', md, md.map(() => 0), collapseExternal(c, s, md), 'as_cemented', `empty casing, ${s.mud_weight} ppg mud backup outside`);
  const cementing = (c, s, md) => mk('Cementing', 'collapse', md, mudHyd(c, md, s.mud_weight), annulusAsCemented(c, s, md), 'running', `lead ${s.cement_lead_ppg} / tail ${s.cement_tail_ppg} ppg outside, ${s.mud_weight} ppg displacement fluid inside`);
  function lostReturns(c, s, md) { if (s.next_hole_mud_weight == null || s.next_section_td_md == null) return null; const tdT = c.traj.tvd(s.next_section_td_md), probe = linspace(c.traj.tvd(s.shoe_md), tdT, 50);
    const pMin = Math.min(...probe.map(t => profilePressure(c.pp, t) / Math.max(t, 1))) * tdT, gn = ppg2grad(s.next_hole_mud_weight), level = Math.max(0, tdT - pMin / gn);
    const int = md.map(m => gn * Math.max(c.traj.tvd(m) - level, 0));
    return mk('Lost returns', 'collapse', md, int, collapseExternal(c, s, md), 'as_cemented', `${s.next_hole_mud_weight} ppg mud level drops to ${level.toFixed(0)} ft TVD`); }
  const runningCase = (c, s, md) => { const p = mudHyd(c, md, s.mud_weight); return mk('Running + overpull', 'axial', md, p, p, 'running', `${(s.overpull ?? 100000).toFixed(0)} lbf overpull in ${s.mud_weight} ppg mud`); };
  function standardLoadCases(well, s, step = 50, innerDiameter = null) { const c = ctx(well), md = depthGrid(s, step);
    const cases = [pressureTest, gasToSurface, tubingLeak, stimulation, fullEvac, cementing, lostReturns, runningCase].map(b => b(c, s, md)).filter(Boolean);
    const kick = gasKick(c, s, md, innerDiameter); if (kick) cases.splice(1, 0, kick);
    for (const liner of linersOf(well, s)) { for (const b of [gasToSurface, tubingLeak, stimulation]) { const lc = b(c, s, md, liner); if (lc) cases.push(lc); } const k = gasKick(c, s, md, innerDiameter, liner); if (k) cases.push(k); }
    return cases; }

  // ----------------------------------------------------------------- axial
  const weightPerFt = sp => sp.geometry.area * STEEL_DENSITY * 12;
  function hangingWeight(md, s, traj, weightAt) { const h = s.hanger_md || 0, grid = linspace(h, s.shoe_md, 801), inc = grid.map(x => traj.inclination(x) * Math.PI / 180), cum = [0];
    for (let i = 1; i < grid.length; i++) { const mid = 0.5 * (grid[i] + grid[i - 1]); cum.push(cum[i - 1] + (grid[i] - grid[i - 1]) * Math.cos(0.5 * (inc[i] + inc[i - 1])) * weightAt(mid)); }
    const total = cum[cum.length - 1]; return md.map(m => total - interp(m, grid, cum)); }
  function runningAxial(md, s, design, traj, overpull) { const pShoe = ppg2grad(s.mud_weight) * traj.tvd(s.shoe_md), fEnd = -pShoe * design.sections[design.sections.length - 1].spec.geometry.area;
    const op = overpull ?? s.overpull ?? 100000; return hangingWeight(md, s, traj, design.weightAt).map(x => x + fEnd + op); }
  function asCementedAxial(md, s, design, traj) { const shoeT = traj.tvd(s.shoe_md), tocT = traj.tvd(s.toc_md), tailTopT = traj.tvd(Math.max(s.toc_md, s.shoe_md - s.tail_length));
    const pShoe = ppg2grad(s.mud_weight) * tocT + ppg2grad(s.cement_lead_ppg) * (tailTopT - tocT) + ppg2grad(s.cement_tail_ppg) * (shoeT - tailTopT);
    const fEnd = -pShoe * design.sections[design.sections.length - 1].spec.geometry.area; return hangingWeight(md, s, traj, design.weightAt).map(x => x + fEnd); }

  // ----------------------------------------------------------------- designs
  function design(sections) { const secs = sections.map(x => ({top_md: x.top_md, bottom_md: x.bottom_md, spec: x.spec})); const bounds = secs.slice(0, -1).map(x => x.bottom_md);
    const idx = m => { let i = 0; while (i < bounds.length && bounds[i] < m) i++; return i; };  // searchsorted(side=left)
    const w = secs.map(x => weightPerFt(x.spec));
    return {sections: secs, uniform: secs.length === 1, top_md: secs[0].top_md, bottom_md: secs[secs.length - 1].bottom_md,
      label: secs.length === 1 ? secs[0].spec.label : secs.map(x => `${x.spec.label} (${x.top_md.toFixed(0)}-${x.bottom_md.toFixed(0)})`).join(' / '),
      specAt: m => secs[idx(m)].spec, weightAt: m => w[idx(m)]}; }
  const uniform = (s, sp) => design([{top_md: s.hanger_md || 0, bottom_md: s.shoe_md, spec: sp}]);

  // ----------------------------------------------------------------- evaluation
  function evaluateDesign(well, s, dsg, cases, step = 50) { const traj = trajectory(well.trajectory.stations);
    cases = cases || standardLoadCases(well, s, step, dsg.sections[0].spec.id); const req = well.design_factors; const checks = [];
    const safeDf = (r, l) => r.map((x, i) => l[i] > 0 ? x / l[i] : Infinity);
    for (const c of cases) { const md = c.md, specs = md.map(m => dsg.specAt(m)), axial = c.axial_state === 'running' ? runningAxial(md, s, dsg, traj) : asCementedAxial(md, s, dsg, traj);
      const area = specs.map(sp => sp.geometry.area), derate = md.map(m => derateFactor(well.yield_derating, temperature(well.formation, traj.tvd(m)))), yp = specs.map((sp, i) => sp.yield * derate[i]);
      const sa = axial.map((f, i) => f / area[i]), dls = md.map(m => traj.dls(m));
      const bR = specs.map((sp, i) => sp.burst * derate[i]); checks.push({case: c.name, check: 'burst', md, design_factor: safeDf(bR, c.burst_load), load: c.burst_load, rating: bR});
      const cR = specs.map((sp, i) => collapseWithAxial(sp.geometry, yp[i], sa[i]) * sp.connection.ce); checks.push({case: c.name, check: 'collapse', md, design_factor: safeDf(cR, c.collapse_load), load: c.collapse_load, rating: cR});
      const tL = axial.map((f, i) => Math.max(f, 0) + bendingStress(specs[i].geometry, dls[i]) * area[i]), tR = specs.map((sp, i) => sp.tension_rating * derate[i]); checks.push({case: c.name, check: 'tension', md, design_factor: safeDf(tR, tL), load: tL, rating: tR});
      const v = md.map((m, i) => maxVme(specs[i].geometry, c.internal[i], c.external[i], axial[i], dls[i])); checks.push({case: c.name, check: 'triaxial', md, design_factor: safeDf(yp, v), load: v, rating: yp});
      c.axial = axial; }
    const summary = {};
    for (const chk of ['burst', 'collapse', 'tension', 'triaxial']) { let best = null; for (const c of checks.filter(x => x.check === chk)) { let mi = 0; for (let i = 1; i < c.design_factor.length; i++) if (c.design_factor[i] < c.design_factor[mi]) mi = i; const v = c.design_factor[mi]; if (!best || v < best.min_df) best = {min_df: v, case: c.case, md: c.md[mi]}; }
      summary[chk] = {min_df: best.min_df, required: req[chk], case: best.case, md: best.md, pass: best.min_df >= req[chk]}; }
    const passMask = () => { const md = checks[0].md, ok = md.map(() => true); for (const c of checks) for (let i = 0; i < md.length; i++) if (!(c.design_factor[i] >= req[c.check] - 1e-9)) ok[i] = false; return ok; };
    return {string: s.name, design: dsg, spec: dsg.sections[0].spec, checks, cases, summary, passes: Object.values(summary).every(v => v.pass), passMask,
      temperature: {md: cases[0].md, temperature_f: cases[0].md.map(m => temperature(well.formation, traj.tvd(m))), yield_factor: cases[0].md.map(m => derateFactor(well.yield_derating, temperature(well.formation, traj.tvd(m))))}};
  }
  const evaluateString = (well, s, sp, step) => evaluateDesign(well, s, uniform(s, sp), null, step);

  // ----------------------------------------------------------------- optimizer
  const PRICE_INDEX = {'H-40': 0.95, 'J-55': 1.0, 'K-55': 1.0, 'M-65': 1.05, 'N-80': 1.1, 'L-80': 1.15, 'C-90': 1.35, 'R-95': 1.25, 'T-95': 1.4, 'C-110': 1.6, 'P-110': 1.35, 'Q-125': 1.6};
  const costPerFt = (sp, prices) => sp.weight * ((prices || PRICE_INDEX)[sp.grade.name] ?? 1.5);
  const designCost = (d, prices) => d.sections.reduce((a, x) => a + costPerFt(x.spec, prices) * (x.bottom_md - x.top_md), 0);
  function optimizeString(well, s, opts = {}) { const out = []; for (const sp of candidates(s.od, opts.grades, opts.connection || 'BTC', well.formation.sour)) { const r = evaluateString(well, s, sp); if (r.passes) out.push({result: r, design: r.design, spec: sp, cost_per_ft: costPerFt(sp, opts.prices)}); }
    out.sort((a, b) => a.cost_per_ft - b.cost_per_ft || a.spec.weight - b.spec.weight); return out.slice(0, opts.max_results ?? 5); }
  function runs(idx) { const out = []; let start = 0; for (let i = 1; i <= idx.length; i++) if (i === idx.length || idx[i] !== idx[start]) { out.push([start, i, idx[start]]); start = i; } return out; }
  function mergePlan(i, rs, lengths, costs) { const v = rs[i][2], nb = [i - 1, i + 1].filter(j => j >= 0 && j < rs.length), stronger = nb.filter(j => rs[j][2] >= v);
    if (stronger.length) { const j = stronger.reduce((a, b) => costs[rs[a][2]] <= costs[rs[b][2]] ? a : b); return [(costs[rs[j][2]] - costs[v]) * lengths[i], i, rs[j][2]]; }
    const j = nb.reduce((a, b) => (costs[v] - costs[rs[a][2]]) * lengths[a] <= (costs[v] - costs[rs[b][2]]) * lengths[b] ? a : b); return [(costs[v] - costs[rs[j][2]]) * lengths[j], j, v]; }
  function enforceSections(choice, md, costs, minLen, maxSec) { choice = [...choice]; const step = md[1] - md[0];
    for (;;) { const rs = runs(choice); if (rs.length === 1) return choice; const lengths = rs.map(([a, b]) => md[b - 1] - md[a] + step); const short = lengths.map((L, i) => [L, i]).filter(([L]) => L < minLen); let i;
      if (short.length) i = short.reduce((a, b) => a[0] <= b[0] ? a : b)[1]; else if (rs.length > maxSec) { let best = Infinity; for (let k = 0; k < rs.length; k++) { const c = mergePlan(k, rs, lengths, costs)[0]; if (c < best) { best = c; i = k; } } } else return choice;
      const [, target, value] = mergePlan(i, rs, lengths, costs); const [a, b] = rs[target]; for (let k = a; k < b; k++) choice[k] = value; } }
  function designFromChoice(md, choice, specs, top, bottom) { const rs = runs(choice); return design(rs.map(([a, b, v], k) => ({top_md: k === 0 ? top : 0.5 * (md[a - 1] + md[a]), bottom_md: k === rs.length - 1 ? bottom : 0.5 * (md[b - 1] + md[b]), spec: specs[v]}))); }
  function optimizeTapered(well, s, opts = {}) { const minLen = opts.min_section_length ?? 500, maxSec = opts.max_sections ?? 3, step = 50;
    const cands = candidates(s.od, opts.grades, opts.connection || 'BTC', well.formation.sour); const costsAll = cands.map(c => costPerFt(c, opts.prices));
    const order = cands.map((_, i) => i).sort((a, b) => costsAll[a] - costsAll[b] || cands[a].weight - cands[b].weight); const specs = order.map(i => cands[i]), costs = order.map(i => costsAll[i]);
    const masks = specs.map(sp => evaluateDesign(well, s, uniform(s, sp), standardLoadCases(well, s, step, sp.id)).passMask()); const md = depthGrid(s, step);
    if (!md.every((_, i) => masks.some(m => m[i]))) return null; let choice = md.map((_, i) => masks.findIndex(m => m[i]));
    for (let it = 0; it < 10; it++) { choice = enforceSections(choice, md, costs, minLen, maxSec); const d = designFromChoice(md, choice, specs, s.hanger_md || 0, s.shoe_md);
      const r = evaluateDesign(well, s, d, standardLoadCases(well, s, step, d.sections[0].spec.id)); const ok = r.passMask(); if (ok.every(Boolean)) return {result: r, design: d, spec: d.sections[0].spec, cost_per_ft: designCost(d, opts.prices) / (s.shoe_md - (s.hanger_md || 0))};
      for (let i = 0; i < ok.length; i++) if (!ok[i]) { let nxt = -1; for (let k = choice[i] + 1; k < masks.length; k++) if (masks[k][i]) { nxt = k; break; } if (nxt < 0) return null; choice[i] = nxt; } }
    return null; }

  // ----------------------------------------------------------------- examples
  const baseString = o => ({hanger_md: 0, cement_lead_ppg: 12.5, cement_tail_ppg: 15.8, tail_length: 500, next_hole_mud_weight: null, next_section_td_md: null, overpull: 100000, pressure_test: null,
    kick_volume_bbl: null, kick_intensity_ppg: 0.5, max_surface_pressure: null, include_gas_to_surface: false, packer_md: null, packer_fluid_ppg: null, shut_in_tubing_pressure: null, frac_surface_pressure: null, frac_fluid_ppg: null, ...o});
  const exampleBase = () => ({trajectory: {stations: [{md: 0, inclination: 0, azimuth: 0}, {md: 8000, inclination: 0, azimuth: 0}, {md: 9500, inclination: 90, azimuth: 90}, {md: 18000, inclination: 90, azimuth: 90}]},
    formation: {pore_pressure: {points: [{tvd: 0, value: 8.6}, {tvd: 6000, value: 9.0}, {tvd: 9000, value: 11.0}]}, fracture_gradient: {points: [{tvd: 0, value: 12.0}, {tvd: 2000, value: 13.5}, {tvd: 9000, value: 16.5}]}, surface_temperature_f: 70, geothermal_gradient_f_per_100ft: 1.2, sour: false},
    design_factors: {burst: 1.1, collapse: 1.0, tension: 1.6, triaxial: 1.25}, yield_derating: {enabled: true, slope_per_f: 0.0003, reference_f: 70, floor: 0.8}, prefs: {grades: ['J-55', 'K-55', 'N-80', 'L-80', 'P-110'], price_per_lb: null, currency: '$'}, gas_gradient_psi_ft: 0.1});
  function exampleHorizontal() { return {...exampleBase(), name: 'Example Onshore Horizontal Well', strings: [
    baseString({name: 'Surface', type: 'surface', od: 13.375, hole_size: 17.5, shoe_md: 2000, toc_md: 0, mud_weight: 9.0, cement_tail_ppg: 15.6, next_hole_mud_weight: 11.0, next_section_td_md: 8500, pressure_test: 1500}),
    baseString({name: 'Intermediate', type: 'intermediate', od: 9.625, hole_size: 12.25, shoe_md: 8500, toc_md: 1500, mud_weight: 11.0, tail_length: 1000, next_hole_mud_weight: 12.0, next_section_td_md: 18000, pressure_test: 3500, overpull: 150000}),
    baseString({name: 'Production', type: 'production', od: 5.5, hole_size: 8.5, shoe_md: 18000, toc_md: 7000, mud_weight: 12.0, cement_lead_ppg: 13.5, tail_length: 9500, pressure_test: 8000, overpull: 150000, packer_md: 8000, packer_fluid_ppg: 9.0, shut_in_tubing_pressure: 4500, frac_surface_pressure: 9500, frac_fluid_ppg: 8.6})]}; }
  function exampleLiner() { const w = exampleHorizontal(); w.name = 'Example Onshore Well with Frac Liner'; w.strings = [w.strings[0], w.strings[1],
    baseString({name: 'Production', type: 'production', od: 7.0, hole_size: 8.5, shoe_md: 11500, toc_md: 7000, mud_weight: 12.0, cement_lead_ppg: 13.5, tail_length: 3000, pressure_test: 6000, overpull: 150000, packer_md: 8000, packer_fluid_ppg: 9.0, shut_in_tubing_pressure: 4500}),
    baseString({name: 'Liner', type: 'liner', od: 4.5, hole_size: 6.125, hanger_md: 10500, shoe_md: 18000, toc_md: 10500, mud_weight: 12.0, cement_lead_ppg: 15.8, tail_length: 7500, pressure_test: 8000, overpull: 60000, frac_surface_pressure: 9500, frac_fluid_ppg: 8.6})]; return w; }

  return {geom, burstRating, collapseRating, collapseWithAxial, spec, candidates, pipes, pipesForOd, grades, connections, trajectory, profileAt, standardLoadCases, evaluateDesign, evaluateString,
    design, uniform, optimizeString, optimizeTapered, costPerFt, designCost, wellErrors, wellWarnings, exampleHorizontal, exampleLiner, baseString, interp, PRICE_INDEX};
})();
if (typeof module !== 'undefined') module.exports = Engine;
