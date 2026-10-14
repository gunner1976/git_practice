// Plain-language checks on the well object. Returns [{path, level: 'error'|'warn', msg}].
function validateWell(w) {
  const out = [], err = (path, msg) => out.push({path, level: 'error', msg}), warn = (path, msg) => out.push({path, level: 'warn', msg});
  const st = w.trajectory.stations;
  if (st.length < 2) err('trajectory', 'Add at least a surface station (MD 0) and TD.');
  for (let i = 1; i < st.length; i++) if (st[i].md <= st[i - 1].md) err('trajectory', `Survey MD must increase: row ${i + 1} (${st[i].md}) is not below row ${i} (${st[i - 1].md}).`);
  const td = Math.max(...st.map(s => s.md), 0);
  for (const [name, pts] of [['pore pressure', w.formation.pore_pressure.points], ['fracture gradient', w.formation.fracture_gradient.points]]) {
    if (!pts.length) err(name, `Add at least one ${name} point.`);
    for (let i = 1; i < pts.length; i++) if (pts[i].tvd < pts[i - 1].tvd) err(name, `${name} points must be sorted by TVD (row ${i + 1}).`);
  }
  const pp = w.formation.pore_pressure.points, fg = w.formation.fracture_gradient.points;
  const at = (pts, t) => { if (!pts.length) return 0; if (t <= pts[0].tvd) return pts[0].value; for (let i = 1; i < pts.length; i++) if (t <= pts[i].tvd) { const f = (t - pts[i - 1].tvd) / (pts[i].tvd - pts[i - 1].tvd || 1); return pts[i - 1].value + f * (pts[i].value - pts[i - 1].value); } return pts.at(-1).value; };
  for (const p of fg) if (at(pp, p.tvd) >= p.value) warn('fracture gradient', `At ${p.tvd} ft TVD the fracture gradient (${p.value} ppg) is not above pore pressure (${at(pp, p.tvd).toFixed(1)} ppg) — no drilling window.`);
  const strings = w.strings || [];
  if (!strings.length) err('strings', 'Add at least one casing string.');
  const tvd = Schematic.tvdFn(st);
  strings.forEach((s, i) => {
    const n = s.name || `string ${i + 1}`;
    if (!(s.od > 0)) err(`strings.${i}.od`, `${n}: OD is required.`);
    if (s.hole_size && s.hole_size <= s.od) err(`strings.${i}.hole_size`, `${n}: hole size (${s.hole_size}") must be larger than the casing OD (${s.od}").`);
    if (!(s.shoe_md > (s.hanger_md || 0))) err(`strings.${i}.shoe_md`, `${n}: shoe MD must be below the top of the string.`);
    if (s.toc_md > s.shoe_md) err(`strings.${i}.toc_md`, `${n}: top of cement (${s.toc_md}) cannot be below the shoe (${s.shoe_md}).`);
    if (s.type === 'liner' && !(s.hanger_md > 0)) err(`strings.${i}.hanger_md`, `${n}: a liner hangs below surface — enter the liner top MD.`);
    if (s.type !== 'liner' && s.hanger_md > 0) err(`strings.${i}.hanger_md`, `${n}: only liners have a top MD; set it to 0 or change the type to liner.`);
    if (s.shoe_md > td) warn(`strings.${i}.shoe_md`, `${n}: shoe (${s.shoe_md} ft) is below the last survey station (${td} ft); the hole is assumed to continue at the last inclination.`);
    if (!(s.mud_weight > 0)) err(`strings.${i}.mud_weight`, `${n}: mud weight is required.`);
    else { const pore = at(pp, tvd(s.shoe_md)), frac = at(fg, tvd(s.shoe_md));
      if (s.mud_weight < pore) warn(`strings.${i}.mud_weight`, `${n}: mud weight ${s.mud_weight} ppg is below pore pressure at the shoe (${pore.toFixed(1)} ppg).`);
      if (frac && s.mud_weight > frac) warn(`strings.${i}.mud_weight`, `${n}: mud weight ${s.mud_weight} ppg exceeds the fracture gradient at the shoe (${frac.toFixed(1)} ppg).`); }
    if (i > 0 && s.type !== 'liner' && strings[i - 1].type !== 'liner' && s.od >= strings[i - 1].od) err(`strings.${i}.od`, `${n}: OD (${s.od}") must be smaller than the string above (${strings[i - 1].od}").`);
    if (i > 0 && s.shoe_md <= strings[i - 1].shoe_md) warn(`strings.${i}.shoe_md`, `${n}: shoe is not below the previous string's shoe — check the order of strings.`);
    if (['surface', 'intermediate'].includes(s.type) && (!s.next_hole_mud_weight || !s.next_section_td_md)) warn(`strings.${i}.next_hole_mud_weight`, `${n}: without "Next MW" and "Next TD" the lost-returns and kick cases are skipped for this string.`);
    if (s.type === 'production' && !s.frac_surface_pressure && !s.shut_in_tubing_pressure) warn(`strings.${i}.frac_surface_pressure`, `${n}: no stimulation or tubing-leak pressure — the production burst cases are skipped.`);
    if (s.type === 'liner') { const parent = strings.filter(p => p !== s && p.od > s.od && (p.hanger_md || 0) <= s.hanger_md && s.hanger_md < p.shoe_md); if (!parent.length) err(`strings.${i}.hanger_md`, `${n}: no larger string covers the liner top at ${s.hanger_md} ft.`); }
  });
  return out;
}
