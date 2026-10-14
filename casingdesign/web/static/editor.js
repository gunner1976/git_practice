// Well-plan form editor. Edits the well object in place; `section` selects which part
// of the form to show ('well' | 'pressures' | 'strings' | null for everything).
const Editor = (() => {
  let well = null, root = null, section = null, onChangeCb = () => {}, onBind = () => {};
  const onChange = () => { onBind(well); onChangeCb(); };
  const num = v => (v === '' || v == null) ? null : +v;

  const STRING_FIELDS = [
    ['name', 'Name', 'text'], ['type', 'Type', ['surface', 'intermediate', 'production', 'liner', 'conductor']],
    ['od', 'OD (in)', 'num'], ['hole_size', 'Hole (in)', 'num'],
    ['hanger_md', 'Top MD (liners)', 'num'], ['shoe_md', 'Shoe MD', 'num'], ['toc_md', 'TOC MD', 'num'],
    ['mud_weight', 'Mud (ppg)', 'num'], ['cement_lead_ppg', 'Lead (ppg)', 'num'],
    ['cement_tail_ppg', 'Tail (ppg)', 'num'], ['tail_length', 'Tail length (ft)', 'num'],
    ['overpull', 'Overpull (lbf)', 'num'], ['pressure_test', 'Test (psi)', 'num'],
  ];
  const DRILL_AHEAD = [
    ['next_hole_mud_weight', 'Next MW (ppg)', 'num'], ['next_section_td_md', 'Next TD MD', 'num'],
    ['kick_volume_bbl', 'Kick (bbl)', 'num'], ['kick_intensity_ppg', 'Kick intensity (ppg)', 'num'],
    ['max_surface_pressure', 'BOP (psi)', 'num'], ['include_gas_to_surface', 'Also gas-to-surface', 'bool'],
  ];
  const PRODUCTION = [
    ['packer_md', 'Packer MD', 'num'], ['packer_fluid_ppg', 'Packer fluid (ppg)', 'num'],
    ['shut_in_tubing_pressure', 'SITP (psi)', 'num'],
    ['frac_surface_pressure', 'Frac STP (psi)', 'num'], ['frac_fluid_ppg', 'Frac fluid (ppg)', 'num'],
  ];

  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') el.className = v; else if (k.startsWith('on')) el[k] = v; else if (v != null && v !== false) el.setAttribute(k, v === true ? '' : v);
    }
    for (const k of kids.flat()) if (k != null) el.append(k instanceof Node ? k : document.createTextNode(String(k)));
    return el;
  };

  function input(obj, key, kind) {
    if (Array.isArray(kind)) {
      return h('select', {onchange: e => { obj[key] = e.target.value; onChange(); }},
        ...kind.map(o => h('option', {value: o, selected: obj[key] === o}, o)));
    }
    if (kind === 'bool') {
      return h('input', {type: 'checkbox', checked: !!obj[key], onchange: e => { obj[key] = e.target.checked; onChange(); }});
    }
    return h('input', {type: kind === 'num' ? 'number' : 'text', step: 'any', value: obj[key] == null ? '' : obj[key],
      onchange: e => { obj[key] = kind === 'num' ? num(e.target.value) : e.target.value; onChange(); }});
  }
  const fieldGrid = (obj, fields) => h('div', {class: 'grid'}, ...fields.map(([k, label, kind]) =>
    h('label', {class: 'f'}, h('span', {}, label), input(obj, k, kind))));

  function table(rows, cols, factory, title) {
    const wrap = h('div', {class: 'tbl'});
    const redraw = () => wrap.replaceChildren(
      h('div', {class: 'row'}, h('h3', {}, title), h('button', {onclick: () => { rows.push(factory(rows)); onChange(); redraw(); }}, '+ row')),
      h('table', {class: 'edit'}, h('thead', {}, h('tr', {}, ...cols.map(c => h('th', {}, c[1])), h('th'))),
        h('tbody', {}, ...rows.map((r, i) => h('tr', {}, ...cols.map(([k]) => h('td', {}, input(r, k, 'num'))),
          h('td', {}, h('button', {class: 'x', title: 'remove', onclick: () => { rows.splice(i, 1); onChange(); redraw(); }}, '×')))))));
    redraw();
    return wrap;
  }

  function stringCard(s, i) {
    return h('details', {open: true, class: 'string'},
      h('summary', {}, h('b', {}, `${s.name || 'string'} · ${s.od}" · ${s.type}`),
        h('button', {class: 'x', title: 'remove string', onclick: e => { e.preventDefault(); well.strings.splice(i, 1); onChange(); render(); }}, '×')),
      fieldGrid(s, STRING_FIELDS),
      h('h4', {}, 'Drilling ahead below this string (well control)'), fieldGrid(s, DRILL_AHEAD),
      h('h4', {}, 'Production / stimulation'), fieldGrid(s, PRODUCTION));
  }

  function newString() {
    const last = well.strings.at(-1);
    return {name: 'New string', type: 'production', od: 5.5, hole_size: 8.5, hanger_md: 0,
      shoe_md: (last?.shoe_md ?? 5000) + 3000, toc_md: last?.shoe_md ?? 0, mud_weight: last?.next_hole_mud_weight ?? 10,
      cement_lead_ppg: 12.5, cement_tail_ppg: 15.8, tail_length: 500, overpull: 100000, pressure_test: null,
      next_hole_mud_weight: null, next_section_td_md: null, kick_volume_bbl: null, kick_intensity_ppg: 0.5,
      max_surface_pressure: null, include_gas_to_surface: false, packer_md: null, packer_fluid_ppg: null,
      shut_in_tubing_pressure: null, frac_surface_pressure: null, frac_fluid_ppg: null};
  }

  const panel = (title, ...kids) => h('div', {class: 'panel'}, h('h2', {}, title), ...kids);
  const stationFactory = rows => ({md: (rows.at(-1)?.md ?? 0) + 1000, inclination: rows.at(-1)?.inclination ?? 0, azimuth: rows.at(-1)?.azimuth ?? 0});
  const ppFactory = (dflt) => rows => ({tvd: (rows.at(-1)?.tvd ?? 0) + 1000, value: rows.at(-1)?.value ?? dflt});

  function render() {
    if (!root || !well) return;
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
        h('p', {class: 'muted small'}, 'Design factors are minimum rating ÷ load. The defaults are common onshore values; set them to your company standard.')),
      panel('Trajectory', h('p', {class: 'muted small'}, 'Survey stations, minimum curvature between them. A vertical well needs only surface and TD.'),
        table(w.trajectory.stations, [['md', 'MD ft'], ['inclination', 'Inc °'], ['azimuth', 'Azi °']], stationFactory, 'Survey stations')));
    if (!section || section === 'pressures') parts.push(
      panel('Pore pressure and fracture gradient', h('p', {class: 'muted small'}, 'Equivalent mud weight versus TVD, interpolated linearly between points.'),
        h('div', {class: 'grid', style: 'grid-template-columns:1fr 1fr'},
          table(w.formation.pore_pressure.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']], ppFactory(9), 'Pore pressure'),
          table(w.formation.fracture_gradient.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']], ppFactory(14), 'Fracture gradient'))));
    if (!section || section === 'strings') parts.push(
      panel('Casing program', h('p', {class: 'muted small'}, 'One card per string, shallowest first. Filling in test, kick or production inputs switches on the matching load cases; leave a field blank to skip that case.'),
        ...w.strings.map(stringCard),
        h('div', {class: 'row'}, h('button', {onclick: () => { well.strings.push(newString()); onChange(); render(); }}, '+ Add string'))));
    root.replaceChildren(...parts);
  }

  return {
    mount(el, cb) { root = el; onChangeCb = cb; },
    set(w, sec = null) { well = w; section = sec; render(); },
    get() { return structuredClone(well); },
    bind(cb) { onBind = cb; },
    render,
  };
})();
