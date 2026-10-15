// SRDE Planner integration: when opened from the Planner as /pages/casing-design/#...&pwell=SRDE-001 the tool loads the well
// from the hub (/api/plan/*), builds the design basis in engine units, and can publish the result back into the Planner's
// 'casing' module. Inert outside the hub (no pwell in the hash, or not served under /pages/).
(() => {
const M_TO_FT = 3.280839895, KPAM_TO_PPG = 0.145037738 * 0.3048 / 0.052;   // 1 kPa/m = 0.8502 ppg EMW
const OD_TALLY = {20: '20"', 16: '16"', 13.375: '13-3/8"', 11.75: '11-3/4"', 10.75: '10-3/4"', 9.625: '9-5/8"', 8.625: '8-5/8"', 7.625: '7-5/8"', 7: '7"', 6.625: '6-5/8"', 5.5: '5-1/2"', 5: '5"', 4.5: '4-1/2"'};
const HOLE_TALLY = {26: '26"', 17.5: '17-1/2"', 16: '16"', 14.75: '14-3/4"', 12.25: '12-1/4"', 10.625: '10-5/8"', 9.875: '9-7/8"', 8.75: '8-3/4"', 8.5: '8-1/2"', 7.875: '7-7/8"', 6.75: '6-3/4"', 6.125: '6-1/8"', 6: '6"', 4.75: '4-3/4"'};
const tallyToDec = s => { if (!s) return null; const m = String(s).match(/^(\d+)(?:-(\d+)\/(\d+))?/); return m ? +m[1] + (m[2] ? +m[2] / +m[3] : 0) : null; };
const nearestKey = (map, v) => { let best = null; for (const k of Object.keys(map)) if (best == null || Math.abs(+k - v) < Math.abs(+best - v)) best = k; return best != null && Math.abs(+best - v) < 0.02 ? map[best] : ''; };
const PWELL = decodeURIComponent((location.hash.match(/pwell=([^&]+)/) || [])[1] || '');
const ON_HUB = /\/pages\//.test(location.pathname);
if (!PWELL || !ON_HUB) return;

async function hub(path, body) { const r = await fetch('/api/plan/' + path, body ? {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)} : {cache: 'no-store'}); let j = {}; try { j = await r.json(); } catch {} if (!r.ok) throw new Error(j.error || ('hub error ' + r.status)); return j; }
const numv = (inputs, key) => { const r = (inputs || []).find(x => x.key === key); const v = r ? +r.value : NaN; return isFinite(v) && r.value !== '' ? v : null; };

async function loadWell(id) {
  const q = '?well=' + encodeURIComponent(id);
  const [program, survey, casing, tops] = await Promise.all([hub('program' + q), hub('module' + q + '&module=survey').catch(() => null), hub('module' + q + '&module=casing').catch(() => null), hub('prog_tops' + q).catch(() => null)]);
  let overlays = null; try { overlays = (await (await fetch('/pages/planner/data.json', {cache: 'no-store'})).json()).overlays; } catch {}
  const basis = [];   // what came from where, with tags, shown to the user and carried in the publish
  const inputs = program.inputs || [], g = program.geometry || {};
  // --- trajectory (m -> ft)
  let stations;
  const sv = survey && survey.doc && survey.doc.data && survey.doc.data.stations;
  if (sv && sv.length >= 2) { stations = sv.map(([md, inc, azi]) => ({md: md * M_TO_FT, inclination: inc, azimuth: azi})); basis.push({item: 'Trajectory', value: `${sv.length} survey stations (${survey.doc.data.survey_type || 'plan'})`, tag: 'S', source: 'Planner deviation-survey module'}); }
  else { const kop = numv(inputs, 'kop') ?? g.kop_md ?? null, land = g.land_md ?? g.landing_md ?? null, lat = numv(inputs, 'lat_len') ?? 0;
    if (land) { stations = [{md: 0, inclination: 0, azimuth: 0}, {md: (kop ?? land * 0.6) * M_TO_FT, inclination: 0, azimuth: 0}, {md: land * M_TO_FT, inclination: 90, azimuth: 0}, {md: (land + Math.max(lat, 100)) * M_TO_FT, inclination: 90, azimuth: 0}]; basis.push({item: 'Trajectory', value: `synthesised from design inputs: KOP ${Math.round(kop ?? land * 0.6)} m, landing ${Math.round(land)} m MD, lateral ${Math.round(lat)} m`, tag: 'S', source: 'Planner design inputs / well_calc.geometry (no survey module yet)'}); }
    else { stations = [{md: 0, inclination: 0, azimuth: 0}, {md: 1000 * M_TO_FT, inclination: 0, azimuth: 0}]; basis.push({item: 'Trajectory', value: 'no survey and no landing depth: vertical 1,000 m placeholder', tag: 'S', source: '-'}); } }
  // --- pressures and temperature
  const pore_kpam = overlays && overlays.pressure ? +overlays.pressure.pore_kpa_m : 7.9, pore_tag = overlays && overlays.pressure ? overlays.pressure.pore_tag : 'T record / E reading';
  const pore_ppg = +(pore_kpam * KPAM_TO_PPG).toFixed(2);
  basis.push({item: 'Pore pressure', value: `${pore_kpam} kPa/m = ${pore_ppg} ppg EMW, constant with depth`, tag: pore_tag, source: 'Planner overlay (regional RFT)'});
  const frac_ppg = 13.46;   // 0.70 psi/ft - an ASSUMPTION; no LOT/FIT exists in the concession (hazard H10)
  basis.push({item: 'Fracture gradient', value: `${frac_ppg} ppg EMW (0.70 psi/ft) ASSUMED - no LOT/FIT held (H10). Edit on the Pressures step; confirm before publishing.`, tag: 'S assumed', source: 'none held', warn: true});
  const ot = (overlays && overlays.temperature) || {}; const t0c = ot.intercept_c != null ? +ot.intercept_c : ot.surface_c != null ? +ot.surface_c : 18, tgc = ot.grad_c_per_m != null ? +ot.grad_c_per_m : ot.grad_c_m != null ? +ot.grad_c_m : 0.031;
  const tsurf_f = +(t0c * 1.8 + 32).toFixed(1), tgrad_f100 = +(tgc * 1.8 * 30.48).toFixed(2);
  basis.push({item: 'Temperature', value: `${t0c} °C + ${tgc} °C/m = ${tsurf_f} °F + ${tgrad_f100} °F/100 ft`, tag: ot.tag || 'S', source: 'Planner overlay (geotherm)'});
  // --- strings: the current casing document if any, else the Nexus default rows
  const doc = casing && casing.doc && casing.doc.data && casing.doc.data.strings && casing.doc.data.strings.length ? casing.doc.data : null;
  let rows = doc ? doc.strings : null;
  if (!rows) { try { rows = ((await (await fetch('/pages/planner/data.json', {cache: 'no-store'})).json()).design || {}).strings || null; } catch {} }
  const depthM = key => key ? numv(inputs, key) : null;
  const landM = g.land_md ?? g.landing_md ?? g.prod_shoe_md ?? null;
  const strings = []; let prevShoe = 0;
  const mw = Math.max(pore_ppg + 0.5, 8.6);
  for (const r of (rows || [])) {
    const kind = (r.kind || '').toLowerCase(); if (!['conductor', 'surface', 'intermediate', 'production', 'liner'].includes(kind)) continue;
    const od = tallyToDec(r.od), hole = tallyToDec(r.hole) || (od ? od + 2.5 : null); if (!od) continue;
    let shoe_m = depthM(r.depth_key); if (shoe_m == null && kind === 'production') shoe_m = landM; if (shoe_m == null && kind === 'surface') shoe_m = numv(inputs, 'surf_shoe'); if (shoe_m == null && kind === 'conductor') shoe_m = numv(inputs, 'cond_shoe');
    if (shoe_m == null) { shoe_m = prevShoe + 300; basis.push({item: `${r.label || kind} shoe`, value: `no depth input - placed ${Math.round(shoe_m)} m`, tag: 'S', source: '-', warn: true}); }
    const s = Engine.baseString({name: r.label || kind[0].toUpperCase() + kind.slice(1), type: kind, od, hole_size: hole, hanger_md: kind === 'liner' ? Math.max(0, prevShoe - 100) * M_TO_FT : 0, shoe_md: shoe_m * M_TO_FT, toc_md: kind === 'liner' ? Math.max(0, prevShoe - 100) * M_TO_FT : 0, mud_weight: +mw.toFixed(1), pressure_test: kind === 'conductor' ? null : 1500});
    s._planner = {depth_key: r.depth_key || '', od_tally: r.od, hole_tally: r.hole, grade: r.grade, weight: r.weight_ppf, conn: r.conn};
    strings.push(s); prevShoe = shoe_m;
  }
  for (let i = 0; i < strings.length - 1; i++) { const s = strings[i], nx = strings[i + 1]; if (['surface', 'intermediate', 'conductor'].includes(s.type) && nx.shoe_md > s.shoe_md) { s.next_hole_mud_weight = nx.mud_weight; s.next_section_td_md = nx.shoe_md; } }
  basis.push({item: 'Mud weights', value: `${mw.toFixed(1)} ppg on every string (max(pore + 0.5, 8.6)) - planning default`, tag: 'S', source: '-', warn: true});
  basis.push({item: 'Casing strings', value: doc ? `${strings.length} rows from the Planner casing module (${casing.doc.source === 'tool' ? 'published by ' + casing.doc.tool_id : 'entered in the Planner'})` : `${strings.length} rows from the Nexus default design`, tag: 'S', source: doc ? 'Planner casing module' : 'planner/data.json design.strings'});
  const base = Engine.exampleHorizontal();
  const well = {...base, name: `${id} casing design`, trajectory: {stations}, strings,
    formation: {...base.formation, pore_pressure: {points: [{tvd: 0, value: pore_ppg}]}, fracture_gradient: {points: [{tvd: 0, value: frac_ppg}]}, surface_temperature_f: tsurf_f, geothermal_gradient_f_per_100ft: tgrad_f100},
    planner: {well_id: id, slot: program.well, basis, frac_confirmed: false, loaded_at: new Date().toISOString()}};
  return well;
}

function toPlannerDoc(well, design) {
  const strings = [], an = [];
  for (const st of design.strings) { const r = st.result; const s = well.strings.find(x => x.name === st.string) || {}; const pl = s._planner || {};
    const secs = r ? r.design.sections : []; const label = st.string;
    const purpose = r ? Object.entries(r.summary).map(([k, v]) => `${k} DF ${isFinite(v.min_df) ? v.min_df.toFixed(2) : 'inf'} (${v.case})`).join('; ') : 'no catalog pipe passes';
    secs.forEach((x, i) => strings.push({kind: s.type || 'production', label: secs.length > 1 ? `${label} ${Math.round(x.top_md / M_TO_FT).toLocaleString()}-${Math.round(x.bottom_md / M_TO_FT).toLocaleString()} m` : label,
      od: nearestKey(OD_TALLY, x.spec.od) || pl.od_tally || '', hole: nearestKey(HOLE_TALLY, s.hole_size) || pl.hole_tally || '', weight_ppf: String(x.spec.weight), grade: x.spec.grade.name,
      conn: x.spec.connection.name === 'PREMIUM' ? 'premium' : x.spec.connection.name,
      cement: i === secs.length - 1 ? `TOC ${Math.round((s.toc_md || 0) / M_TO_FT).toLocaleString()} m; lead ${s.cement_lead_ppg} / tail ${s.cement_tail_ppg} ppg; shoe ${Math.round(s.shoe_md / M_TO_FT).toLocaleString()} m MD` : '',
      purpose: i === 0 ? purpose : '', depth_key: i === secs.length - 1 ? (pl.depth_key || (s.type === 'surface' ? 'surf_shoe' : s.type === 'conductor' ? 'cond_shoe' : '')) : ''}));
    if (!secs.length) strings.push({kind: s.type || 'production', label, od: pl.od_tally || nearestKey(OD_TALLY, s.od), hole: pl.hole_tally || '', weight_ppf: '', grade: '', conn: '', cement: '', purpose, depth_key: pl.depth_key || ''});
    an.push({name: st.string, od: s.od, pipe: r ? (r.design.uniform ? r.spec.label : 'tapered: ' + secs.map(x => x.spec.label).join(' / ')) : null, pass: !!(r && r.passes), overridden: !!st.overridden,
      sections: secs.map(x => ({top_m: Math.round(x.top_md / M_TO_FT), bottom_m: Math.round(x.bottom_md / M_TO_FT), pipe: x.spec.label, burst_psi: Math.round(x.spec.burst), collapse_psi: Math.round(x.spec.collapse), joint_lbf: Math.round(x.spec.joint_strength)})),
      summary: r ? Object.fromEntries(Object.entries(r.summary).map(([k, v]) => [k, {min_df: isFinite(v.min_df) ? +v.min_df.toFixed(3) : null, required: v.required, case: v.case, md_m: Math.round(v.md / M_TO_FT), pass: v.pass}])) : {},
      cases: r ? r.cases.map(c => ({name: c.name, basis: c.description})) : []}); }
  const f = well.formation, p = well.planner || {};
  return {strings, analysis: {tool: 'casing-design', tool_version: 'v1', run_at: new Date().toISOString().slice(0, 16).replace('T', ' '),
    frac_basis: p.frac_confirmed ? `E team-entered ${f.fracture_gradient.points.map(x => x.value).join('/')} ppg EMW` : `S assumed ${f.fracture_gradient.points.map(x => x.value).join('/')} ppg EMW (no LOT/FIT held, H10)`,
    basis: {pore_ppg: f.pore_pressure.points.map(x => [x.tvd / M_TO_FT, x.value]), frac_ppg: f.fracture_gradient.points.map(x => [x.tvd / M_TO_FT, x.value]), surface_temperature_c: +((f.surface_temperature_f - 32) / 1.8).toFixed(1), geothermal_c_per_m: +(f.geothermal_gradient_f_per_100ft / 1.8 / 30.48).toFixed(4),
      design_factors: well.design_factors, mud_weights_ppg: Object.fromEntries(well.strings.map(s => [s.name, s.mud_weight])), grades: well.prefs && well.prefs.grades, loaded: p.basis || []},
    strings: an, warnings: design.warnings || [], units_note: 'engine ran in US oilfield units (ft, psi, ppg); depths published in metres'}};
}

window.PlannerMode = {well_id: PWELL, loadWell, toPlannerDoc, hub, plannerUrl: `/pages/planner/#program/design&well=${encodeURIComponent(PWELL)}`};
})();
