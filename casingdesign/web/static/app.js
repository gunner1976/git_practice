// Casing Design app: projects -> guided steps -> one-click design.
const $ = s => document.querySelector(s);
const app = $('#app');
let catalog = null, project = null, designData = null, saveTimer = null, dirty = false;
const STEPS = [['well', 'Well & design basis'], ['pressures', 'Pressures'], ['strings', 'Casing program'], ['design', 'Design']];

async function api(path, method = 'GET', body) {
  const r = await fetch(path, {method, headers: body ? {'content-type': 'application/json'} : {}, body: body ? JSON.stringify(body) : undefined});
  if (!r.ok) { let t = await r.text(); try { t = JSON.parse(t).detail || t; } catch {} throw new Error(typeof t === 'string' ? t : JSON.stringify(t)); }
  return r.json();
}
const fmt = (x, d = 2) => x == null ? '∞' : (+x).toLocaleString(undefined, {maximumFractionDigits: d, minimumFractionDigits: d});
const fmt0 = x => x == null ? '—' : Math.round(x).toLocaleString();
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 1800); }
const h = (tag, attrs = {}, ...kids) => { const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) { if (k === 'class') el.className = v; else if (k.startsWith('on')) el[k] = v; else if (v !== false && v != null) el.setAttribute(k, v === true ? '' : v); }
  for (const k of kids.flat()) if (k != null) el.append(k instanceof Node ? k : document.createTextNode(String(k))); return el; };

