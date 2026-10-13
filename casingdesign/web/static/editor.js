// Well-plan form editor. `well` (a plain object matching casingdesign.well.Well) is the
// single source of truth; the form and the JSON view are two renderings of it.
const Editor = (() => {
  let well = null, onChange = () => {};
  const num = v => (v === '' || v == null) ? null : +v;

  const STRING_FIELDS = [
    ['name', 'Name', 'text'], ['type', 'Type', ['surface', 'intermediate', 'production', 'liner', 'conductor']],
    ['od', 'OD (in)', 'num'], ['hole_size', 'Hole (in)', 'num'],
    ['hanger_md', 'Hanger MD', 'num'], ['shoe_md', 'Shoe MD', 'num'], ['toc_md', 'TOC MD', 'num'],
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
      if (k === 'class') el.className = v; else if (k.startsWith('on')) el[k] = v; else el.setAttribute(k, v);
    }
    for (const k of kids.flat()) el.append(k instanceof Node ? k : document.createTextNode(String(k)));
    return el;
  };

  function input(obj, key, kind) {
    if (Array.isArray(kind)) {
      const sel = h('select', {onchange: e => { obj[key] = e.target.value; onChange(); }},
        ...kind.map(o => h('option', {value: o, ...(obj[key] === o ? {selected: ''} : {})}, o)));
      return sel;
    }
    if (kind === 'bool') {
      return h('input', {type: 'checkbox', ...(obj[key] ? {checked: ''} : {}),
        onchange: e => { obj[key] = e.target.checked; onChange(); }});
    }
    return h('input', {type: kind === 'num' ? 'number' : 'text', step: 'any',
      value: obj[key] == null ? '' : obj[key],
      onchange: e => { obj[key] = kind === 'num' ? num(e.target.value) : e.target.value; onChange(); }});
  }

  function fieldGrid(obj, fields) {
    return h('div', {class: 'grid'}, ...fields.map(([k, label, kind]) =>
      h('label', {class: 'f'}, h('span', {}, label), input(obj, k, kind))));
  }

  function table(rows, cols, factory, title) {
    const render = () => {
      const t = h('table', {class: 'edit'},
        h('thead', {}, h('tr', {}, ...cols.map(c => h('th', {}, c[1])), h('th'))),
        h('tbody', {}, ...rows.map((r, i) => h('tr', {},
          ...cols.map(([k]) => h('td', {}, input(r, k, 'num'))),
          h('td', {}, h('button', {class: 'x', title: 'remove', onclick: () => { rows.splice(i, 1); onChange(); redraw(); }}, '×'))))));
      return t;
    };
    const wrap = h('div', {class: 'tbl'});
    const redraw = () => { wrap.replaceChildren(h('div', {class: 'row'}, h('h3', {}, title),
      h('button', {onclick: () => { rows.push(factory(rows)); onChange(); redraw(); }}, '+ row')), render()); };
    redraw();
    return wrap;
  }

  function stringCard(s, i) {
    const details = h('details', {open: ''},
      h('summary', {}, h('b', {}, `${s.name || 'string'} · ${s.od}"`),
        h('button', {class: 'x', onclick: e => { e.preventDefault(); well.strings.splice(i, 1); onChange(); render(); }}, '×')),
      fieldGrid(s, STRING_FIELDS),
      h('h4', {}, 'Drilling ahead (well control)'), fieldGrid(s, DRILL_AHEAD),
      h('h4', {}, 'Production'), fieldGrid(s, PRODUCTION));
    return details;
  }

  let root;
  function render() {
    if (!root || !well) return;
    const w = well;
    root.replaceChildren(
      h('div', {class: 'grid'},
        h('label', {class: 'f wide'}, h('span', {}, 'Well name'), input(w, 'name', 'text')),
        ...['burst', 'collapse', 'tension', 'triaxial'].map(k =>
          h('label', {class: 'f'}, h('span', {}, `DF ${k}`), input(w.design_factors, k, 'num'))),
        h('label', {class: 'f'}, h('span', {}, 'Gas grad (psi/ft)'), input(w, 'gas_gradient_psi_ft', 'num')),
        h('label', {class: 'f'}, h('span', {}, 'Sour'), input(w.formation, 'sour', 'bool'))),
      table(w.trajectory.stations, [['md', 'MD ft'], ['inclination', 'Inc °'], ['azimuth', 'Azi °']],
        rows => ({md: (rows.at(-1)?.md ?? 0) + 1000, inclination: rows.at(-1)?.inclination ?? 0, azimuth: rows.at(-1)?.azimuth ?? 0}),
        'Trajectory (survey stations)'),
      table(w.formation.pore_pressure.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']],
        rows => ({tvd: (rows.at(-1)?.tvd ?? 0) + 1000, value: rows.at(-1)?.value ?? 9}), 'Pore pressure'),
      table(w.formation.fracture_gradient.points, [['tvd', 'TVD ft'], ['value', 'EMW ppg']],
        rows => ({tvd: (rows.at(-1)?.tvd ?? 0) + 1000, value: rows.at(-1)?.value ?? 14}), 'Fracture gradient'),
      h('div', {class: 'row'}, h('h3', {}, 'Casing strings'),
        h('button', {onclick: () => { well.strings.push(newString()); onChange(); render(); }}, '+ string')),
      ...w.strings.map(stringCard));
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

  return {
    mount(el, cb) { root = el; onChange = cb; },
    set(w) { well = structuredClone(w); render(); },
    get() { return structuredClone(well); },
    render,
  };
})();
