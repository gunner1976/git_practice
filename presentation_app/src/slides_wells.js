// ---------------------------------------------------------------- field history time-lapse, well-by-well tour, production performance, current state
import { h, $, $$, countUp } from './engine.js';
import { C, timeChart, hbars, legend } from './charts.js';
import { STATUS_LABEL } from './field3d.js';
import { std, S, DT, ymd, scene, wellStates } from './slides_core.js';

const d3 = window.d3;
const NOW = 2026.8;
export const CURRENT = { 'TEC-10': { status: 'restorable' }, 'TEC-2': { status: 'restorable' } };   // Oct 2026 reading of the evidence (tec10_tec2_status.md)
const WELLS_P = ['TEC-6', 'TEC-2', 'TEC-7', 'TEC-9', 'TEC-10'];
const WCUT = '#f2c14e';   // water-cut line on the well charts

// monthly oil-rate matrix by well for stacked charts
function rateMatrix(D, t0 = 1956, t1 = 2023.99) {
  const months = []; for (let y = Math.floor(t0); y <= Math.floor(t1); y++) for (let m = 0; m < 12; m++) months.push(+(y + m / 12).toFixed(4));
  const idx = new Map(months.map((t, i) => [t, i])); const M = {}; WELLS_P.forEach(w => M[w] = new Array(months.length).fill(0));
  for (const r of D.prod) { if (!M[r.w]) continue; const i = idx.get(+r.t.toFixed(4)); if (i == null) continue; const d = new Date(Date.UTC(Math.floor(r.t), Math.round((r.t % 1) * 12) + 1, 0)).getUTCDate(); M[r.w][i] += (r.o || 0) / d; }
  return { months, dates: months.map(DT), M };
}
// monthly grid from the first to the last row: rows flagged z are documented zero months (CNH-reported zeros, shut-in segments of the
// well's status history); months with no row are left null so the line breaks there (no monthly record exists)
function wellSeries(D, w) {
  const rows = D.prod.filter(r => r.w === w).sort((a, b) => a.t - b.t); const out = { oil: [], water: [], wcut: [] };
  if (!rows.length) return out;
  const dim = t => new Date(Date.UTC(Math.floor(t), Math.round((t % 1) * 12) + 1, 0)).getUTCDate();
  const key = t => Math.round(t * 12), by = new Map(rows.map(r => [key(r.t), r]));
  for (let k = key(rows[0].t); k <= key(rows[rows.length - 1].t); k++) {
    const t = k / 12, d = DT(t), r = by.get(k);
    if (!r) { out.oil.push({ d, v: null }); out.water.push({ d, v: null }); out.wcut.push({ d, v: null }); continue; }
    const o = (r.o || 0) / dim(t), wt = r.wt != null ? r.wt / dim(t) : null;
    // water cut: volume-weighted over this and the two previous months that flowed; undefined (null) while the well is shut in
    let so = 0, sw = 0; if (wt != null && o + wt > 0.5) for (let j = 0; j < 3; j++) { const q = by.get(k - j); if (q && q.wt != null && (q.o || 0) + q.wt > 0) { so += q.o || 0; sw += q.wt; } }
    out.oil.push({ d, v: o }); out.water.push({ d, v: wt }); out.wcut.push({ d, v: so + sw > 0 ? 100 * sw / (so + sw) : null });
  }
  return out;
}
function animateClock(ctx, from, to, dur, onT) {
  return new Promise(res => {
    if (ctx.fast || !dur || from === to) { onT(to); return res(); }
    const t0 = performance.now(), gen = ctx.player.runGen;
    const tick = () => { if (gen !== ctx.player.runGen) return res(); const f = Math.min(1, (performance.now() - t0) / dur); const e = f < 0.5 ? 2 * f * f : 1 - Math.pow(-2 * f + 2, 2) / 2; onT(from + (to - from) * e); if (f < 1) requestAnimationFrame(tick); else res(); };
    tick();
  });
}
const yrLabel = t => { const y = Math.floor(t), m = Math.min(11, Math.floor((t - y) * 12)); return `${['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m]} ${y}`; };

