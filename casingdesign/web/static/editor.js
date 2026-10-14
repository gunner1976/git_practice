// Well-plan form editor. Edits the well object in place; `section` selects which part
// of the form to show ('well' | 'pressures' | 'strings' | null for everything).
const Editor = (() => {
  let well = null, root = null, section = null, onChangeCb = () => {}, onBind = () => {};
  let rerender = null;
  const onChange = () => { onBind(well); onChangeCb(); clearTimeout(rerender); rerender = setTimeout(render, 200); };
  const num = v => (v === '' || v == null) ? null : +v;

  // [key, label, kind, hint]
  const STRING_FIELDS = [
    ['name', 'Name', 'text', 'Shown on results and the report.'],
    ['type', 'Type', ['surface', 'intermediate', 'production', 'liner', 'conductor'], 'Decides which load cases apply: surface/intermediate get well-control cases, production gets tubing-leak/stimulation, liners hang inside the string above.'],
    ['od', 'Casing OD (in)', 'num', 'Nominal outside diameter, e.g. 9.625 for 9-5/8".'],
    ['hole_size', 'Hole size (in)', 'num', 'Bit size the string is run in.'],
    ['hanger_md', 'Liner top MD (ft)', 'num', 'Liners only: measured depth of the liner hanger. 0 for strings to surface.'],
    ['shoe_md', 'Shoe MD (ft)', 'num', 'Measured depth of the casing shoe.'],
    ['toc_md', 'Top of cement MD (ft)', 'num', 'Above TOC the annulus holds mud; below it, cement (pore pressure is used as backup once set).'],
    ['mud_weight', 'Mud weight (ppg)', 'num', 'Mud the string is run and cemented in. Used for running loads, collapse backup and the pressure test.'],
    ['cement_lead_ppg', 'Lead slurry (ppg)', 'num', 'Lighter slurry above the tail.'],
    ['cement_tail_ppg', 'Tail slurry (ppg)', 'num', 'Heavier slurry across the shoe.'],
    ['tail_length', 'Tail length (ft)', 'num', 'Length of tail slurry above the shoe.'],
    ['overpull', 'Overpull (lbf)', 'num', 'Extra pull allowed at surface while running (stuck-pipe margin).'],
    ['pressure_test', 'Pressure test (psi)', 'num', 'Surface test pressure after cementing. Leave blank to skip the test case.'],
  ];
  const DRILL_AHEAD = [
    ['next_hole_mud_weight', 'Next section mud weight (ppg)', 'num', 'Heaviest mud used while drilling below this shoe.'],
    ['next_section_td_md', 'Next section TD MD (ft)', 'num', 'Depth drilled below this shoe before the next string is run.'],
    ['kick_volume_bbl', 'Kick volume (bbl)', 'num', 'Design influx volume for kick tolerance. Leave blank for the conservative gas-to-surface case.'],
    ['kick_intensity_ppg', 'Kick intensity (ppg)', 'num', 'Formation pressure in excess of the mud weight when the kick is taken.'],
    ['max_surface_pressure', 'BOP rating (psi)', 'num', 'Caps the surface pressure in well-control cases. Blank for no cap.'],
    ['include_gas_to_surface', 'Also run gas-to-surface', 'bool', 'Keep the full gas column case even when a kick volume is given.'],
  ];
  const PRODUCTION = [
    ['packer_md', 'Packer MD (ft)', 'num', 'Production packer depth; packer fluid sits above it.'],
    ['packer_fluid_ppg', 'Packer fluid (ppg)', 'num', 'Fluid left in the casing/tubing annulus.'],
    ['shut_in_tubing_pressure', 'Shut-in tubing pressure (psi)', 'num', 'Applied on top of the packer fluid for the tubing-leak case. Blank to skip.'],
    ['frac_surface_pressure', 'Max treating pressure (psi)', 'num', 'Surface pressure during fracturing down the casing. Blank to skip the stimulation case.'],
    ['frac_fluid_ppg', 'Frac fluid (ppg)', 'num', 'Density of the fluid pumped during stimulation.'],
  ];
  const STD = [[20, 26], [16, 20], [13.375, 17.5], [10.75, 14.75], [9.625, 12.25], [7.625, 9.875], [7, 8.75], [5.5, 7.875], [4.5, 6.125]];

  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') el.className = v; else if (k.startsWith('on')) el[k] = v; else if (v != null && v !== false) el.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat()) if (k != null) el.append(k instanceof Node ? k : document.createTextNode(String(k)));
    return el;
  };

  let pathCounter = 0;
  function input(obj, key, kind, path) {
    path = path || `auto.${pathCounter++}`;
    if (Array.isArray(kind)) {
      return h('select', {'data-path': path, onchange: e => { obj[key] = e.target.value; onChange(); }},
        ...kind.map(o => h('option', {value: o, selected: obj[key] === o}, o)));
    }
    if (kind === 'bool') {
      return h('input', {'data-path': path, type: 'checkbox', checked: !!obj[key], onchange: e => { obj[key] = e.target.checked; onChange(); }});
    }
    return h('input', {'data-path': path, type: kind === 'num' ? 'number' : 'text', step: 'any', value: obj[key] == null ? '' : obj[key],
      onchange: e => { obj[key] = kind === 'num' ? num(e.target.value) : e.target.value; onChange(); }});
  }
  let issues = [];
  const issueFor = path => issues.filter(i => i.path === path);
  const fieldGrid = (obj, fields, pathPrefix = '') => h('div', {class: 'grid'}, ...fields.map(([k, label, kind, hint]) => {
    const probs = issueFor(pathPrefix + k);
    return h('label', {class: 'f' + (probs.some(p => p.level === 'error') ? ' bad' : probs.length ? ' warnish' : ''), title: hint || ''},
      h('span', {}, label), input(obj, k, kind, pathPrefix + k), ...probs.map(p => h('small', {class: p.level === 'error' ? 'fail' : 'warn'}, p.msg)));
  }));

  function table(rows, cols, factory, title) {
    const wrap = h('div', {class: 'tbl'});
    const redraw = () => wrap.replaceChildren(
      h('div', {class: 'row'}, h('h3', {}, title), h('button', {onclick: () => { rows.push(factory(rows)); onChange(); redraw(); }}, '+ row')),
      h('table', {class: 'edit'}, h('thead', {}, h('tr', {}, ...cols.map(c => h('th', {}, c[1])), h('th'))),
        h('tbody', {}, ...rows.map((r, i) => h('tr', {}, ...cols.map(([k]) => h('td', {}, input(r, k, 'num', `${title}.${i}.${k}`))),
          h('td', {}, h('button', {class: 'x', title: 'remove', onclick: () => { rows.splice(i, 1); onChange(); redraw(); }}, '×')))))));
    redraw();
    return wrap;
  }

  function stringCard(s, i) {
    const pre = `strings.${i}.`, n = issues.filter(x => x.path.startsWith(pre)), nErr = n.filter(x => x.level === 'error').length;
    const drillsAhead = ['surface', 'intermediate', 'conductor'].includes(s.type) || (s.type === 'liner' && s.next_section_td_md);
    const produces = ['production', 'liner'].includes(s.type);
    const main = STRING_FIELDS.filter(([k]) => k !== 'hanger_md' || s.type === 'liner');
    return h('details', {open: true, class: 'string'},
      h('summary', {}, h('span', {}, h('b', {}, `${s.name || 'string'} · ${s.od}" · ${s.type}`),
          nErr ? h('span', {class: 'badge fail', style: 'margin-left:8px'}, `${nErr} to fix`) : n.length ? h('span', {class: 'badge info', style: 'margin-left:8px'}, `${n.length} note${n.length > 1 ? 's' : ''}`) : null),
        h('span', {}, i > 0 ? h('button', {class: 'link small', title: 'move up', onclick: e => { e.preventDefault(); [well.strings[i - 1], well.strings[i]] = [well.strings[i], well.strings[i - 1]]; onChange(); render(); }}, '↑') : null,
          h('button', {class: 'x', title: 'remove string', onclick: e => { e.preventDefault(); if (confirm(`Remove ${s.name}?`)) { well.strings.splice(i, 1); onChange(); render(); } }}, '×'))),
      fieldGrid(s, main, pre),
      h('details', {open: drillsAhead || !!s.kick_volume_bbl, class: 'sub'}, h('summary', {}, h('span', {}, 'Drilling ahead below this string (well-control cases)'), h('span', {class: 'muted small'}, drillsAhead ? 'applies' : 'usually not for this type')), fieldGrid(s, DRILL_AHEAD, pre)),
      h('details', {open: produces, class: 'sub'}, h('summary', {}, h('span', {}, 'Production and stimulation cases'), h('span', {class: 'muted small'}, produces ? 'applies' : 'usually not for this type')), fieldGrid(s, PRODUCTION, pre)));
  }

  function newString() {
    const last = well.strings.at(-1), tvd = Schematic.tvdFn(well.trajectory.stations);
    const td = well.trajectory.stations.at(-1)?.md || 10000;
    let od = 13.375, hole = 17.5, type = 'surface';
    if (last) { const idx = STD.findIndex(([o]) => o <= last.od); const nxt = STD[Math.min(idx + 1, STD.length - 1)]; od = nxt[0]; hole = nxt[1]; type = 'production'; }
    if (last && last.type === 'production') type = 'liner';
    const shoe = last ? Math.min(td, last.shoe_md + Math.max(2000, (td - last.shoe_md))) : Math.min(2000, td);
    const pts = well.formation.pore_pressure.points, t = tvd(shoe);
    let pore = pts.length ? pts.reduce((v, p) => p.tvd <= t ? p.value : v, pts[0].value) : 9;
    const mw = Math.round((pore + 0.5) * 10) / 10;
    if (last && ['surface', 'intermediate'].includes(last.type)) { last.next_hole_mud_weight = last.next_hole_mud_weight ?? mw; last.next_section_td_md = last.next_section_td_md ?? shoe; }
    return {name: `${od}" ${type}`, type, od, hole_size: hole, hanger_md: type === 'liner' ? Math.max(0, last.shoe_md - 500) : 0,
      shoe_md: shoe, toc_md: type === 'liner' ? Math.max(0, last.shoe_md - 500) : (last ? Math.max(0, last.shoe_md - 500) : 0), mud_weight: mw,
      cement_lead_ppg: 12.5, cement_tail_ppg: 15.8, tail_length: 500, overpull: 100000, pressure_test: null,
      next_hole_mud_weight: null, next_section_td_md: null, kick_volume_bbl: null, kick_intensity_ppg: 0.5,
      max_surface_pressure: null, include_gas_to_surface: false, packer_md: null, packer_fluid_ppg: null,
      shut_in_tubing_pressure: null, frac_surface_pressure: null, frac_fluid_ppg: null};
  }

  const panel = (title, ...kids) => h('div', {class: 'panel'}, h('h2', {}, title), ...kids);
  const stationFactory = rows => ({md: (rows.at(-1)?.md ?? 0) + 1000, inclination: rows.at(-1)?.inclination ?? 0, azimuth: rows.at(-1)?.azimuth ?? 0});
  const ppFactory = (dflt) => rows => ({tvd: (rows.at(-1)?.tvd ?? 0) + 1000, value: rows.at(-1)?.value ?? dflt});

  const GRADES = ['H-40', 'J-55', 'K-55', 'M-65', 'N-80', 'L-80', 'C-90', 'R-95', 'T-95', 'C-110', 'P-110', 'Q-125'];
  const DEFAULT_GRADES = ['J-55', 'K-55', 'N-80', 'L-80', 'P-110'];
  function gradePicker() {
    well.prefs = well.prefs || {}; well.prefs.grades = well.prefs.grades || [...DEFAULT_GRADES];
    return h('div', {}, h('h3', {}, 'Grades to consider'), h('p', {class: 'muted small'}, 'The optimizer only picks from these. Sour wells automatically exclude non-sour grades.'),
      h('div', {class: 'row'}, ...GRADES.map(g => h('label', {class: 'chip'}, h('input', {type: 'checkbox', checked: well.prefs.grades.includes(g), onchange: e => { const set = new Set(well.prefs.grades); e.target.checked ? set.add(g) : set.delete(g); well.prefs.grades = GRADES.filter(x => set.has(x)); onChange(); }}), g))));
  }
  function render() {
    if (!root || !well) return;
    pathCounter = 0;
    const active = document.activeElement, focusPath = (active && root.contains(active)) ? active.dataset.path : null;
    const scrollY = window.scrollY;
    issues = typeof validateWell === 'function' ? validateWell(well) : [];
    const w = well, parts = [];
    if (!section || section === 'well') parts.push(
      panel('Well', h('div', {class: 'grid'},
        ...['burst', 'collapse', 'tension', 'triaxial'].map(k => h('label', {class: 'f'}, h('span', {}, `Design factor: ${k}`), input(w.design_factors, k, 'num'))),
        h('label', {class: 'f'}, h('span', {}, 'Gas gradient (psi/ft)'), input(w, 'gas_gradient_psi_ft', 'num')),
        h('label', {class: 'f'}, h('span', {}, 'Sour service'), input(w.formation, 'sour', 'bool')),
        h('label', {class: 'f'}, h('span', {}, 'Surface temperature (°F)'), input(w.formation, 'surface_temperature_f', 'num')),
        h('label', {class: 'f'}, h('span', {}, 'Geothermal gradient (°F/100 ft)'), input(w.formation, 'geothermal_gradient_f_per_100ft', 'num')),
        h('label', {class: 'f'}, h('span', {}, 'Derate yield for temperature'), input(w.yield_derating, 'enabled', 'bool')),
        h('label', {class: 'f'}, h('span', {}, 'Derating slope (per °F)'), input(w.yield_derating, 'slope_per_f', 'num'))),
        h('p', {class: 'muted small'}, 'Design factors are minimum rating ÷ load. The defaults are common onshore values; set them to your company standard.'),
        gradePicker()),
      panel('Trajectory', h('p', {class: 'muted small'}, 'Survey stations, minimum curvature between them. A vertical well needs only surface and TD.'),
        ...issueList('trajectory'),
        table(w.trajectory.stations, [['md', 'MD ft'], ['inclination', 'Inc °'], ['azimuth', 'Azi °']], stationFactory, 'Survey stations')));
    if (!section || section === 'pressures') parts.push(
      h('div', {class: 'two'},
        panel('Pore pressure and fracture gradient', h('p', {class: 'muted small'}, 'Equivalent mud weight versus TVD, interpolated linearly between points. The chart shows the drilling window with each string\'s mud weight.'),
          ...issueList('pore pressure'), ...issueList('fracture gradient'),
          table(w.formation.pore_pressure.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']], ppFactory(9), 'Pore pressure'),
          table(w.formation.fracture_gradient.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']], ppFactory(14), 'Fracture gradient')),
        panel('Pressure window', h('div', {id: 'pressure-window'}))));
    if (!section || section === 'strings') parts.push(
      h('div', {class: 'two wide-left'},
        panel('Casing program', h('p', {class: 'muted small'}, 'One card per string, shallowest first. Hover a label for what it means. Blank test, kick or production inputs skip those load cases.'),
          ...issueList('strings'),
          ...w.strings.map(stringCard),
          h('div', {class: 'row'}, h('button', {class: 'primary', onclick: () => { well.strings.push(newString()); onChange(); render(); }}, '+ Add next string'))),
        panel('Schematic', h('div', {id: 'schematic'}))));
    root.replaceChildren(...parts);
    const sc = root.querySelector('#schematic'); if (sc) Schematic.draw(sc, w);
    const pw = root.querySelector('#pressure-window'); if (pw) Schematic.pressureWindow(pw, w);
    if (focusPath) { const el = root.querySelector(`[data-path="${CSS.escape(focusPath)}"]`); if (el) { el.focus({preventScroll: true}); } }
    window.scrollTo(0, scrollY);
  }
  const issueList = path => issues.filter(i => i.path === path).map(i => h('div', {class: (i.level === 'error' ? 'fail' : 'warn') + ' small'}, (i.level === 'error' ? '✗ ' : '⚠ ') + i.msg));

  return {
    issues: () => issues,
    mount(el, cb) { root = el; onChangeCb = cb; },
    set(w, sec = null) { well = w; section = sec; render(); },
    get() { return structuredClone(well); },
    bind(cb) { onBind = cb; },
    render,
  };
})();