// ---------------------------------------------------------------- routing
function route() {
  const hash = location.hash || '#/';
  const m = hash.match(/^#\/p\/([^/]+)(?:\/(\w+))?/);
  if (m) openProject(m[1], m[2] || 'well'); else renderHome();
}
window.addEventListener('hashchange', route);

// ---------------------------------------------------------------- home
async function renderHome() {
  project = null; designData = null; $('#save-state').textContent = '';
  const list = await api('/api/projects');
  app.replaceChildren(
    h('div', {class: 'panel hero'}, h('h2', {style: 'font-size:20px'}, 'Design casing strings for an onshore well'),
      h('p', {}, 'Enter the well, pressures and casing program; the optimizer picks the cheapest API 5CT pipe that passes every load case and shows you why.'),
      h('div', {class: 'row', style: 'justify-content:center'},
        h('button', {class: 'primary big', onclick: () => newProject('horizontal')}, '+ New well from example'),
        h('button', {class: 'big', onclick: () => newProject('liner')}, '+ Example with frac liner'),
        h('label', {class: 'big', style: 'padding:12px 16px;border:1px solid var(--line);border-radius:7px;cursor:pointer'}, 'Import Landmark EDM…',
          h('input', {type: 'file', accept: '.xml', hidden: true, onchange: e => importEdm(e.target.files[0])})))),
    h('div', {class: 'panel'}, h('h2', {}, 'Your wells'),
      list.length ? h('ul', {class: 'projects'}, ...list.map(p => h('li', {},
        h('a', {href: `#/p/${p.id}`}, p.name), h('span', {class: 'muted small'}, `${p.strings} strings · TD ${fmt0(p.td)} ft · updated ${new Date(p.updated).toLocaleString()}`),
        h('span', {class: 'spacer'}), h('a', {href: `/report/${p.id}`, target: '_blank', class: 'small'}, 'report'),
        h('button', {class: 'x', title: 'delete', onclick: async () => { if (confirm(`Delete "${p.name}"?`)) { await api(`/api/projects/${p.id}`, 'DELETE'); renderHome(); } }}, '×'))))
      : h('div', {class: 'empty'}, 'No wells yet. Start from an example above — every field can be changed.')));
}
async function newProject(example) {
  const well = await api('/api/example?name=' + example);
  const p = await api('/api/projects', 'POST', {name: well.name, well});
  location.hash = `#/p/${p.id}/well`;
}
async function importEdm(file) {
  if (!file) return;
  const fd = new FormData(); fd.append('file', file);
  const r = await fetch('/api/import', {method: 'POST', body: fd});
  if (!r.ok) { alert(await r.text()); return; }
  const d = await r.json();
  const design = Object.fromEntries(Object.entries(d.specs).map(([n, s]) => [n, {weight: s.weight, grade: s.grade, connection: s.connection}]));
  const p = await api('/api/projects', 'POST', {name: d.well.name, well: d.well, design});
  sessionStorage.setItem('import-notes-' + p.id, JSON.stringify(d.warnings));
  location.hash = `#/p/${p.id}/strings`;
}

// ---------------------------------------------------------------- project
async function openProject(id, step) {
  if (!project || project.id !== id) { project = await api(`/api/projects/${id}`); designData = null; }
  renderProject(step);
}
function markDirty() { dirty = true; designData = null; $('#save-state').textContent = 'unsaved…'; clearTimeout(saveTimer); saveTimer = setTimeout(save, 800); }
async function save() {
  if (!project || !dirty) return;
  try { project = await api(`/api/projects/${project.id}`, 'PUT', {name: project.name, well: project.well, design: project.design});
    dirty = false; $('#save-state').textContent = 'saved'; }
  catch (e) { $('#save-state').textContent = 'save failed: ' + e.message; }
}
function renderProject(step) {
  const w = project.well;
  app.replaceChildren(
    h('div', {class: 'row', style: 'justify-content:space-between'},
      h('input', {value: project.name, style: 'font-size:18px;font-weight:600;border:none;background:none;padding:4px 0;min-width:300px', onchange: e => { project.name = e.target.value; markDirty(); }}),
      h('div', {class: 'row'}, h('a', {href: `/report/${project.id}`, target: '_blank'}, h('button', {}, 'Report')),
        h('button', {onclick: () => { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(w, null, 2)], {type: 'application/json'})); a.download = project.name.replace(/[^\w.-]+/g, '_') + '.json'; a.click(); }}, 'Export JSON'))),
    h('div', {class: 'steps'}, ...STEPS.map(([k, label], i) => h('button', {'aria-current': k === step ? 'step' : null, class: STEPS.findIndex(s => s[0] === step) > i ? 'done' : '', onclick: () => location.hash = `#/p/${project.id}/${k}`}, `${i + 1}. ${label}`))),
    h('div', {id: 'step'}));
  const el = $('#step');
  if (step === 'design') renderDesign(el); else { const ed = h('div', {id: 'editor'}); el.append(ed); Editor.mount(ed, markDirty); Editor.set(w, step); Editor.bind(obj => { project.well = obj; }); }
  const notes = sessionStorage.getItem('import-notes-' + project.id);
  if (notes && step === 'strings') { el.prepend(h('div', {class: 'panel'}, h('h2', {}, 'Imported from EDM — please review'), h('ul', {class: 'small warn'}, ...JSON.parse(notes).map(n => h('li', {}, n))))); sessionStorage.removeItem('import-notes-' + project.id); }
  if (step !== 'design') {
    const nav = h('div', {class: 'row', style: 'justify-content:flex-end'});
    const refresh = () => { const errs = validateWell(project.well).filter(i => i.level === 'error'); nav.replaceChildren(...[
      errs.length ? h('span', {class: 'fail small'}, `${errs.length} thing${errs.length > 1 ? 's' : ''} to fix before designing`) : null,
      h('button', {class: 'primary', disabled: step === 'strings' && errs.length > 0, onclick: () => { const i = STEPS.findIndex(s => s[0] === step); location.hash = `#/p/${project.id}/${STEPS[i + 1][0]}`; }}, step === 'strings' ? 'Design my well →' : 'Next →')].filter(Boolean)); };
    refresh(); el.addEventListener('change', () => setTimeout(refresh, 300)); el.append(nav);
  }
}