export function wellSlides(ctx) {
  const D = ctx.D, F = ctx.field, P = {};
  const EV = D.events;

  // ================================================================ the time-lapse: sixty years, aggregated to today
  P.history = {
    id: 'history', kind: '3d', title: 'Sixty years in four minutes', section: 'History',
    build(el) {
      el.innerHTML = `<div class="glass" style="position:absolute;left:70px;top:56px;width:520px;padding:16px 26px"><div class="eyebrow" style="font-size:19px">Field history · 1956 → today</div><div class="big-year" id="hYear" style="font-size:110px">1956</div>
          <div class="ticker" id="hTick" style="font-size:22px"></div></div>
        <div class="glass" id="hPanel" style="position:absolute;right:70px;top:56px;width:640px;padding:22px 28px"></div>
        <div class="glass" style="position:absolute;left:70px;right:70px;bottom:104px;height:300px;padding:12px 20px 4px"><div id="hChart"></div></div>
        <div class="src" style="bottom:70px">Monthly records: CNH 1960–2016 (1960–65 field-level, attributed to TEC-6, the only producer then), Tonalli 2018–22 (commingled 2019–22 shown as TEC-10). Zero months are reported zeros or shut-ins; hatched 1956–59 = no monthly record. Pressure at 2,300 mSS. Well colours: green producing, amber shut in, blue injector, grey plugged.</div><div class="pg"></div>`;
      const R = rateMatrix(D);
      const pr = D.pressure.filter(p => p.usable).map(p => ({ d: ymd(p.date), v: p.p_mpa }));
      const ch = timeChart($('#hChart', el), { W: 1740, H: 280, m: { l: 86, r: 86, t: 14, b: 40 }, right: true, x: [ymd('1955-06'), ymd('2026-12')], yl: [0, 1000], yr: [0, 30], yticks: 4, ylabel: 'Oil, bbl/d', yrlabel: 'MPa',
        stack: WELLS_P.map(w => ({ key: w, color: C.wells[w], values: R.M[w] })), stackDates: R.dates, bands: [{ from: ymd('1956-06'), to: ymd('1960-01'), hatch: '#9aa6b2', opacity: 0, label: 'no record', vertical: true, size: 16 }],
        series: [{ key: 'p', type: 'dots', color: '#9cc7f0', r: 7, axis: 'r', values: pr }], xticks: 14 });
      const lg = legend($('#hChart', el), [...WELLS_P.map(w => [C.wells[w], w]), ['#9cc7f0', 'pressure, MPa', 'dot']]); lg.style.cssText += ';position:absolute;right:120px;top:12px;font-size:18px;gap:6px 16px';
      let T = 1955.9;
      const setT = t => {
        T = t; const s = ctx.hist.at(t); F.setWellStates(wellStates(ctx, t, { override: t > 2023.2 ? CURRENT : {} })); ch.revealTo(DT(t)); ch.cursor(DT(t));
        $('#hYear', el).textContent = Math.floor(t);
        $('#hTick', el).innerHTML = `<b>${Math.round(s.fieldRate)}</b> bbl/d · <b>${s.nprod}</b> well${s.nprod === 1 ? '' : 's'} producing<br>cumulative <b>${(s.fieldOil / 1e6).toFixed(2)}</b> MMbbl recorded`;
      };
      const panel = (title, items) => { $('#hPanel', el).innerHTML = `<h3 style="font-size:30px">${title}</h3><div class="evlist" style="margin-top:12px;gap:8px">${items.map(([d, t, s]) => `<div class="ev" style="grid-template-columns:150px 1fr"><span class="d" style="font-size:18px">${d}</span><span class="t" style="font-size:21px">${t}${s ? `<small style="font-size:18px">${s}</small>` : ''}</span></div>`).join('')}</div>`; };
      scene(ctx, { year: 1955.9, view: 'overview', dur: 0, captions: true, surfaceOpacity: 0.9, shift: [-0.16, 0.1] });
      setT(1955.9);
      const chap = (from, to, title, items, view, say) => ({ say, run: async f => { panel(title, items); if (view) (typeof view === 'string' ? F.view(view, f ? 0 : 2200) : F.focusWell(view.w, f ? 0 : 2200, view.o || {})); await animateClock(ctx, from, to, f ? 0 : ctx.stepDuration * 0.92, setT); } });
      return [
        chap(1955.9, 1957.3, 'Discovery, 1956–57', [['Feb 1956', 'TEC-3, the first well, finds oil over salt water low on the flank', 'Plugged. Its test sets the lowest known oil, −2,374 m'], ['Jun 1956', 'TEC-2 discovers the field', '453 bbl/d from El Abra; the top test flows gas-rich oil'], ['Jul 1956', 'TEC-5 finds the reef 248 m low; plugged'], ['Oct 1956 – Jan 1957', 'TEC-6 and TEC-7 complete at 480–560 bbl/d']], 'overview',
          'Watch the field build up in time. In 1956 PEMEX drilled five wells in a year. TEC-3, the first, found oil over salt water low on the north-east flank. TEC-2 discovered the field in June at four hundred and fifty barrels a day. TEC-5 found the reef far too low. TEC-6 and TEC-7 came in at five hundred barrels a day each.'),
        chap(1957.3, 1971.7, 'One well carries the field, 1957–71', [['Mar 1957', 'Salt water: TEC-2 and TEC-7 shut in after months', 'Both completed low, in the bottom of the column'], ['1957–71', 'TEC-6 alone: about 100 bbl/d for fourteen years'], ['Dec 1964', 'Static surveys: pressure still ~252 kg/cm²']], { w: 'TEC-6', o: { dist: 2600, az: -0.6, el: 0.4 } },
          'Within months salt water reached TEC-2 and TEC-7, which had been completed low in the column, and both were shut in. For fourteen years TEC-6 carried the field alone, at about a hundred barrels a day, and the 1964 pressure surveys still read the discovery pressure.'),
        chap(1971.7, 1973.6, 'Move up the column, 1971–73', [['Oct–Dec 1971', 'TEC-7, TEC-6 and TEC-2 recompleted 10–25 m higher'], ['Mar 1972', 'Field peak: 932 bbl/d from three wells', 'TEC-7 442 · TEC-2 269 · TEC-6 221'], ['Mar 1972', 'TEC-101 finds the reef low and wet on the west flank'], ['May 1973', 'TEC-9 completes on the southern high']], 'crest',
          'In late 1971 PEMEX worked over all three wells and moved each one ten to twenty five metres up the column, away from the water. In March 1972 the field peaked at nine hundred and thirty two barrels a day. TEC-101 found the west flank wet, and in 1973 TEC-9 was drilled on the southern high.'),
        chap(1973.6, 1999.2, 'Four wells, slow decline, 1973–99', [['1973–90', 'Four producers; water cut climbs in every well'], ['Mar 1976', 'TEC-6 moved up again, to 2,314–2,316 m', 'Second peak 293 bbl/d, 1977'], ['1980s', 'Wells cycled at 25–40 bbl/d, 50–80 % water'], ['Oct 1998', 'TEC-7 survey: 250.6 kg/cm², no depletion']], 'overview',
          'For the next quarter century four wells produced together. Water cut climbed everywhere, and the wells were cycled on and off to let the water cones settle. TEC-6 moved up a second time in 1976. By the 1980s each well made twenty five to forty barrels a day, yet a 1998 pressure survey still showed no depletion.'),
        chap(1999.2, 2016.3, 'PEMEX winds down, 1999–2016', [['1999–2003', 'Field shut in; TEC-9 restarts 2003 at ~100 bbl/d'], ['Dec 2006', 'TEC-6 and TEC-7 last production; TEC-6 abandoned 2007', 'Casing parted at 352 m, beside today’s TEC-10 / TEC-12 pad'], ['2012', 'TEC-9: solvent and acid lift it from 10 to 102 bbl/d', 'Damage, not depletion; plugged Jan 2013'], ['Jan 2016', 'TEC-2 last PEMEX production']], 'crest',
          'From 1999 PEMEX wound the field down. TEC-6 and TEC-7 last produced in 2006, and TEC-6 was abandoned with a parted casing. In 2012 a cheap solvent and acid job lifted TEC-9 from ten to a hundred barrels a day, which is damage, not depletion, but PEMEX plugged it a year later. TEC-2 made the last PEMEX oil in 2016.'),
        chap(2016.3, 2019.95, 'Tonalli, 2016–19', [['Nov 2016', 'Handover to Tonalli under licence CNH-R01-L03-A24/2016'], ['2018', 'TEC-10 drilled, cored, logged and tested: 194 bbl/d', 'Pressure 24.14 MPa: 2 % below discovery'], ['Nov 2018 – Aug 2019', 'TEC-11 horizontal: water only, plugged'], ['Aug 2019', 'TEC-7 becomes the field’s water-injection well']], { w: 'TEC-10', o: { dist: 2400, az: -0.3, el: 0.38 } },
          'In late 2016 PEMEX handed the field to Tonalli. In 2018 Tonalli cleaned out TEC-2 and drilled TEC-10, which tested a hundred and ninety four barrels a day and measured almost the discovery pressure. The horizontal TEC-11 made only water and was plugged, and TEC-7 was converted to take the field’s produced water.'),
        chap(2019.95, 2023.2, 'Producing, then shut in, 2020–23', [['2020–21', 'TEC-10 and TEC-2 produce 30–70 bbl/d at 70–86 % water', 'Solvent jobs keep wax out of the tubing'], ['Feb 2022', 'Field shut in after CNH rejects the evaluation report'], ['Nov 2022', 'TEC-10 stimulated and restarted: ~45 bbl/d'], ['Jan 2023', 'Last production: TEC-2 16, TEC-10 2 bbl/d']], 'overview',
          'Through 2020 and 2021 TEC-10, with TEC-2 at times, made thirty to seventy barrels a day at high water cut, kept going with solvent treatments for wax. The field was shut in in February 2022 after the regulator rejected the evaluation report. TEC-10 was stimulated and restarted in November, and the last oil was produced in January 2023.'),
        chap(2023.2, NOW, 'Today, October 2026', [['Producing', 'None'], ['Restorable', 'TEC-10 on a solvent schedule; TEC-2 intermittently'], ['Injector', 'TEC-7 (state to confirm)'], ['Plugged', 'TEC-3, 5, 6, 9, 101; TEC-11 temporarily abandoned'], ['Planned', 'TEC-12 at the crest']], 'surface',
          'And that brings us to today. Nothing is producing. TEC-10 can be brought back on a solvent-treatment schedule, and TEC-2 can produce intermittently alongside it. TEC-7 is the disposal well. Every PEMEX producer except TEC-2 is plugged. About one point seven million barrels are in the monthly record, nearly two million with PEMEX’s early allocations, and the crest of the reef is still untouched.')
      ];
    }
  };

  // ================================================================ well-by-well
  function wellSlide(o) {
    return {
      id: 'w-' + o.well, kind: '3d', title: o.title, section: 'Well by well',
      build(el) {
        const W = D.wells.find(w => w.well === o.well) || {};
        el.innerHTML = `<div class="glass" style="position:absolute;right:70px;top:56px;width:800px;padding:24px 30px 20px">
          <div class="eyebrow">${o.eyebrow}</div><h2 style="font-size:46px;margin-top:8px">${o.title}</h2>
          <div class="row" style="gap:26px;margin-top:16px;flex-wrap:wrap">${o.facts.map(([k, v]) => `<div><div style="font-size:17px;color:var(--ink3);text-transform:uppercase;letter-spacing:.08em">${k}</div><div style="font:600 26px var(--serif);color:var(--ink)">${v}</div></div>`).join('')}</div>
          <div id="wChart" style="margin-top:14px"></div><div class="evlist" id="wEv" style="margin-top:14px"></div></div>
          <div class="glass" style="position:absolute;left:70px;top:56px;padding:12px 22px"><div class="big-year" id="wYear" style="font-size:80px">—</div><div class="ticker" id="wTick" style="font-size:21px"></div></div>
          <div class="src">${o.src || 'PEMEX well files and CNH monthly records; Tonalli operations logs and daily production; events.json and wells.json in data/processed/presentation.'} Zero months are CNH-reported zeros or documented shut-ins; hatched = no monthly record exists.</div><div class="pg"></div>`;
        const ser = wellSeries(D, o.series || o.well);
        const x0 = ymd(o.x0 || (W.spud || '1956').slice(0, 7)), x1 = ymd(o.x1 || '2027-01');
        const hasProd = ser.oil.length > 0;
        const ch = hasProd ? timeChart($('#wChart', el), { W: 740, H: 240, m: { l: 70, r: 64, t: 10, b: 40 }, right: true, x: [x0, x1], yl: [0, o.ymax || 600], yr: [0, 100], yticks: 4, xticks: 6, ylabel: 'bbl/d', yrlabel: 'water cut %',
          bands: (o.missing || []).map(([a, b, t, kind]) => kind === 'note' ? { from: ymd(a), to: ymd(b), opacity: 0.06, label: t, ly: 22, size: 16 } : { from: ymd(a), to: ymd(b), hatch: '#9aa6b2', opacity: 0, label: t, vertical: true, size: 16 }),
          series: [{ key: 'w', color: C.water, values: ser.water, type: 'area', opacity: 0.3, width: 2 }, { key: 'o', color: C.oil, values: ser.oil, type: 'area', opacity: 0.45, width: 2.6 },
            { key: 'c', color: WCUT, values: ser.wcut, axis: 'r', width: 2.2, alpha: 0.95 }] }) : null;
        if (hasProd) { const l = legend($('#wChart', el), [[C.oil, 'oil, bbl/d'], [C.water, 'water, bbl/d'], [WCUT, 'water cut, % (right; 3-month)', 'ln']]); l.style.fontSize = '18px'; }
        else $('#wChart', el).innerHTML = `<p style="font-size:24px;margin:6px 0 0">${o.noProd || 'Never produced.'}</p>`;
        const evEl = $('#wEv', el);
        const setT = t => {
          F.setWellStates(wellStates(ctx, t, { override: t > 2023.2 ? CURRENT : {} }));
          if (ch) { ch.revealTo(DT(t)); ch.cursor(DT(t)); }
          $('#wYear', el).textContent = Math.floor(t);
          const s = ctx.hist.at(t).wells[o.well] || {}; const st = t > 2023.2 && CURRENT[o.well] ? CURRENT[o.well].status : s.status;
          $('#wTick', el).innerHTML = `${o.well}: <b>${STATUS_LABEL[st] || '—'}</b>${s.cum_oil ? `<br>cumulative <b>${Math.round(s.cum_oil / 1000)}</b> kbbl in the record` : ''}`;
        };
        let T = ctx.hist.toT(W.spud || '1956-01') - 0.02;
        scene(ctx, { year: T, focus: o.focusWell || o.well, focusOpts: o.cam || { dist: 2500, az: -0.55, el: 0.32 }, highlight: o.well, surfaceOpacity: 0.6, shift: [-0.22, 0.02] });
        setT(T);
        return o.steps.map((st, i) => ({
          say: st.say,
          run: async f => {
            if (st.ev) evEl.insertAdjacentHTML('beforeend', `<div class="ev" style="animation:none"><span class="d">${st.ev[0]}</span><span class="t">${st.ev[1]}${st.ev[2] ? `<small>${st.ev[2]}</small>` : ''}</span></div>`);
            while (evEl.children.length > 3) evEl.removeChild(evEl.firstChild);
            if (st.cam) F.focusWell(st.cam.w || o.well, f ? 0 : 2000, st.cam);
            if (st.t != null) { const to = typeof st.t === 'string' ? ctx.hist.toT(st.t) : st.t; await animateClock(ctx, T, to, f ? 0 : Math.min(ctx.stepDuration * 0.9, 9000), setT); T = to; }
          }
        }));
      }
    };
  }

  P.w6 = wellSlide({ well: 'TEC-6', eyebrow: 'Well by well · 1', title: 'TEC-6: the field’s workhorse', ymax: 700, missing: [['1956-10', '1960-01', 'no monthly record']],
    facts: [['Completed', 'Oct 1956'], ['El Abra top', '−2,294 m'], ['Initial', '480–580 bbl/d'], ['Cumulative', '~900 kbbl']],
    src: 'TEC-6 informe final (1956), PEMEX production expediente and 1976 programme, CNH monthly 1966–2006 (1960–65 field record attributed to TEC-6), 2007 estado mecánico. ~388 kbbl of its total is a PEMEX wellfile allocation.',
    steps: [
      { say: 'Now the wells one at a time, starting with the biggest producer. TEC-6 was completed in October 1956, open hole at the bottom of its reef section, and flowed about five hundred barrels a day with three percent water.', ev: ['Oct 1956', 'Completed open hole at 2,336–2,338 mMD', '~480–580 bbl/d, 3.4 % water'], t: '1957-01' },
      { say: 'From 1957 it carried the field alone for fourteen years, at about a hundred barrels a day.', ev: ['1957–71', 'The only producer in the field'], t: '1971-08' },
      { say: 'In 1971 PEMEX squeezed the original interval and moved up to two thousand three hundred and twenty four metres, then in 1976 up again, to two thousand three hundred and fourteen. Each move bought a new peak, the second at nearly three hundred barrels a day in 1977.', ev: ['1971 · 1976', 'Moved up the column twice', 'Second peak 293 bbl/d, Aug 1977'], t: '1978-01' },
      { say: 'It produced until 2006 and was abandoned in 2007 with its casing parted at three hundred and fifty two metres. It sits beside the TEC-10 pad that TEC-12 will be drilled from, which is why anti-collision is in the programme. In all, about nine hundred thousand barrels.', ev: ['Apr 2007', 'Plugged and abandoned', 'Casing parted at 352 m; poor cement 45–2,000 m'], t: NOW }
    ] });
  P.w2 = wellSlide({ well: 'TEC-2', eyebrow: 'Well by well · 2', title: 'TEC-2: the discovery, still restorable', ymax: 500, missing: [['1956-06', '1957-04', 'no record'], ['2019-09', '2023-02', 'in TEC-10 stream', 'note']],
    facts: [['Completed', 'Jun 1956'], ['El Abra top', '−2,302 m'], ['Initial', '453 bbl/d'], ['Cumulative', '~371 kbbl']],
    src: 'TEC-2 Forma 19 reports (1955–56), 1971 workover programme, CNH monthly 1972–2016, IHS 2018 well test, Tonalli operations log, GLJ YE2022–25. tec10_tec2_status.md.',
    steps: [
      { say: 'TEC-2 discovered the field. Its first test, at the very top of El Abra, flowed gas-rich oil: evidence of a small gas cap at the crest in 1956. It was completed lower down, at four hundred and fifty three barrels a day.', ev: ['May–Jun 1956', 'Discovery: top test gas-rich; 453 bbl/d from 2,335–2,339 mMD'], t: '1956-09' },
      { say: 'Nine months later salt water arrived and it was shut in for fifteen years. In December 1971 it was recompleted thirty metres higher and produced from that interval until 2016: three hundred and twenty thousand barrels.', ev: ['Mar 1957', 'Shut in for salt water'], t: '1972-04' },
      { say: 'In 2018 Tonalli found the tubing full of paraffin. The well test showed a skin of plus one hundred and ninety six: the well is badly damaged near the wellbore, not depleted. A plug in 2019 shut off the wet deeper perforations.', ev: ['1972–2016', 'Produced 320 kbbl from 2,307–2,311 mMD'], t: '2016-02' },
      { say: 'Its last production was sixteen barrels a day in January 2023, after a December workover. It is a low-rate, intermittent well, cycled on and off to let the water cone settle. It pays when it shares costs with TEC-10, and GLJ carries it as non-producing with a small workover.', ev: ['2018–23', 'Paraffin clean-out; skin +196; 16–50 bbl/d at 75–90 % water', 'Restorable: intermittent, sharing TEC-10’s costs'], t: NOW }
    ] });
  P.w7 = wellSlide({ well: 'TEC-7', eyebrow: 'Well by well · 3', title: 'TEC-7: oil at the top in 1957, water injector now', ymax: 600, missing: [['1957-01', '1957-04', 'no record']],
    facts: [['Completed', 'Jan 1957'], ['El Abra top', '−2,304 m'], ['Initial', '560 bbl/d'], ['Cumulative', '~293 kbbl']],
    src: 'TEC-7 expediente de perforación (215 pp., read Oct 2026), 1971 schematic, CNH monthly, ASEA authorisation 1712/2019, Tonalli 2019 operations log · tec7_expediente_findings.md.',
    steps: [
      { say: 'TEC-7 tested five hundred and sixty barrels a day in January 1957. Its electric log, run before any production, is the best evidence we have about the top of the reef: the top seven metres at thirteen percent water saturation and seventeen percent porosity.', ev: ['Jan 1957', 'Tested 560 bbl/d; 1957 E-log: top 7 m Sw 0.13, φ 0.17'], t: '1957-02' },
      { say: 'It watered out in seven weeks from its low completion and was shut in until 1971.', ev: ['Mar 1957', 'Shut in for salt water after 7 weeks'], t: '1971-09' },
      { say: 'Recompleted twenty five metres higher in October 1971, it came back at nearly five hundred barrels a day and was the biggest contributor to the 1972 peak. It produced until 1990, then briefly in 2006.', ev: ['Oct 1971', 'Recompleted 25 m higher: 478 bbl/d', 'Largest share of the 1972 peak'], t: '2007-01' },
      { say: 'In 2019 Tonalli reopened it and got only water, a hundred and eighty two barrels a day, probably through bad cement to the old perforations. It became the field’s water-injection well, which is what cut the operating cost by two thirds.', ev: ['2019', 'Reopened: 182 bbl/d water', 'Converted to the produced-water injector, Aug 2019'], t: NOW }
    ] });
  P.w9 = wellSlide({ well: 'TEC-9', eyebrow: 'Well by well · 4', title: 'TEC-9: 353 kbbl from one interval, its top never perforated', ymax: 300,
    facts: [['Completed', 'May 1973'], ['El Abra top', '−2,296 m'], ['Producing', '1973–2012'], ['Cumulative', '353 kbbl']],
    src: 'TEC-9 estado mecánico, 1973 resistivity–sonic–neutron logs, CNH monthly 1973–2012, PEMEX 2012 workover records · docs/19 G-62. Directional survey CSV (205 m N displacement; PEMEX diagram 112 m).',
    steps: [
      { say: 'TEC-9 was drilled in 1973 as a deviated well onto the southern high, a hundred and eighteen metres from the TEC-12 bottom hole.', ev: ['May 1973', 'Completed at 2,328–2,333 mMD'], t: '1974-01' },
      { say: 'From one interval it made three hundred and fifty three thousand barrels over almost forty years. Its 1973 logs show the top eight metres of the reef porous, at about fifteen percent, and at the same saturation as the producing interval. PEMEX cemented that top unit behind casing and never perforated it.', ev: ['1973–99', 'One interval, steady decline', 'Top 8 m: φ ~15 %, never perforated'], t: '1999-01' },
      { say: 'In 2012, at ten barrels a day, PEMEX ran solvent and three cubic metres of acid and the rate jumped to a hundred and two barrels a day. That is near-wellbore damage, not depletion, the same story as TEC-2 and TEC-10.', ev: ['2012', 'Solvent + acid: 10 → 102 bbl/d'], t: '2012-08' },
      { say: 'A workover that November failed, and the well was plugged in January 2013. Its unperforated top is TEC-12’s best analogue.', ev: ['Jan 2013', 'Plugged after a failed workover'], t: NOW }
    ] });
  P.wedge = wellSlide({ well: 'TEC-3', eyebrow: 'Well by well · 5', title: 'TEC-3, TEC-5 and TEC-101 define the edges', series: '__none', noProd: 'None of the three produced. They found the reef low and wet, and between them they place the oil–water contact and the flanks.',
    facts: [['TEC-3', '−2,373 m'], ['TEC-5', '−2,551 m'], ['TEC-101', '−2,334 m']],
    src: 'TEC-3 production expediente (DST, 1956), TEC-5 informe final and plugging programme (1956), TEC-101 logs and estado mecánico (1972) · cnh_findings.md §4, G-61, G-76.',
    steps: [
      { say: 'Three wells never produced, and they matter because they define the edges. TEC-3, the very first well, found the reef at minus two thousand three hundred and seventy three metres on the north-east flank. Its drill-stem test recovered oil over salt water: that is the lowest known oil in the field, minus two thousand three hundred and seventy four.', ev: ['Mar 1956', 'TEC-3: oil over salt water on test', 'Lowest known oil −2,374 m'], t: '1956-04' },
      { say: 'TEC-5, a kilometre and a half to the north-west, found the reef two hundred and fifty metres lower, off the structure.', ev: ['Jul 1956', 'TEC-5: reef at −2,551 m, off structure'], t: '1956-08', cam: { w: 'TEC-5', dist: 2600, az: -0.9, el: 0.35 } },
      { say: 'TEC-101 in 1972 found the west flank water-invaded at minus two thousand three hundred and thirty four, with the same low-resistivity marl above the reef that TEC-10 later found. All three are plugged.', ev: ['Mar 1972', 'TEC-101: west flank, water-invaded', 'Marl above the reef, as at TEC-10'], t: NOW, cam: { w: 'TEC-101', dist: 2000, az: -0.7, el: 0.3 } }
    ] });
  P.w10 = wellSlide({ well: 'TEC-10', eyebrow: 'Well by well · 6', title: 'TEC-10: proof the column is still there', ymax: 300, x0: '2018-01', missing: [['2019-12', '2023-01', 'commingled field stream (TEC-2 in 2020)', 'note']],
    facts: [['Drilled', 'Apr–May 2018'], ['El Abra top', '−2,310 m'], ['Initial', '194 bbl/d'], ['Cumulative', '~77 kbbl']],
    src: 'Weatherford logs and Stratascan core (2018), IHS PTA, TEC-10 daily production Sep 2018–Nov 2019, commingled sales 2019–22 (shown as TEC-10, the main or sole source per CNH filings), GLJ YE2022–25 · tec10_tec2_status.md.',
    steps: [
      { say: 'TEC-10 is Tonalli’s well, drilled in 2018 from the TEC-6 pad to the south-west. It was cored, fully logged, and tested in three zones. The deeper two gave no oil. The top zone, just below the reef top, flowed a hundred and ninety four barrels a day after stimulation.', ev: ['Apr–Aug 2018', 'Drilled, cored, logged; zone C 194 bbl/d', 'Build-up: 24.14 MPa, aquifer boundary 195 m away'], t: '2018-09' },
      { say: 'It peaked at two hundred and thirty two barrels a day in October 2018 and declined to seventy seven within a year, with water cut rising from forty to two thirds. Wax was dropping out in the tubing, and four solvent jobs in 2019 kept it going.', ev: ['2018–19', 'Peak day 232 bbl/d; 44 kbbl in 431 days', 'Four APSOL-AP solvent jobs in 2019'], t: '2020-01' },
      { say: 'By the end of 2021 it was making thirty four barrels a day at eighty six percent water. After the 2022 shut-in a twenty-thousand-dollar stimulation brought it back at about forty five barrels a day net, and it last produced in January 2023.', ev: ['2021–23', '34 bbl/d at 86 % water; restarted Nov 2022 at ~45 bbl/d'], t: '2023-02' },
      { say: 'The reservoir behind it was at full pressure in 2018, so the decline between treatments is wax and near-wellbore restriction. TEC-10 should come back at thirty to forty five barrels a day on a regular solvent or hot-oil schedule, which is how GLJ carries it, and that is the base the incremental TEC-12 economics stand on.', ev: ['Today', 'Shut in, restorable', 'Solvent / hot-oil schedule; GLJ PDNP with a 15 k$ workover'], t: NOW }
    ] });

  // ---------------------------------------------------------------- TEC-11: the concept (schematic)
  P.t11a = {
    id: 'tec11-concept', title: 'TEC-11: the concept', section: 'Well by well',
    build(el) {
      const body = std(el, { eyebrow: 'Well by well · 7 · TEC-11DES, 2018–19', title: 'The idea: a long lateral at the top of the oil, far from the water', src: 'Concept from the Jan 2019 operator deck and Kevin’s description (docs/18 A5); horizontal productivity screening by Babu–Odeh (HWrates). Schematic, not to scale.' });
      body.innerHTML = `<div class="row" style="gap:40px"><div id="t11c" style="width:1100px;height:640px"></div><div class="col grow" style="gap:24px">
        ${S(0, `<h3>Vertical wells cone</h3><p>Every Tecolutla vertical drew water up into a cone round the perforations and watered out, often within months.</p>`)}
        ${S(1, `<h3>A horizontal spreads the drawdown</h3><p>720 m of hole at the top of the column, completed open hole, produces the same rate at a fraction of the drawdown, so the water arrives later.</p>`)}
        ${S(2, `<h3>What it was meant to prove</h3><p>That horizontals work here. The Jan 2019 plan carried TEC-11, 12 and 13 as horizontals at <b>694 bbl/d each</b>, against TEC-10's 149.</p>`)}
        ${S(3, `<p style="color:var(--accent2)"><b>That concept has never been tested.</b> The next slide shows why.</p>`)}</div></div>`;
      const W = 1100, Hh = 640, svg = d3.select('#t11c', el).append('svg').attr('viewBox', `0 0 ${W} ${Hh}`).attr('width', W).attr('height', Hh).style('font-family', 'IBM Plex Sans, sans-serif');
      const reefTop = x => 200 + 50 * Math.pow((x - 560) / 560, 2) * 1.6;   // a gentle dome
      const owc = 470;
      svg.append('rect').attr('width', W).attr('height', Hh).attr('fill', '#0f151c');
      svg.append('path').attr('d', d3.area().x(d => d).y0(0).y1(d => reefTop(d))(d3.range(0, W + 1, 10))).attr('fill', '#5a4a33');
      svg.append('path').attr('d', d3.area().x(d => d).y0(d => reefTop(d)).y1(owc)(d3.range(0, W + 1, 10))).attr('fill', '#2f5f3a');
      svg.append('rect').attr('y', owc).attr('width', W).attr('height', Hh - owc).attr('fill', '#1f4f7d');
      svg.append('text').attr('x', 20).attr('y', 40).attr('fill', '#e9dcc0').style('font-size', '22px').text('Tantoyuca marl');
      svg.append('text').attr('x', 20).attr('y', 300).attr('fill', '#cfe8c9').style('font-size', '22px').text('El Abra, oil column');
      svg.append('text').attr('x', 20).attr('y', owc + 50).attr('fill', '#cfe3ff').style('font-size', '22px').text('Aquifer (bottom water)');
      // vertical well with cone
      const vg = svg.append('g').attr('opacity', 0);
      vg.append('line').attr('x1', 250).attr('x2', 250).attr('y1', 0).attr('y2', 330).attr('stroke', '#fff').attr('stroke-width', 6);
      vg.append('rect').attr('x', 240).attr('y', 300).attr('width', 20).attr('height', 26).attr('fill', '#ff7a2f');
      const cone = vg.append('path').attr('d', `M120,${owc} Q250,${owc} 250,${owc}  Q250,${owc} 380,${owc}Z`).attr('fill', '#1f4f7d');
      vg.append('text').attr('x', 250).attr('y', Hh - 30).attr('text-anchor', 'middle').attr('fill', '#fff').style('font-size', '21px').text('vertical: water cones up');
      // horizontal
      const hg = svg.append('g').attr('opacity', 0);
      const path = `M620,0 L620,120 Q620,${reefTop(700) + 18} 720,${reefTop(720) + 18} L1060,${reefTop(1060) + 18}`;
      const hp = hg.append('path').attr('d', path).attr('fill', 'none').attr('stroke', '#ffcf3a').attr('stroke-width', 7);
      const hcone = hg.append('path').attr('d', `M700,${owc} L1080,${owc} L1080,${owc} L700,${owc}Z`).attr('fill', '#1f4f7d');
      hg.append('text').attr('x', 880).attr('y', Hh - 30).attr('text-anchor', 'middle').attr('fill', '#fff').style('font-size', '21px').text('horizontal: low drawdown, flat water rise');
      return [
        { say: 'TEC-11 is the well people remember, so it deserves a careful explanation. Start with the problem it was meant to solve. Every vertical well in this field drew the bottom water up into a cone around its perforations and watered out.', run: f => { vg.transition().duration(f ? 0 : 700).attr('opacity', 1); cone.transition().delay(f ? 0 : 700).duration(f ? 0 : 2500).attr('d', `M120,${owc} Q250,${owc} 250,340 Q250,${owc} 380,${owc}Z`); } },
        { say: 'A horizontal well at the top of the column spreads the same production along seven hundred metres of hole. Drawdown at any point is small, so the water rises slowly and evenly instead of coning.', run: f => { hg.transition().duration(f ? 0 : 700).attr('opacity', 1); const L = hp.node().getTotalLength(); hp.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', f ? 0 : L).transition().duration(f ? 0 : 2600).attr('stroke-dashoffset', 0); hcone.transition().delay(f ? 0 : 2400).duration(f ? 0 : 1800).attr('d', `M700,${owc} L1080,${owc} L1080,${owc - 22} L700,${owc - 22}Z`); } },
        { say: 'If it worked, it would change the field: the January 2019 plan carried three horizontals at six hundred and ninety four barrels a day each, against a hundred and fifty for TEC-10.' },
        { say: 'The important point for TEC-12 is that this concept was never actually tested. Here is what happened.' }
      ];
    }
  };

  // ---------------------------------------------------------------- TEC-11: what happened, along hole
  P.t11b = {
    id: 'tec11-failures', title: 'TEC-11: what went wrong', section: 'Well by well',
    build(el) {
      const body = std(el, { eyebrow: 'Well by well · 8 · TEC-11DES, 2018–19', title: 'A chain of failures, and a lateral that probably stayed in the marl', src: 'Directional survey; Jan 2019 depth grid along hole (tec11_vs_grid.csv); recorded LWD sonic (TEC11_logs_mss.csv; marl ~71 µs/ft at TEC-10, El Abra 52–57); Tonalli final schematic (Sep 2019), Halliburton reports, cost summary; Tantoyuca test log “Tantoyuca Seguimiento Tec #11 apertura.xlsx” (28 Aug–2 Sep 2019) and Jaguar discussion deck (Sep 2022) · tec11_story.md, G-64, G-75.' });
      body.innerHTML = `<div id="t11h"></div><div class="row" style="gap:30px;align-items:flex-start"><div class="evlist grow" id="t11ev" style="display:grid;grid-template-columns:1fr 1fr;gap:12px 40px"></div>
        <div class="card" style="width:430px">${S(7, `<div class="kpi"><div class="v">4.40<small>MM</small></div><div class="l">all-in, against a 3.93 MM budget; 0.96 MM of completion invoices of unknown status</div></div>`)}</div></div>`;
      const G = D.tec11_grid.filter(r => r.mMD >= 2250), L = D.tec11_logs.filter(r => r.md >= 2250);
      const Wc = 1700, Hc = 330, m = { l: 96, r: 30, t: 20, b: 50 };
      const svg = d3.select('#t11h', el).append('svg').attr('viewBox', `0 0 ${Wc} ${Hc}`).attr('width', Wc).attr('height', Hc).style('font-family', 'IBM Plex Sans, sans-serif');
      const x = d3.scaleLinear().domain([2250, 3300]).range([m.l, Wc - m.r]), y = d3.scaleLinear().domain([2225, 2345]).range([m.t, Hc - m.b]);
      const ax = svg.append('g').attr('transform', `translate(0,${Hc - m.b})`).call(d3.axisBottom(x).ticks(11).tickFormat(d3.format(','))); const ay = svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6).tickFormat(d => '−' + d3.format(',')(d)));
      [ax, ay].forEach(a => { a.selectAll('text').attr('fill', C.ink2).style('font-size', '19px'); a.selectAll('line,path').attr('stroke', C.grid); });
      svg.append('text').attr('x', Wc / 2).attr('y', Hc - 8).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '19px').text('Measured depth along the hole, m');
      svg.append('text').attr('x', 24).attr('y', (Hc) / 2).attr('transform', `rotate(-90,24,${Hc / 2})`).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '19px').text('m below sea level');
      // El Abra top from the grid, reef below shaded
      svg.append('path').attr('d', d3.area().x(r => x(r.mMD)).y0(Hc - m.b).y1(r => y(r.grid_mss))(G)).attr('fill', '#2f6d9a').attr('opacity', 0.35);
      svg.append('path').attr('d', d3.line().x(r => x(r.mMD)).y(r => y(r.grid_mss))(G)).attr('fill', 'none').attr('stroke', '#7fc3ff').attr('stroke-width', 3).attr('stroke-dasharray', '9 6');
      svg.append('text').attr('x', x(3000)).attr('y', y(2338)).attr('fill', '#cfe3ff').style('font-size', '20px').text('El Abra below the mapped top (Jan 2019 grid)');
      // path coloured by sonic: marl-like (>=65) tan, reef-like (<60) blue
      const segs = svg.append('g');
      for (let i = 0; i + 1 < L.length; i++) { const a = L[i], b = L[i + 1]; const c = a.dtc >= 65 ? '#d9b98a' : a.dtc < 60 ? '#7fc3ff' : '#c9c9c9'; segs.append('line').attr('x1', x(a.md)).attr('y1', y(a.mss)).attr('x2', x(b.md)).attr('y2', y(b.mss)).attr('stroke', c).attr('stroke-width', 8).attr('stroke-linecap', 'round'); }
      const lg = svg.append('g').attr('transform', `translate(${m.l + 20},${Hc - m.b - 14})`);
      [['#d9b98a', 'well path, sonic ≥ 65 µs/ft (marl-like)'], ['#7fc3ff', 'sonic < 60 µs/ft (reef-like)']].forEach(([c, t], i) => { lg.append('rect').attr('x', i * 440).attr('width', 30).attr('height', 10).attr('y', -6).attr('fill', c); lg.append('text').attr('x', i * 440 + 40).attr('y', 4).text(t).attr('fill', C.ink).style('font-size', '19px'); });
      const marks = svg.append('g');
      const mark = (md, txt, col, dy = 0, span) => { const g = marks.append('g').attr('opacity', 0); const yy = y(2240 + dy); if (span) g.append('rect').attr('x', x(span[0])).attr('width', x(span[1]) - x(span[0])).attr('y', m.t).attr('height', Hc - m.b - m.t).attr('fill', col).attr('opacity', 0.16); g.append('line').attr('x1', x(md)).attr('x2', x(md)).attr('y1', m.t).attr('y2', Hc - m.b).attr('stroke', col).attr('stroke-width', 2.5).attr('stroke-dasharray', '5 5'); g.append('text').attr('x', x(md) + 8).attr('y', yy).text(txt).attr('fill', col).style('font-size', '19px').attr('font-weight', 600).attr('paint-order', 'stroke').attr('stroke', '#0f151c').attr('stroke-width', 5); return g; };
      const M = [mark(2354.4, '7 in shoe, 61.6°', '#e8e2d6', 0), mark(2563, 'lateral starts', '#e8e2d6', 8), mark(2866, 'fish 2,866–2,872 · liner ends 2,863', '#ff8f87', 0, [2872, 3283]), mark(2643.5, '5 perfs 2,643–2,746, acid unisolated', '#ffb38a', 16, [2643.5, 2745.5]), mark(2400, 'plug ~2,400 (Aug 2019)', '#c9b6ff', 24), mark(2361, 'Tantoyuca 2,361–2,364: water', '#f2c14e', 40, [2361, 2364])];
      const ev = $('#t11ev', el);
      const add = (d, t, s) => { ev.insertAdjacentHTML('beforeend', `<div class="ev"><span class="d">${d}</span><span class="t" style="font-size:22px">${t}${s ? `<small>${s}</small>` : ''}</span></div>`); while (ev.children.length > 4) ev.removeChild(ev.firstChild); };
      return [
        { say: 'This is TEC-11 along its length. The horizontal axis is measured depth along the hole, the vertical is depth below sea level. The dashed blue line is the top of El Abra from the 2019 grid along the well path, and the coloured line is the well itself.' },
        { say: 'Colour comes from the sonic log recorded while drilling. Tan is marl-like, blue is reef-like. Almost the whole lateral reads like the marl, seventy three microseconds per foot, and it ran four to ten metres above the mapped reef top. No resistivity was run to check, so this is an interpretation, but the sonic, the grid and the tops table agree. The lateral probably never got into the reef it was aimed at.', run: f => { M[0].transition().duration(f ? 0 : 600).attr('opacity', 1); M[1].transition().duration(f ? 0 : 600).attr('opacity', 1); add('Nov–Dec 2018', 'No pilot hole, no resistivity; steering below plan, hole collapse', 'Casing set at 61.6°; TD 3,283 m on 18 Dec 2018'); } },
        { say: 'Then the completion went wrong in sequence. The liner hanger was damaged and the tie-back failed. In May 2019 a bit and mill were lost in the hole at two thousand eight hundred and sixty six metres, cutting off the last four hundred metres of open hole.', run: f => { M[2].transition().duration(f ? 0 : 600).attr('opacity', 1); add('May 2019', 'Fish at 2,866–2,872 m; 411 m of open hole lost'); } },
        { say: 'Because the selective tool could not pass the damaged hanger, five short intervals were perforated and acid was pumped from surface with no isolation. Pressure broke down at once: the acid most likely opened a fracture to the aquifer.', run: f => { M[3].transition().duration(f ? 0 : 600).attr('opacity', 1); add('Jun 2019', 'Five perforations; acid bull-headed, unisolated'); } },
        { say: 'The well then made two hundred and sixty to two hundred and eighty six barrels a day of water with traces of oil. In August the lateral was plugged off.', run: f => { M[4].transition().duration(f ? 0 : 600).attr('opacity', 1); add('Jul–Aug 2019', 'El Abra: 260–286 bbl/d water, no oil', 'composite plug at ~2,400 m, 11–12 Aug'); } },
        { say: 'A question that comes up: why not produce the Tantoyuca instead? It was tested above the plug at the end of August 2019, perforated at two thousand three hundred and sixty one to two thousand three hundred and sixty four metres. In four and a half days on a fourteen sixty-fourths choke it flowed only water, a hundred and ninety two barrels a day at first and ninety six at the end, five hundred and twenty eight barrels in all, with no measurable oil. Only a trace of heavy, seventeen-degree oil was sampled. The Tantoyuca here is a tight marl, three to six ohm-metres with no fractures; there is no stabilised oil rate to report because there was none.', run: f => { M[5].transition().duration(f ? 0 : 600).attr('opacity', 1); add('28 Aug – 2 Sep 2019', 'Tantoyuca test: 0 bbl/d oil (trace, 17 °API); 192 → 96 bbl/d water', '14/64 in choke, ~170 psi; 528 bbl water in 4.5 days'); } },
        { say: 'So TEC-11 tested how fast the aquifer reaches a well through acidised fractures. It did not test a horizontal in reservoir rock. The lessons are built into TEC-12: a conventional well, a full log suite before completion, perforation on the data, and no unisolated acid near the water.', run: () => add('Lessons → TEC-12', 'Conventional S-well; log before completing; no unisolated acid') },
        { say: 'All in, it cost four point four million dollars against a three point nine million budget, including about a million of completion invoices whose status is still unresolved.' }
      ];
    }
  };

  // ================================================================ field production performance
  P.performance = {
    id: 'performance', title: 'Production performance', section: 'Reservoir',
    build(el) {
      const body = std(el, { eyebrow: 'Production performance', title: 'Five producers, 1.94–1.98 MMbbl, every one limited by water', src: 'Monthly records (production_by_well.csv; one source per well-month): CNH 1966–2016, field-level 1960–65 (attributed to TEC-6), Tonalli 2018–22. Cumulative per well: By Zone allocation (Mar 2020) and GLJ for TEC-10. Zero months are CNH-reported zeros (G-34) or documented shut-ins. Hatched 1956–59: no monthly record of any kind; those years exist only as PEMEX wellfile allocations.' });
      body.innerHTML = `<div id="pf"></div><div class="row" style="gap:50px;align-items:flex-start"><div style="width:860px">${S(1, `<div id="pfc"></div>`)}</div>
        <div class="col grow" style="gap:20px">${S(2, `<p><b>Water, not pressure, ended every well.</b> Each producer was moved up the column as the water arrived; pressure never fell.</p>`)}${S(3, `<p><b>Damage, not depletion, explains the late decline:</b> wax, scale and skin; cheap solvent and acid jobs restored TEC-9 in 2012 and TEC-10 in 2019–22.</p>`)}</div></div>`;
      const R = rateMatrix(D);
      const ch = timeChart($('#pf', el), { W: 1700, H: 330, m: { l: 90, r: 30, t: 20, b: 44 }, x: [ymd('1956-01'), ymd('2023-06')], yl: [0, 1000], yticks: 5, xticks: 14, ylabel: 'Oil, bbl/d (monthly)', bands: [{ from: ymd('1956-06'), to: ymd('1960-01'), hatch: '#9aa6b2', opacity: 0, label: 'no monthly record', vertical: true, size: 18 }],
        stack: WELLS_P.map(w => ({ key: w, color: C.wells[w], values: R.M[w] })), stackDates: R.dates,
        events: [{ d: ymd('1972-03'), text: '932 bbl/d, Mar 1972', y: 0.04 }, { d: ymd('1999-02'), text: '1999–2003 field shut in', y: 0.3 }, { d: ymd('2018-09'), text: 'TEC-10', y: 0.3, left: true }] });
      legend($('#pf', el), WELLS_P.map(w => [C.wells[w], w]));
      const cum = [['TEC-6', 899785, 'incl. ~388 kbbl wellfile allocation 1956–65'], ['TEC-2', 371177], ['TEC-9', 352601], ['TEC-7', 293001], ['TEC-10', 77100]];
      const b = hbars($('#pfc', el), cum.map(([w, v]) => ({ label: w, value: v / 1000, color: C.wells[w], text: d3.format(',')(Math.round(v / 1000)) + ' kbbl' })), { W: 860, rowH: 40, labelW: 140, max: 1000, ticks: 5, m: { r: 160 } });
      return [
        { say: 'Here is the whole production record, by well, as a monthly rate. One caveat first: there is no monthly record at all for 1956 to 1959, the hatched band. Those years survive only as PEMEX wellfile allocations, so the chart starts in 1960. From 1960 to 1965 there is a single field-level record, which is TEC-6, the only producer at the time. Where the rate drops to zero, the well was reported shut in.', run: f => ch.revealTo(ymd('1971-06'), f ? 0 : 3000) },
        { say: 'Five wells produced oil. TEC-6 made about nine hundred thousand barrels, TEC-2 and TEC-9 about three hundred and fifty thousand each, TEC-7 about three hundred thousand, and TEC-10, in four years, seventy seven thousand. The peak was nine hundred and thirty two barrels a day in March 1972, from three wells right after their recompletions.', run: f => { ch.revealTo(ymd('2000-01'), f ? 0 : 3200); b.show(f); } },
        { say: 'The pattern is the same in every well: strong initial rates, water arriving from below, a recompletion higher up, and a new peak. Water ended each well. Pressure never did.', run: f => ch.revealAll(f ? 0 : 3200) },
        { say: 'And late in life the decline is damage, not depletion. Wax and skin choke the wells, and cheap solvent and acid jobs brought TEC-9 back in 2012 and kept TEC-10 going. That matters for running the field, and for TEC-12.' }
      ];
    }
  };

  // ================================================================ current state, Oct 2026
  P.current = {
    id: 'current', kind: '3d', title: 'The field today', section: 'Operations',
    build(el) {
      const rows = [['TEC-10', 'Shut in since Jan 2023 · <b>restorable</b> at ~30–45 bbl/d on a solvent / hot-oil schedule (GLJ: PDNP, 15 k$ workover)', 'tag-ok'], ['TEC-2', 'Shut in · <b>intermittent</b> producer, 16–23 bbl/d at 75–80 % water, worth running only with TEC-10', 'tag-ok'], ['TEC-7', 'Produced-water injector since Aug 2019; current wellhead state to confirm (G-57)', 'tag-blue'], ['TEC-11', 'Temporarily abandoned; composite plug ~2,400 mMD', 'tag-grey'], ['TEC-6, 9', 'Plugged 2007 and 2013', 'tag-grey'], ['TEC-3, 5, 101', 'Dry, plugged 1956–72', 'tag-grey'], ['TEC-12', 'Planned from the TEC-10 pad; GLJ schedules first oil Jul 2028', 'tag-warn']];
      el.innerHTML = `<div class="glass" style="position:absolute;right:70px;top:56px;width:880px;padding:26px 32px">
        <div class="eyebrow">Operations · October 2026</div><h2 style="font-size:50px;margin-top:8px">The field today</h2>
        <table class="st" style="margin-top:18px;font-size:23px">${rows.map((r, i) => `<tr data-step="${i < 2 ? 1 : i < 6 ? 2 : 3}"><td style="white-space:nowrap"><span class="pill ${r[2]}">${r[0]}</span></td><td>${r[1]}</td></tr>`).join('')}</table></div>
        <div class="src">tec10_tec2_status.md; wells.json status_now; GLJ YE2024–25 (PDNP restarts); docs/gaps.md G-57, G-65. Restart rates are interpretation from the last steady periods, not tests.</div><div class="pg"></div>`;
      scene(ctx, { year: NOW, view: 'crest', override: CURRENT, surfaceOpacity: 0.8, shift: [-0.24, 0] });
      return [
        { say: 'So where does the field stand today? Nothing is producing. But two wells can come back.', run: f => F.view('crest', f ? 0 : 2200) },
        { say: 'TEC-10 is restorable. Its last steady rates were thirty to forty five barrels a day at seventy to eighty six percent water, and the reservoir behind it is at full pressure. It needs a solvent or hot-oil clean-up at restart and then a regular treatment schedule for wax, which is how it was run in 2019. TEC-2 can produce intermittently at sixteen to twenty three barrels a day alongside it.', run: f => F.focusWell('TEC-10', f ? 0 : 2200, { dist: 1500, az: -0.4, el: 0.3 }) },
        { say: 'TEC-7 remains the disposal well, and the rest are plugged or temporarily abandoned.', run: f => F.view('overview', f ? 0 : 2200) },
        { say: 'And TEC-12 is planned from the same pad as TEC-10, which means it shares the battery, the flowline and the disposal well. That is what makes it pay.', run: f => F.focusWell('TEC-12', f ? 0 : 2200, { dist: 1600, az: 0.5, el: 0.3 }) }
      ];
    }
  };
  return P;
}
