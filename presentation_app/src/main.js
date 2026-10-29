// ---------------------------------------------------------------- app shell: tabs, presentation, 3-D explorer, data room
import { $, $$, h, Narrator, Player } from './engine.js';
import { Field3D, STATUS_COL, STATUS_LABEL, RAMP_CSS } from './field3d.js';
import { buildSlides } from './slides.js';

const BASE = 'data/';
const state = { tab: 'present' };

// ---------------------------------------------------------------- history model: well status, rates and cumulatives at any date
export function makeHistory(D) {
  const byWell = {};
  for (const r of D.prod) { (byWell[r.w] ||= []).push(r); }
  for (const k in byWell) byWell[k].sort((a, b) => a.t - b.t);
  const tl = {}; for (const w of D.wells) tl[w.well] = (w.status_timeline || []).map(s => ({ ...s, f: toT(s.from), u: s.to ? toT(s.to, true) : 1e9 }));
  function toT(s, end) { if (!s) return null; const p = String(s).split('-').map(Number); const y = p[0], m = p[1] || (end ? 12 : 1), d = p[2] || (end ? 28 : 1); return y + (m - 1) / 12 + (d - 1) / 365; }
  function at(t) {
    const out = {}; let fieldOil = 0, fieldWater = 0, fieldRate = 0, nprod = 0;
    for (const w of D.wells) {
      const segs = tl[w.well]; let st = null;
      for (const s of segs) if (t >= s.f && t < s.u) st = s.status;
      if (!st && segs.length && t >= segs[segs.length - 1].f) st = segs[segs.length - 1].status;
      const recs = byWell[w.well] || []; let cum = 0, cumw = 0, q = 0;
      for (const r of recs) { if (r.t > t) break; cum += r.o || 0; cumw += r.wt || 0; if (t - r.t < 1 / 12 + 1e-6) q = (r.o || 0) / 30.4; }
      cum += (w.cum_base && t >= w.cum_base.t ? w.cum_base.v : 0);
      const vis = st != null || (segs.length && t >= segs[0].f);
      out[w.well] = { visible: vis, status: st || (vis ? 'none' : undefined), oil_bpd: q, cum_oil: cum, cum_water: cumw };
      if (q > 0) nprod++; fieldOil += cum; fieldWater += cumw; fieldRate += q;
    }
    return { wells: out, fieldOil, fieldWater, fieldRate, nprod };
  }
  return { at, toT, byWell };
}