// ---------------------------------------------------------------- design
async function renderDesign(el) {
  el.replaceChildren(h('div', {class: 'panel'}, h('div', {class: 'row'}, h('span', {}, 'Running the optimizer for every string…'))));
  await save();
  const errs = validateWell(project.well).filter(i => i.level === 'error');
  if (errs.length) { el.replaceChildren(h('div', {class: 'panel'}, h('h2', {}, 'Fix these first'), ...errs.map(e => h('div', {class: 'fail'}, '✗ ' + e.msg)), h('div', {class: 'row'}, h('button', {onclick: () => location.hash = `#/p/${project.id}/strings`}, '← Back to casing program')))); return; }
  try { if (!designData) designData = await api('/api/design', 'POST', {well: project.well, choices: project.design && Object.keys(project.design).length ? project.design : null, grades: project.well.prefs?.grades || null}); }
  catch (e) { el.replaceChildren(h('div', {class: 'panel'}, h('div', {class: 'err'}, e.message))); return; }
  const d = designData;
  const allPass = d.strings.every(s => s.result && s.result.pass);
  el.replaceChildren(
    h('div', {class: 'panel'}, h('div', {class: 'row', style: 'justify-content:space-between'},
      h('h2', {style: 'margin:0'}, allPass ? '✓ Every string passes' : '✗ Some strings need attention'),
      h('div', {class: 'row'}, h('button', {class: 'link', onclick: () => { project.design = {}; markDirty(); designData = null; renderDesign(el); }}, 'Reset to recommendations'),
        h('a', {href: `/report/${project.id}`, target: '_blank'}, h('button', {class: 'primary'}, 'Open report')))),
      ...(d.warnings || []).map(w => h('div', {class: 'warn small'}, '⚠ ' + w))),
    h('div', {class: 'cards'}, ...d.strings.map(stringCard)),
    h('div', {id: 'detail'}));
}
function stringCard(s) {
  const r = s.result, rec = s.recommended;
  const card = h('div', {class: 'card'});
  card.append(h('div', {class: 'row', style: 'justify-content:space-between'}, h('h3', {}, `${s.string} · ${s.od}"`), r ? h('span', {class: 'badge ' + (r.pass ? 'pass' : 'fail')}, r.pass ? 'PASS' : 'FAIL') : h('span', {class: 'badge fail'}, 'NO PIPE PASSES')));
  if (!r) { card.append(h('p', {class: 'muted small'}, 'No catalog pipe meets the design factors over the full length. Consider a larger OD, a shallower shoe, or relaxing the load basis.')); return card; }
  card.append(h('div', {class: 'pipe'}, r.design.uniform ? r.spec.label : 'Tapered: ' + r.design.sections.map(x => x.spec.label).join(' / ')),
    h('div', {class: 'small muted'}, s.overridden ? 'your selection' : (rec ? (rec.kind === 'tapered' ? 'cheapest passing design (tapered)' : 'cheapest passing pipe') : '')),
    h('div', {class: 'dfs'}, ...Object.entries(r.summary).map(([k, v]) => h('div', {class: 'df'}, k, h('b', {class: v.pass ? 'pass' : 'fail'}, fmt(v.min_df)), h('span', {class: 'muted'}, `≥ ${v.required} · ${v.case}`)))));
  if (!r.design.uniform) card.append(h('table', {}, h('tbody', {}, ...r.design.sections.map(x => h('tr', {}, h('td', {}, `${fmt0(x.top_md)}–${fmt0(x.bottom_md)} ft`), h('td', {}, x.spec.label))))));
  const pipes = catalog.pipes.filter(p => Math.abs(p.od - s.od) < 1e-6);
  const cur = r.design.sections[0].spec;
  const wt = h('select', {}, ...pipes.map(p => h('option', {value: p.weight, selected: p.weight === cur.weight}, p.weight + '#')));
  const gr = h('select', {}, ...catalog.grades.map(g => h('option', {selected: g === cur.grade}, g)));
  const cn = h('select', {}, ...catalog.connections.map(c => h('option', {selected: c === cur.connection}, c)));
  const apply = async () => { project.design = project.design || {}; project.design[s.string] = {weight: +wt.value, grade: gr.value, connection: cn.value}; dirty = true; designData = null; await save(); renderDesign($('#step')); };
  card.append(h('details', {}, h('summary', {}, 'Choose a different pipe', h('span', {class: 'muted small'}, `${s.alternatives.length} passing uniform options`)),
    h('div', {class: 'row'}, wt, gr, cn, h('button', {onclick: apply}, 'Use')),
    s.alternatives.length ? h('table', {}, h('tbody', {}, ...s.alternatives.map(a => h('tr', {}, h('td', {}, a.design.label), h('td', {class: 'muted small'}, `cost idx ${fmt(a.cost_per_ft, 1)}/ft`), h('td', {}, h('button', {class: 'link', onclick: () => { wt.value = a.design.sections[0].spec.weight; gr.value = a.design.sections[0].spec.grade; cn.value = a.design.sections[0].spec.connection; apply(); }}, 'use')))))) : null));
  card.append(h('button', {class: 'link', onclick: () => showDetail(s)}, 'Show loads & plots ↓'));
  return card;
}
function showDetail(s) {
  const r = s.result, det = $('#detail');
  det.replaceChildren(h('div', {class: 'panel'}, h('h2', {}, `${s.string} — load cases vs rating`),
    h('table', {}, h('thead', {}, h('tr', {}, h('th', {}, 'Load case'), h('th', {}, 'Basis'))), h('tbody', {}, ...r.cases.map(c => h('tr', {}, h('td', {}, c.name), h('td', {class: 'small muted'}, c.description))))),
    h('div', {class: 'plots'}, h('div', {class: 'plot', id: 'p-burst'}), h('div', {class: 'plot', id: 'p-collapse'}), h('div', {class: 'plot', id: 'p-tension'}), h('div', {class: 'plot', id: 'p-vme'}))));
  plotCheck('p-burst', r, 'burst', 'Burst: differential pressure (psi)'); plotCheck('p-collapse', r, 'collapse', 'Collapse: differential pressure (psi)');
  plotCheck('p-tension', r, 'tension', 'Tension: axial load (lbf)'); plotEllipse('p-vme', r);
  det.scrollIntoView({behavior: 'smooth'});
}
const palette = ['#1f5fbf', '#d35400', '#1e8e4f', '#8e44ad', '#c0392b', '#16a085', '#7f8c8d', '#b7950b'];
const layoutBase = (title, xTitle) => ({title: {text: title, font: {size: 13}}, margin: {l: 60, r: 20, t: 40, b: 50}, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {color: getComputedStyle(document.body).color},
  xaxis: {title: xTitle, gridcolor: 'rgba(128,128,128,.25)', zeroline: false}, yaxis: {title: 'MD (ft)', autorange: 'reversed', gridcolor: 'rgba(128,128,128,.25)'}, legend: {orientation: 'h', y: -0.2, font: {size: 11}}});