async function boot() {
  const [D, M] = await Promise.all([fetch(BASE + 'app_data.json').then(r => r.json()), fetch(BASE + 'viewer_meta.json').then(r => r.json())]);
  const field = new Field3D(M, BASE); const hist = makeHistory(D);
  const narrator = new Narrator();   // never throws: a broken browser speech engine leaves the recorded narration working
  narrator.es = await fetch(BASE + 'narration_es.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));
  narrator.loadStudio('audio/', [{ id: 'en-heart', lang: 'en', label: 'Studio · English, female (neural)' }, { id: 'es-claude', lang: 'es', label: 'Studio · Mexican Spanish, male (neural)' }]);
  const ctx = { D, M, field, hist, narrator, fast: false };
  window.TEC = ctx;
  // ---------------- tabs
  const tabs = $$('[data-tab]');
  function setTab(t) {
    state.prev = state.tab; state.tab = t; tabs.forEach(b => b.setAttribute('aria-selected', b.dataset.tab === t)); $$('.tab').forEach(s => s.hidden = s.id !== 'tab-' + t);
    if (t === 'present') { field.mount($('#glPresent')); field.paused = player.slides[player.si]?.kind !== '3d'; fitStage(); if (state.prev === 'field') player.go(player.si, Math.max(0, player.step), { play: false }); }   // put the slide's own scene back
    if (t === 'field') { player.pause(); field.paused = false; field.mount($('#glField')); explorer.enter(); }
    if (t === 'data') player.pause();
    if (t === 'slides') { player.pause(); deck.enter(); }
    try { history.replaceState(null, '', '#' + t); } catch (e) {}
  }
  tabs.forEach(b => b.addEventListener('click', () => setTab(b.dataset.tab)));
  // ---------------- presentation
  const stage = $('#stage'), wrap = $('#stageWrap');
  function fitStage() {
    const s = Math.min(wrap.clientWidth / 1920, wrap.clientHeight / 1080); stage.style.transform = `scale(${s})`;
    stage.style.left = (wrap.clientWidth - 1920 * s) / 2 + 'px'; stage.style.top = (wrap.clientHeight - 1080 * s) / 2 + 'px';
    field.renderer.setPixelRatio(Math.min(2, Math.max(0.6, s * (window.devicePixelRatio || 1)))); field.resize();
  }
  new ResizeObserver(() => { if (state.tab === 'present') fitStage(); else field.resize(); }).observe(document.body);
  const slides = buildSlides(ctx);
  const cap = $('#caption'), capOn = { v: true };
  narrator.onSentence = s => { cap.textContent = s; cap.classList.toggle('on', !!s && capOn.v); };
  const outline = $('#outline');
  slides.forEach((s, i) => outline.append(h('option', { value: i }, `${String(i + 1).padStart(2, '0')}  ${s.section ? s.section + ' · ' : ''}${s.title}`)));
  const prog = $('#progress');
  const ui = {
    onSlide(i, s) { outline.value = i; $('#slideNo').textContent = `${i + 1} / ${slides.length}`; prog.style.width = ((i + 1) / slides.length * 100) + '%'; },
    onStep(p) { $('#stepDots').innerHTML = p.steps.map((_, k) => `<i class="${k < p.step ? 'done' : k === p.step ? 'cur' : ''}"></i>`).join(''); },
    onPlay(on) { $('#play').setAttribute('aria-pressed', on); $('#play').innerHTML = on ? '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14"/><rect x="14" y="5" width="4" height="14"/></svg><span>Pause</span>' : '<svg viewBox="0 0 24 24"><path d="M7 5l12 7-12 7z"/></svg><span>Play</span>'; }
  };
  const player = new Player({ stage, slideLayer: $('#slides'), glLayer: $('#glPresent'), slides, ctx, ui });
  ctx.player = player;
  $('#play').onclick = () => { narrator.unlock(); player.toggle(); }; $('#next').onclick = () => player.next(); $('#prev').onclick = () => player.prev();
  outline.onchange = () => player.go(+outline.value, 0);
  const vs = $('#voice');
  narrator.onVoices = vv => { vs.innerHTML = ''; vv.slice(0, 40).forEach(v => vs.append(h('option', { value: v.name }, v.studio ? v.label : `Browser · ${v.name.replace(/Microsoft |Google /, '')} · ${v.lang}`))); if (narrator.voice) vs.value = narrator.voice.name; vs.disabled = !vv.length; };
  if (narrator.voices.length) narrator.onVoices(narrator.voices);

  vs.onchange = () => { const was = player.playing; narrator.setVoice(vs.value); narrator.prepare(player.slides[player.si].id); if (was) player.go(player.si, Math.max(0, player.step), { play: true }); };
  const setLangUI = () => { $('#langEn').setAttribute('aria-pressed', narrator.lang === 'en'); $('#langEs').setAttribute('aria-pressed', narrator.lang === 'es'); };
  const chooseLang = l => { if (l === narrator.lang) return; const was = player.playing; narrator.setLang(l); setLangUI(); if (was) player.go(player.si, Math.max(0, player.step), { play: true }); };
  $('#langEn').onclick = () => chooseLang('en'); $('#langEs').onclick = () => chooseLang('es'); setLangUI();
  $('#rate').oninput = e => { narrator.setRate(+e.target.value); $('#rateOut').textContent = narrator.rate.toFixed(2) + '×'; };
  $('#mute').onclick = e => { narrator.muted = !narrator.muted; e.currentTarget.setAttribute('aria-pressed', narrator.muted); e.currentTarget.querySelector('span').textContent = narrator.muted ? 'Voice off' : 'Voice on'; };
  $('#caps').onclick = e => { capOn.v = !capOn.v; e.currentTarget.setAttribute('aria-pressed', capOn.v); cap.classList.toggle('on', capOn.v && !!cap.textContent); };
  $('#full').onclick = () => { const el = $('#tab-present'); (document.fullscreenElement ? document.exitFullscreen() : el.requestFullscreen?.())?.catch?.(() => {}); };
  document.addEventListener('keydown', e => {
    if (state.tab === 'slides' && !/INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return deck.key(e);
    if (state.tab !== 'present' || /INPUT|SELECT|TEXTAREA/.test(e.target.tagName)) return;
    if (e.key === ' ' || e.key === 'k') { e.preventDefault(); player.toggle(); }
    else if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); player.next(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); player.prev(); }
  });
  // ---------------- explorer + data room
  const explorer = makeExplorer(ctx); makeDataRoom(ctx); const deck = makeDeck();
  const start = (location.hash || '').replace('#', '');
  await player.go(0, 0, { play: false });   // build the first slide before any tab, so its scene cannot overwrite the explorer's
  setTab(['present', 'field', 'data', 'slides'].includes(start) ? start : 'present');
  $('#loading').hidden = true;
}

// ---------------------------------------------------------------- 3-D explorer tab
function makeExplorer(ctx) {
  const { field, hist, D, M } = ctx; const host = $('#fieldCtl');
  const st = { vol: 'pstm', il: null, xl: null, k: null, cmap: 'rwb', year: 2026.8, playing: false };
  const row = (lab, el, out) => h('label', { class: 'ctl' }, h('span', {}, lab), el, out || '');
  const sel = (id, opts) => { const s = h('select', { id }); opts.forEach(([v, t]) => s.append(h('option', { value: v }, t))); return s; };
  const rng = (id, min, max, step, val) => h('input', { type: 'range', id, min, max, step, value: val });
  const volS = sel('xVol', [['pstm', 'PEMEX PSTM 554702 (time, shown in depth)'], ['psdm', 'PSDM 2019 (depth)'], ['', 'No seismic']]);
  const cmS = sel('xCmap', [['rwb', 'Red / white / blue'], ['grey', 'Greyscale']]);
  const ilR = rng('xIl', 0, 170, 1, 103), xlR = rng('xXl', 0, 171, 1, 80), kR = rng('xK', 0, 250, 1, 108);
  const ilC = h('input', { type: 'checkbox', id: 'xIlOn', checked: true }), xlC = h('input', { type: 'checkbox', id: 'xXlOn', checked: true }), kC = h('input', { type: 'checkbox', id: 'xKOn' });
  const veR = rng('xVe', 1, 8, 0.5, 2.5), yrR = rng('xYear', 1955, 2026.8, 0.1, 2026.8);
  const ilO = h('output'), xlO = h('output'), kO = h('output'), veO = h('output'), yrO = h('output');
  const surfC = h('input', { type: 'checkbox', id: 'xSurf', checked: true }), owcC = h('input', { type: 'checkbox', id: 'xOwc', checked: true }), labC = h('input', { type: 'checkbox', id: 'xLab', checked: true });
  const playB = h('button', { id: 'xPlay', class: 'btn' }, 'Play history');
  const wellsBox = h('div', { class: 'wellbtns' });
  for (const w of M.wells) wellsBox.append(h('button', { class: 'btn sm', onclick: () => { field.setHighlight(w.well); field.focusWell(w.well); readout(w.well); } }, w.well));
  const views = h('div', { class: 'wellbtns' }, ...['reservoir', 'overview', 'crest', 'section', 'top', 'surface'].map(v => h('button', { class: 'btn sm', onclick: () => field.view(v) }, v[0].toUpperCase() + v.slice(1))));
  const ro = h('div', { class: 'readout', id: 'xRead' });
  host.append(
    h('h3', {}, 'Seismic'), row('Volume', volS), row('Colour', cmS),
    h('div', { class: 'ctl2' }, ilC, row('Inline', ilR, ilO)), h('div', { class: 'ctl2' }, xlC, row('Crossline', xlR, xlO)), h('div', { class: 'ctl2' }, kC, row('Depth slice', kR, kO)),
    h('h3', {}, 'Display'), h('div', { class: 'checks' }, h('label', {}, surfC, 'El Abra top (Jan 2019 grid)'), h('label', {}, owcC, 'Lowest known oil −2,374 m'), h('label', {}, labC, 'Well labels')),
    row('Vertical exag.', veR, veO), h('h3', {}, 'History'), row('Date', yrR, yrO), playB,
    h('h3', {}, 'Wells'), wellsBox, h('h3', {}, 'Views'), views, ro,
    h('p', { class: 'fine' }, 'Drag to orbit, right-drag or two fingers to pan, scroll or pinch to zoom. Seismic is an 8-bit display copy of the Colab extracts, for orientation only. The PSTM is placed in depth at the well-tie velocity (2,914–2,951 m/s), exact at the reef top and approximate away from it. Well colours follow the status legend; columns at the wellheads grow with cumulative oil (green) and water (blue).'));
  const legendEl = $('#fieldLegend');
  legendEl.innerHTML = Object.entries({ producing: 'Producing', shut_in: 'Shut in', restorable: 'Shut in, restorable', injector: 'Water injector', testing: 'Testing / workover', plugged: 'Plugged', planned: 'Planned' }).map(([k, t]) => `<span><i style="background:#${STATUS_COL[k].toString(16).padStart(6, '0')}"></i>${t}</span>`).join('') +
    `<span class="ramp">El Abra top <b style="background:linear-gradient(90deg,${RAMP_CSS.join(',')})"></b> deep → high</span>`;
  function info() { return M[st.vol]; }
  function apply() {
    const I = st.vol ? info() : null;
    if (I) { ilR.max = I.ni - 1; xlR.max = I.nj - 1; kR.max = I.nk - 1; }
    const zOf = k => I.axis === 'time_ms' ? `≈${Math.round((I.k0 + k * I.dk) / 2000 * I.v_field_mps).toLocaleString()} m` : `${Math.round(I.k0 + k * I.dk).toLocaleString()} m`;   // PSTM: depth at the well-tie velocity
    ilO.textContent = I ? `${(I.inline0 ?? 0) + +ilR.value}` : ''; xlO.textContent = I ? `${(I.crossline0 ?? 0) + +xlR.value}` : ''; kO.textContent = I ? zOf(+kR.value) : '';
    field.setSlices(st.vol ? { vol: st.vol, il: ilC.checked ? +ilR.value : null, xl: xlC.checked ? +xlR.value : null, k: kC.checked ? +kR.value : null, cmap: cmS.value } : null);
  }
  function setYear(y) { st.year = y; yrR.value = y; const yy = Math.floor(y), mm = Math.floor((y - yy) * 12) + 1; yrO.textContent = `${yy}-${String(mm).padStart(2, '0')}`; const ws = hist.at(y).wells; if (y > 2023.2) { ws['TEC-10'].status = 'restorable'; ws['TEC-2'].status = 'restorable'; } field.setWellStates(withCaptions(ws)); }
  function withCaptions(ws) { for (const [k, s] of Object.entries(ws)) s.caption = s.status && s.status !== 'none' ? STATUS_LABEL[s.status] || s.status : ''; return ws; }
  function readout(w) {
    const W = D.wells.find(x => x.well === w); if (!W) return; const s = hist.at(st.year).wells[w] || {};
    ro.innerHTML = `<b>${w}</b> · ${W.type || ''}<br>${W.result || ''}<br>Spud ${W.spud || '—'} · TD ${W.td_mmd ? W.td_mmd.toLocaleString() + ' mMD' : '—'}<br>El Abra top ${W.el_abra_top_mss ? '−' + Math.abs(W.el_abra_top_mss).toLocaleString() + ' m' : '—'}<br>Cumulative oil to date shown: ${Math.round(s.cum_oil || 0).toLocaleString()} bbl<br>Now: ${W.status_now || ''}`;
  }
  [volS, cmS, ilR, xlR, kR, ilC, xlC, kC].forEach(e => e.addEventListener('input', () => { st.vol = volS.value; apply(); }));
  veR.oninput = () => { veO.textContent = veR.value + '×'; field.setVE(+veR.value); setYear(st.year); };
  surfC.onchange = () => field.showSurface(surfC.checked, 1); owcC.onchange = () => field.owc.visible = owcC.checked; labC.onchange = () => { field.labelsOn = labC.checked; setYear(st.year); };
  yrR.oninput = () => setYear(+yrR.value);
  playB.onclick = () => {
    if (st.playing) { st.playing = false; playB.textContent = 'Play history'; return; }
    st.playing = true; playB.textContent = 'Stop'; if (st.year > 2026) setYear(1955.5);
    const t0 = performance.now(), y0 = st.year; const run = () => { if (!st.playing) return; const y = Math.min(2026.8, y0 + (performance.now() - t0) / 1000 * 1.6); setYear(y); if (y < 2026.8) requestAnimationFrame(run); else { st.playing = false; playB.textContent = 'Play history'; } }; run();
  };
  veO.textContent = '2.5×';
  // the presentation shares this 3-D field: reset everything it may have changed (spin, pads, labels, surface opacity, VE, camera)
  return { enter() {
    field.paused = false; field.orbit(false); field.setPads(null); field.setTarget(null); field.setFocusMode({}); field.setShift(0, 0); field.setHighlight(null);
    field.labelsOn = labC.checked; field.owc.visible = owcC.checked; if (field.ve !== +veR.value) field.setVE(+veR.value);
    field.showSurface(surfC.checked, 1); setYear(st.year); st.vol = volS.value; apply(); field.view('reservoir', 1200);
  } };
}