function plotCheck(id, r, check, title) {
  const req = r.summary[check].required, checks = r.checks.filter(c => c.check === check && c.load.some(x => x > 0));
  const traces = checks.map((c, i) => ({x: c.load, y: c.md, name: c.case, mode: 'lines', line: {color: palette[i % palette.length], width: 2}}));
  const rating = r.checks.find(c => c.check === check);
  traces.push({x: rating.rating.map(x => x / req), y: rating.md, name: `Rating / DF ${req}`, mode: 'lines', line: {color: '#000', dash: 'dash', width: 2}});
  traces.push({x: rating.rating, y: rating.md, name: 'Rating', mode: 'lines', line: {color: '#888', dash: 'dot', width: 1}});
  Plotly.newPlot(id, traces, layoutBase(title, title.split(':')[1]), {responsive: true, displaylogo: false});
}
function plotEllipse(id, r) {
  const s = r.spec, Yp = s.yield, req = r.summary.triaxial.required, ro = s.od / 2, ri = s.id / 2, area = Math.PI * (ro * ro - ri * ri), k = (ro * ro + ri * ri) / (ro * ro - ri * ri), Y = Yp / req;
  const xs = [], up = [], dn = [];
  for (let i = 0; i <= 200; i++) { const sa = -Y * 2 / Math.sqrt(3) + i * (2 * Y * 2 / Math.sqrt(3)) / 200, disc = Y * Y - 0.75 * sa * sa; if (disc < 0) continue; const root = Math.sqrt(disc); xs.push(sa * area / 1000); up.push((sa / 2 + root) / k); dn.push((sa / 2 - root) / k); }
  const traces = [{x: xs.concat([...xs].reverse()), y: up.concat([...dn].reverse()), mode: 'lines', name: `Triaxial limit / DF ${req}`, line: {color: '#000', width: 2}},
    {x: [-s.body_yield / 1000, s.tension_rating / 1000, s.tension_rating / 1000, -s.body_yield / 1000, -s.body_yield / 1000], y: [s.burst / r.summary.burst.required, s.burst / r.summary.burst.required, -s.collapse / r.summary.collapse.required, -s.collapse / r.summary.collapse.required, s.burst / r.summary.burst.required], mode: 'lines', name: 'API uniaxial limits / DF', line: {color: '#888', dash: 'dash'}}];
  r.cases.forEach((c, i) => traces.push({x: c.axial.map(f => f / 1000), y: c.internal.map((p, j) => p - c.external[j]), mode: 'markers', name: c.name, marker: {size: 5, color: palette[i % palette.length]}}));
  Plotly.newPlot(id, traces, {title: {text: 'Design envelope (triaxial, inner wall; top section)', font: {size: 13}}, margin: {l: 60, r: 20, t: 40, b: 50}, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {color: getComputedStyle(document.body).color},
    xaxis: {title: 'Axial load (klbf, tension +)', gridcolor: 'rgba(128,128,128,.25)', zeroline: true}, yaxis: {title: 'Differential pressure Pi − Pe (psi)', gridcolor: 'rgba(128,128,128,.25)', zeroline: true}, legend: {orientation: 'h', y: -0.2, font: {size: 11}}}, {responsive: true, displaylogo: false});
}

(async () => { catalog = await api('/api/catalog'); route(); })();