// ---------------------------------------------------------------- slides tab: the static technical deck, page by page, printable
function makeDeck() {
  const wrap = $('#deckWrap'), stage = $('#deckStage'), notes = $('#deckNotes'), sel = $('#dOutline'); let S = null, i = 0, loading = null;
  const fit = () => { const s = Math.min((wrap.clientWidth - 24) / 1920, (wrap.clientHeight - 24) / 1080); stage.style.transform = `scale(${s})`; stage.style.left = (wrap.clientWidth - 1920 * s) / 2 + 'px'; stage.style.top = (wrap.clientHeight - 1080 * s) / 2 + 'px'; };
  new ResizeObserver(() => { if (S) fit(); }).observe(wrap);
  const show = k => { if (!S) return; i = Math.max(0, Math.min(S.slides.length - 1, k)); const s = S.slides[i]; stage.innerHTML = s.html; notes.innerHTML = s.notes ? `<b>Notes.</b> ${s.notes}` : '<i>No notes for this slide.</i>'; sel.value = i; $('#dNo').textContent = `${i + 1} / ${S.slides.length}`; };
  const load = () => loading ||= fetch('deck/deck.json').then(r => r.json()).then(d => {
    S = d; let sec = ''; d.slides.forEach((s, k) => { if (s.section !== sec) { sec = s.section; sel.append(h('option', { disabled: true }, '— ' + sec)); } sel.append(h('option', { value: k }, `${String(k + 1).padStart(2, '0')}  ${s.title}`)); });
    $('#deckPrint').innerHTML = d.slides.map(s => `<div class="deckslide">${s.html}</div>`).join('');
    fit(); show(0);
  }).catch(e => { stage.innerHTML = `<p style="padding:40px;font-size:28px">Could not load the slides: ${e.message}</p>`; });
  $('#dPrev').onclick = () => show(i - 1); $('#dNext').onclick = () => show(i + 1); sel.onchange = () => show(+sel.value);
  $('#dNotesB').onclick = e => { notes.hidden = !notes.hidden; e.currentTarget.setAttribute('aria-pressed', !notes.hidden); fit(); };
  $('#dPrint').onclick = () => load().then(() => window.print());
  $('#dFull').onclick = () => { const el = $('#tab-slides'); (document.fullscreenElement ? document.exitFullscreen() : el.requestFullscreen?.())?.catch?.(() => {}); };
  return {
    enter() { load().then(fit); },
    key(e) { if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); show(i + 1); } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(i - 1); } else if (e.key === 'n' || e.key === 'N') $('#dNotesB').click(); }
  };
}

// ---------------------------------------------------------------- data room tab
function makeDataRoom(ctx) {
  const { D } = ctx; const host = $('#dataRoom');
  const table = (cols, rows, cls = '') => { const t = h('table', { class: 'tbl ' + cls }); t.append(h('thead', {}, h('tr', {}, ...cols.map(c => h('th', {}, c[1]))))); const tb = h('tbody'); rows.forEach(r => tb.append(h('tr', {}, ...cols.map(c => h('td', { class: c[2] || '' }, c[3] ? c[3](r[c[0]], r) : (r[c[0]] ?? '—')))))); t.append(tb); return h('div', { class: 'tblwrap' }, t); };
  const sec = (id, title, note, ...kids) => h('section', { class: 'dsec', id }, h('h2', {}, title), note ? h('p', { class: 'note' }, note) : '', ...kids);
  const n0 = v => v == null || v === '' ? '—' : Number(v).toLocaleString('en-US', { maximumFractionDigits: 1 });
  host.append(
    sec('d-wells', 'Wells', 'Surface locations UTM 14N WGS84. Depths are metres subsea (mSS) unless marked mMD.',
      table([['well', 'Well'], ['type', 'Type'], ['spud', 'Spud'], ['td_mmd', 'TD mMD', 'num', n0], ['el_abra_top_mss', 'El Abra top mSS', 'num', n0], ['result', 'Result'], ['cum_oil_bbl', 'Cum. oil bbl', 'num', n0], ['status_now', 'Status, Oct 2026']], D.wells)),
    sec('d-events', 'Field and well events', 'Chronological. Uncertain items are flagged in the detail.', table([['date', 'Date', 'mono'], ['well', 'Well'], ['category', 'Type'], ['title', 'Event'], ['detail', 'Detail'], ['source', 'Source', 'src']], D.events)),
    sec('d-pressure', 'Reservoir pressure measurements', null, table([['date', 'Date', 'mono'], ['well', 'Well'], ['type', 'Type'], ['depth_mss', 'Datum mSS', 'num', n0], ['p_kgcm2', 'kg/cm²', 'num', n0], ['p_psi', 'psi', 'num', n0], ['source', 'Source', 'src']], D.pressure)),
    sec('d-annual', 'Annual production by well', 'bbl. Pre-1966 TEC-6 and TEC-2 volumes are PEMEX wellfile allocations, not monthly records.', table(D.annualCols.map(c => [c, c, c === 'year' ? 'mono' : 'num', c === 'year' ? null : n0]), D.annual)),
    sec('d-sources', 'Sources and open items', null, h('ul', { class: 'srcs' }, ...D.sources.map(s => h('li', {}, s))))
  );
}

boot().catch(e => { console.error(e); const l = $('#loading'); if (l) l.textContent = 'The app could not load its data: ' + e.message; });
