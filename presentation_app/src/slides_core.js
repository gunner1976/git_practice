// ---------------------------------------------------------------- slide helpers and the geology, reservoir, cost and economics slides
import { h, $, $$, countUp } from './engine.js';
import { C, fmt, timeChart, hbars, vstack, waterfall, donut, histogram, tornado, logTracks, structureMap, legend } from './charts.js';
import { STATUS_LABEL, RAMP_CSS } from './field3d.js';

const d3 = window.d3;
export const DT = t => { const y = Math.floor(t), m = Math.round((t - y) * 12); return new Date(Date.UTC(y, m, 1)); };
export const ymd = s => { const p = String(s).split('-').map(Number); return new Date(Date.UTC(p[0], (p[1] || 1) - 1, p[2] || 1)); };
export const rampI = d3.interpolateRgbBasis(RAMP_CSS);

// standard content slide: eyebrow, title, body; returns the body element
export function std(el, o) {
  el.innerHTML = `<div class="eyebrow">${o.eyebrow || ''}</div><h2>${o.title}</h2><div class="body grow" style="display:flex;flex-direction:column;gap:28px;min-height:0"></div>` +
    (o.src ? `<div class="src">${o.src}</div>` : '') + `<div class="pg"></div>`;
  return el.querySelector('.body');
}
export const S = (n, html, cls = '') => `<div data-step="${n}" class="${cls}">${html}</div>`;

// 3-D scene state for a slide
export function wellStates(ctx, year, { captions = true, override = {} } = {}) {
  const ws = ctx.hist.at(year).wells;
  for (const [k, s] of Object.entries(ws)) { Object.assign(s, override[k] || {}); s.caption = captions && s.status && s.status !== 'none' ? (STATUS_LABEL[s.status] || s.status) : ''; }
  return ws;
}
export function scene(ctx, o = {}) {
  const f = ctx.field; f.labelsOn = o.labels !== false; f.showSurface(o.surface !== false, o.surfaceOpacity ?? 0.95);
  f.owc.visible = !!o.owc; f.setWellStates(wellStates(ctx, o.year ?? 2026.8, { captions: o.captions !== false, override: o.override || {} }));
  f.setFocusMode({ dim: !!o.dim, columns: o.columns !== false }); f.setHighlight(o.highlight || null); f.setTarget(o.target || null); f.setShift(...(o.shift || [0, 0]));
  f.setSlices(o.slices || null); f.setPads(o.pads || null, o.traces || []);
  if (o.focus) f.focusWell(o.focus, ctx.fast ? 0 : (o.dur ?? 2400), o.focusOpts || {}); else if (o.view) f.view(o.view, ctx.fast ? 0 : (o.dur ?? 2400));
  f.orbit(!!o.orbit, o.orbitSpeed ?? 0.25);
}

// ================================================================ slides
export function coreSlides(ctx) {
  const D = ctx.D, M = ctx.M, F = ctx.field;
  const P = {};

  // ---------------------------------------------------------------- cover (3-D)
  P.cover = {
    id: 'cover', kind: '3d', title: 'Tecolutla Field', section: 'Introduction',
    build(el) {
      el.innerHTML = `<div class="glass pe" style="position:absolute;left:110px;top:120px;width:1060px;padding:46px 54px">
        <div class="eyebrow">Contract Area 24 · Veracruz, Mexico</div>
        <h1 style="margin-top:18px">Tecolutla Field</h1>
        <p class="lead" style="margin-top:22px;font-family:var(--serif);font-size:40px;line-height:1.3">Sixty years on a Golden Lane reef, and the one place on its crest that has never been produced</p>
        <p style="margin-top:28px;font-size:26px">Technical presentation for Kinjal · October 2026 · Kevin Gunning, P.Eng.</p></div>
        <div class="src">Depths in metres below sea level (mSS) unless marked mMD · USD · 100 % working interest · 3-D: Jan 2019 El Abra depth grid, directional surveys, PEMEX well files</div><div class="pg"></div>`;
      scene(ctx, { year: 2026.8, view: 'surface', dur: 0, orbit: true, orbitSpeed: 0.35, captions: false, shift: [0.2, 0.04] });
      return [
        { say: 'This is the Tecolutla field: a small El Abra reef on the Golden Lane trend in northern Veracruz, discovered by PEMEX in 1956. What you are looking at is the top of the reef, mapped from the 2019 seismic grid and coloured from blue on the flanks to red at the crest, with every well drilled on it.' },
        { say: 'Over the next half hour we will walk through where the field sits, how it was found and produced well by well, what the reservoir and its fluids are, what it costs to run, and why one more well, TEC-12, at the crest is the opportunity. The presentation plays itself; you can pause, step back, or open the 3-D field and the data tables from the tabs at the top at any time.', run: f => F.view('overview', f ? 0 : 4000) }
      ];
    }
  };

  // ---------------------------------------------------------------- Golden Lane regional map
  P.goldenlane = {
    id: 'goldenlane', title: 'On the Golden Lane', section: 'Setting',
    build(el) {
      const body = std(el, { eyebrow: 'Setting', title: 'Tecolutla sits at the south-eastern tip of the Golden Lane reef rim', src: 'Coastline: Natural Earth 1:10 m. Reef-rim trace is schematic, after published regional maps (Faja de Oro / Tuxpan platform); town positions approximate. Field outline: CNH polygon. Sources: CNH dictamen A24 (2018), RES PEMEX field summary, geology notes. Cerro Azul No. 4: HGS Bulletin editor’s note (Sep 2015), Wikipedia “Cerro Azul, Veracruz”; rate is a blowout estimate, not metered. TM-01: CNH Ronda 2.3 results (2018), licence CNH-R02-L03-TM-01/2017; IFR “Round 2.3 TM-01 Block” deck (Feb 2018).' });
      body.innerHTML = `<div class="row" style="gap:40px;align-items:stretch">
        <div id="glmap" style="width:560px;height:640px;position:relative;flex:none"></div>
        <div class="col grow" style="gap:26px">
          ${S(1, `<h3>The Golden Lane (Faja de Oro)</h3><p>An Albian–Cenomanian reef round the Tuxpan platform: an atoll about 150 km by 70 km. Its rim is a chain of separate fields, each a reef block sealed by Tertiary shale, from Cerro Azul onshore to the marine fields.</p>`)}
          ${S(3, `<h3>Where Tecolutla fits</h3><p>The field is on the onshore reef rim at its south-eastern end, about 60 km east-south-east of Poza Rica and 7 km from the coast. CNH play: <b>El Abra · reef rim · onshore</b>. Tecolutla was licensed in Ronda 1.3 (2016); the adjacent <b>TM-01</b> block, went in Ronda 2.3 (2018) to Jaguar E&amp;P on a USD 26.1 MM tie-break bonus. IFR’s bid deck mapped its El Abra pools: Miguel Hidalgo, Vicente Guerrero, Gutiérrez Zamora.</p>`)}
          ${S(4, `<div class="kpis" style="grid-template-columns:repeat(3,1fr)"><div class="kpi"><div class="v">45</div><div class="l">El Abra fields in the CNH trend table (35 on the reef rim)</div></div><div class="kpi"><div class="v">31<small>%</small></div><div class="l">Median 3P recovery for reef-rim fields</div></div><div class="kpi hot"><div class="v">2.5<small>MMbbl/km²</small></div><div class="l">Tecolutla's oil in place per km², against a rim median of 8.3: a small, thin field</div></div></div>`)}
        </div></div>`;
      const W = 560, Hh = 640, lon0 = -98.2, lon1 = -96.6, lat0 = 20.15, lat1 = 22.05;
      const kx = Math.cos(21.1 * Math.PI / 180), sx = d3.scaleLinear().domain([lon0, lon1]).range([0, W]), sy = d3.scaleLinear().domain([lat0, lat1]).range([Hh, 0]);
      const svg = d3.select('#glmap', el).append('svg').attr('viewBox', `0 0 ${W} ${Hh}`).attr('width', W).attr('height', Hh).style('font-family', 'IBM Plex Sans, sans-serif');
      svg.append('rect').attr('width', W).attr('height', Hh).attr('fill', '#10273a').attr('rx', 10);
      const coast = (D.coast || []).slice().sort((a, b) => b.length - a.length);
      if (coast.length) {
        let main = coast[0].slice(); if (main[0][1] < main[main.length - 1][1]) main.reverse();   // north -> south
        const land = [...main, [lon0 - 1, main[main.length - 1][1]], [lon0 - 1, lat0 - 1], [lon0 - 1, lat1 + 1], [lon0 - 1, main[0][1]]];
        svg.append('path').attr('d', d3.line()(land.map(p => [sx(p[0]), sy(p[1])])) + 'Z').attr('fill', '#1d2a22').attr('stroke', '#6f8a7a').attr('stroke-width', 1.5);
        coast.slice(1).forEach(s => svg.append('path').attr('d', d3.line()(s.map(p => [sx(p[0]), sy(p[1])]))).attr('fill', 'none').attr('stroke', '#6f8a7a').attr('stroke-width', 1.5));
      }
      // schematic rim (lat, lon)
      const rim = [[21.80, -97.55], [21.62, -97.72], [21.35, -97.70], [21.19, -97.74], [21.02, -97.70], [20.88, -97.64], [20.72, -97.50], [20.58, -97.33], [20.48, -97.14], [20.44, -97.01], [20.47, -96.90], [20.62, -96.88], [20.85, -96.97], [21.10, -97.07], [21.32, -97.15], [21.47, -97.22], [21.66, -97.36]];
      const rimLine = d3.line().curve(d3.curveCatmullRomClosed).x(p => sx(p[1])).y(p => sy(p[0]));
      const rimP = svg.append('path').attr('d', rimLine(rim)).attr('fill', 'rgba(232,137,79,0.06)').attr('stroke', '#e8894f').attr('stroke-width', 16).attr('stroke-opacity', 0.55).attr('stroke-linejoin', 'round');
      const L = rimP.node().getTotalLength(); rimP.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L);
      svg.append('text').attr('x', sx(-97.42)).attr('y', sy(21.3)).attr('text-anchor', 'middle').attr('fill', '#9fb3c3').style('font-size', '21px').style('font-style', 'italic').text('Tuxpan platform');
      svg.append('text').attr('x', sx(-97.42)).attr('y', sy(21.3) + 24).attr('text-anchor', 'middle').attr('fill', '#9fb3c3').style('font-size', '18px').text('(lagoon interior)');
      const towns = [['Tampico', 22.23, -97.86], ['Tuxpan', 20.96, -97.40], ['Poza Rica', 20.53, -97.46], ['Papantla', 20.45, -97.32], ['Cerro Azul', 21.19, -97.74], ['Naranjos', 21.35, -97.69], ['Álamo', 20.92, -97.68]];
      towns.forEach(([n, la, lo]) => { if (lo < lon0 || la > lat1) return; svg.append('circle').attr('cx', sx(lo)).attr('cy', sy(la)).attr('r', 5).attr('fill', '#d6dde4'); svg.append('text').attr('x', sx(lo) - 10).attr('y', sy(la) + 6).attr('text-anchor', 'end').attr('fill', '#d6dde4').style('font-size', '19px').text(n); });
      svg.append('text').attr('x', sx(-96.95)).attr('y', sy(21.55)).attr('fill', '#8fb0c8').style('font-size', '20px').style('font-style', 'italic').text('Gulf of Mexico');
      svg.append('text').attr('x', sx(-97.05)).attr('y', sy(21.2)).attr('fill', '#e8a37a').style('font-size', '18px').text('marine Golden Lane');
      const ca = svg.append('g').attr('opacity', 0), cax = sx(-97.74), cay = sy(21.19);
      ca.append('circle').attr('cx', cax).attr('cy', cay).attr('r', 11).attr('fill', '#ffcf3a').attr('stroke', '#fff').attr('stroke-width', 2.5);
      ca.append('circle').attr('class', 'pulse').attr('cx', cax).attr('cy', cay).attr('r', 26).attr('fill', 'none').attr('stroke', '#ffcf3a').attr('stroke-width', 2);
      ca.append('line').attr('x1', cax).attr('y1', cay - 12).attr('x2', 150).attr('y2', 182).attr('stroke', '#ffcf3a').attr('stroke-width', 2);
      ca.append('rect').attr('x', 14).attr('y', 22).attr('width', 330).attr('height', 160).attr('rx', 8).attr('fill', '#0b1620').attr('stroke', '#ffcf3a').attr('stroke-width', 1.5).attr('opacity', 0.94);
      [['Cerro Azul No. 4 · Feb 1916', 600, '#ffe08a'], ['Blew out at ~260,000 bbl/d', 400, '#fff'], ['(estimate); 9 days uncontrolled', 400, '#fff'], ['57+ MMbbl in 14 years', 400, '#fff'], ['~110 km NW of Tecolutla', 400, '#9fb3c3']]
        .forEach(([t, w, c], i) => ca.append('text').attr('x', 28).attr('y', 52 + i * 29).attr('fill', c).style('font-size', '20px').attr('font-weight', w).text(t));
      const tg = svg.append('g').attr('opacity', 0);
      tg.append('circle').attr('cx', sx(-97.009)).attr('cy', sy(20.449)).attr('r', 13).attr('fill', '#ff6a2a').attr('stroke', '#fff').attr('stroke-width', 3);
      tg.append('circle').attr('cx', sx(-97.009)).attr('cy', sy(20.449)).attr('r', 34).attr('fill', 'none').attr('stroke', '#ffb38a').attr('stroke-width', 2).attr('stroke-dasharray', '5 5');
      tg.append('text').attr('x', sx(-97.009) + 40).attr('y', sy(20.449) + 48).attr('fill', '#fff').style('font-size', '26px').attr('font-weight', 600).text('Tecolutla');
      svg.append('text').attr('x', 18).attr('y', Hh - 18).attr('fill', '#9aa6b2').style('font-size', '16px').text('0        25 km');
      svg.append('line').attr('x1', 18).attr('x2', 18 + (sx(lon0 + 25 / (111.32 * kx)) - sx(lon0))).attr('y1', Hh - 40).attr('y2', Hh - 40).attr('stroke', '#9aa6b2').attr('stroke-width', 3);
      return [
        { say: 'Start with the setting. In the Cretaceous, a reef grew round the edge of the Tuxpan platform: an atoll about a hundred and fifty kilometres long. That rim is the Golden Lane, the Faja de Oro, and it has given Mexico some of its most famous wells.', run: f => rimP.transition().duration(f ? 0 : 5000).ease(d3.easeCubicInOut).attr('stroke-dashoffset', 0) },
        { say: 'Uplift and erosion at the end of the Albian cut the rim into separate blocks, each a reef build-up sealed by Tertiary shale. Every Golden Lane field is one of those blocks.' },
        { say: 'The trend made its name early. Cerro Azul number four, about a hundred and ten kilometres north-west of here, blew out in February 1916 and flowed uncontrolled for nine days at an estimated two hundred and sixty thousand barrels a day, one of the largest wells ever drilled. It went on to make more than fifty seven million barrels in fourteen years. Same reef; very different scale.', run: f => ca.transition().duration(f ? 0 : 900).attr('opacity', 1) },
        { say: 'Tecolutla is at the south-eastern tip of the onshore rim, about sixty kilometres from Poza Rica and seven from the coast. It was licensed in Round 1.3 in 2016. The adjacent TM-01 block, with its own El Abra pools, was offered in Round 2.3 in 2018 and went to Jaguar after a tie-break cash bonus of twenty six point one million dollars.', run: f => { ca.transition().duration(f ? 0 : 600).attr('opacity', 0.35); tg.transition().duration(f ? 0 : 900).attr('opacity', 1); } },
        { say: 'Against its neighbours it is small and thin: about two and a half million barrels in place per square kilometre, against a reef-rim median of eight. That sets the scale for everything that follows. This is a field where one good well matters.' }
      ];
    }
  };

  // ---------------------------------------------------------------- at a glance
  P.glance = {
    id: 'glance', title: 'At a glance', section: 'Setting',
    build(el) {
      const body = std(el, { eyebrow: 'At a glance', title: 'Small, mature, still pressured, and its crest never produced', src: 'docs/04 production, docs/05 pressure, docs/07 volumetrics, docs/20 seismic, GLJ report 25269 (YE2025, Kinjal). Cumulative: 1.72 MMbbl in monthly records plus PEMEX wellfile allocations.' });
      body.innerHTML = `<div class="kpis" style="grid-template-columns:repeat(3,1fr);gap:38px 44px">
        ${S(1, `<div class="kpi card"><div class="v"><span data-count="7">7</span> + 2</div><div class="l">PEMEX wells 1956–73, then Tonalli's TEC-10 and TEC-11 in 2018. <b>Five produced oil</b>: TEC-2, 6, 7, 9 and 10</div></div>`)}
        ${S(1, `<div class="kpi card"><div class="v"><span data-count="1.98" data-dec="2">1.98</span><small>MMbbl</small></div><div class="l">Produced 1956–2022, about 20–25 % of the oil in place</div></div>`)}
        ${S(1, `<div class="kpi card"><div class="v"><span data-count="932">932</span><small>bbl/d</small></div><div class="l">Field peak, March 1972, from three wells after the 1971–72 recompletions</div></div>`)}
        ${S(2, `<div class="kpi card"><div class="v">7.8–11.2<small>MMbbl</small></div><div class="l">Oil in place: PEMEX/CNH to IFR; P50 10.0. Remaining recoverable about 0.9 MMbbl (0.3–1.6)</div></div>`)}
        ${S(2, `<div class="kpi card"><div class="v" style="color:var(--blue)">−0.5<small>MPa</small></div><div class="l">Pressure change in 62 years at 2,300 mSS: a strong bottom-water aquifer</div></div>`)}
        ${S(2, `<div class="kpi card hot"><div class="v">−2,293<small>m</small></div><div class="l">El Abra top at the TEC-12 bottom hole on the PEMEX PSTM: the crest, where no well has ever produced</div></div>`)}
      </div>`;
      return [
        { say: 'Here is the field in six numbers.' },
        { say: 'Nine wells. Five of them produced oil: TEC-2, 6, 7 and 9 under PEMEX, and TEC-10 under Tonalli. Together they made about two million barrels, with the field peaking at nine hundred and thirty two barrels a day in March 1972.', run: f => countUp(el, f) },
        { say: 'Seven point eight to eleven million barrels in place, so about a fifth to a quarter recovered. The pressure has barely moved in sixty years because an aquifer replaces what is produced. And the highest El Abra on the seismic, at the planned TEC-12 bottom hole, has never had a well produce from it.' }
      ];
    }
  };

  // ---------------------------------------------------------------- structure map (2-D, blue -> red)
  P.structure = {
    id: 'structure', title: 'Structure: top El Abra', section: 'Geology',
    build(el) {
      const body = std(el, { eyebrow: 'Geology', title: 'A NW–SE culmination; the crest is on the southern high', src: 'Top El Abra, Jan 2019 depth grid (50 m nodes, UTM 14N), contours every 10 m; well tops from the formation-tops table and GLJ map; TEC-11 from its directional survey; TEC-12 from the Feb 2021 programme · figure 25.' });
      body.innerHTML = `<div class="row" style="gap:44px"><div id="smapHost" style="position:relative;width:660px;height:660px;flex:none"></div>
        <div class="col grow" style="gap:24px">
          <div class="legend" style="flex-direction:column;gap:8px"><span style="font-size:20px">Top El Abra, m below sea level</span>
          <div style="display:flex;align-items:center;gap:12px"><span class="ticker">−2,420</span><div class="ramp-bar" style="width:380px;background:linear-gradient(90deg,${RAMP_CSS.join(',')})"></div><span class="ticker">−2,280</span></div>
          <span style="font-size:19px;color:var(--ink3)">blue = deep flank · red = highest</span></div>
          ${S(1, `<table class="st" style="font-size:21px"><tr><th>Well</th><th style="text-align:right">El Abra top, mSS</th><th>Note</th></tr>
            <tr><td>TEC-6</td><td class="n">−2,294.1</td><td>crest, south high</td></tr><tr><td>TEC-9</td><td class="n">−2,295.9</td><td>crest, south high</td></tr>
            <tr class="hl"><td><b>TEC-12 (plan)</b></td><td class="n">−2,293 ±4</td><td>PSTM tie; grid −2,289; programme −2,296</td></tr>
            <tr><td>TEC-2</td><td class="n">−2,301.6</td><td>north end</td></tr><tr><td>TEC-7</td><td class="n">−2,304.0</td><td>east flank</td></tr>
            <tr><td>TEC-10</td><td class="n">−2,309.7</td><td>south-west, at target</td></tr><tr><td>TEC-101</td><td class="n">−2,334.0</td><td>west flank, wet</td></tr>
            <tr><td>TEC-3</td><td class="n">−2,372.6</td><td>NE flank; lowest oil −2,374</td></tr><tr><td>TEC-5</td><td class="n">−2,551.0</td><td>off structure</td></tr></table>`)}
          ${S(2, `<p style="font-size:24px">Dashed blue: the <b style="color:#7fb4ff">−2,374 m</b> lowest known oil closes round the field.</p>`)}
        </div></div>`;
      const G = M.grid2019, Wm = 660, Hm = 660;
      const xr = [706250, 708950], yr = [2261500, 2264200];
      const map = structureMap($('#smapHost', el), G, { W: Wm, H: Hm, xr, yr, zmin: 2280, zmax: 2420, ramp: f => rampI(f) });
      const g = map.svg.append('g');
      const lko = d3.contours().size([G.nx, G.ny]).thresholds([-2374.2])(G.z.flat().map(v => v == null ? -9999 : -v));
      const tr = d3.geoTransform({ point(px, py) { this.stream.point(map.sx(G.x0 + px * G.dx), map.sy(G.y0 + py * G.dy)); } });
      g.append('path').datum(lko[0]).attr('d', d3.geoPath(tr)).attr('fill', 'none').attr('stroke', '#7fb4ff').attr('stroke-width', 3.5).attr('stroke-dasharray', '10 7');
      const t11 = (M.wells.find(w => w.well === 'TEC-11') || {}).path || [];
      g.append('path').attr('d', d3.line()(t11.map(p => [map.sx(p[0]), map.sy(p[1])]))).attr('fill', 'none').attr('stroke', '#c9b6ff').attr('stroke-width', 4);
      const ties = [['TEC-6', 707493.99, 2262529.05], ['TEC-9', 707833.5, 2262336.31], ['TEC-2', 707586.77, 2262986.35], ['TEC-7', 707945.7, 2262705.9], ['TEC-10', 707589.6, 2262253.1], ['TEC-101', 707336.3, 2262779.0], ['TEC-3', 707858.9, 2263433.11], ['TEC-5', 706443.52, 2263588.88], ['TEC-11 TD', 706847.2, 2263952.4]].filter(t => t[1] > xr[0] && t[1] < xr[1] && t[2] > yr[0] && t[2] < yr[1]);
      const off = { 'TEC-9': [14, 20], 'TEC-10': [14, 22], 'TEC-6': [-14, -14, 'end'], 'TEC-101': [-14, -10, 'end'] };
      ties.forEach(([n, x, y]) => { const [dx, dy, an] = off[n] || [14, -10]; g.append('circle').attr('cx', map.sx(x)).attr('cy', map.sy(y)).attr('r', 8).attr('fill', '#0b0f14').attr('stroke', '#fff').attr('stroke-width', 2.5); g.append('text').attr('x', map.sx(x) + dx).attr('y', map.sy(y) + dy).attr('text-anchor', an || 'start').text(n).attr('fill', '#fff').style('font-size', '22px').attr('font-weight', 600).attr('paint-order', 'stroke').attr('stroke', '#0b0f14').attr('stroke-width', 5); });
      const t12 = map.svg.append('g').attr('opacity', 0);
      t12.append('line').attr('x1', map.sx(707582)).attr('y1', map.sy(2262425)).attr('x2', map.sx(707754)).attr('y2', map.sy(2262460)).attr('stroke', '#fff').attr('stroke-width', 3).attr('stroke-dasharray', '6 5');
      t12.append('path').attr('d', d3.symbol(d3.symbolStar, 520)()).attr('transform', `translate(${map.sx(707754)},${map.sy(2262460)})`).attr('fill', '#ffcf3a').attr('stroke', '#0b0f14').attr('stroke-width', 2);
      t12.append('text').attr('x', map.sx(707754) + 22).attr('y', map.sy(2262460) - 16).text('TEC-12').attr('fill', '#ffe08a').style('font-size', '26px').attr('font-weight', 700).attr('paint-order', 'stroke').attr('stroke', '#0b0f14').attr('stroke-width', 5);
      const sc = map.svg.append('g').attr('transform', `translate(24,${Hm - 30})`); sc.append('line').attr('x2', map.sx(706250 + 500) - map.sx(706250)).attr('stroke', '#fff').attr('stroke-width', 4); sc.append('text').attr('y', -10).text('500 m').attr('fill', '#fff').style('font-size', '19px');
      map.svg.append('text').attr('x', Wm - 24).attr('y', 40).attr('text-anchor', 'end').text('N ↑').attr('fill', '#fff').style('font-size', '24px').attr('font-weight', 600);
      return [
        { say: 'This is the top of the El Abra reef from the 2019 depth grid, coloured blue on the deep flanks to red at the highest point. The field is an elongated north-west to south-east high, faulted on both flanks, with Tertiary shale resting directly on the reef.' },
        { say: 'The wells tie the map to within two metres. TEC-6 and TEC-9 are the highest wells, at about two thousand two hundred and ninety five metres subsea. TEC-2 is at the north end, TEC-7 on the east flank, and TEC-10, drilled in 2018, came in lower to the south-west. TEC-101, TEC-3 and TEC-5 define the flanks.' },
        { say: 'The dashed blue line is the lowest known oil at minus two thousand three hundred and seventy four metres, from a 1956 drill-stem test in TEC-3. It closes around the whole structure.' },
        { say: 'And the star is TEC-12: a short deviated well from the TEC-10 pad to the southern high, between TEC-6, TEC-9 and TEC-10, where the reef is highest.', run: f => t12.transition().duration(f ? 0 : 900).attr('opacity', 1) }
      ];
    }
  };

  // ---------------------------------------------------------------- seismic check in 3-D
  P.seismic = {
    id: 'seismic', kind: '3d', title: 'Seismic check', section: 'Geology',
    build(el) {
      el.innerHTML = `<div class="glass pe" style="position:absolute;left:90px;top:80px;width:760px">
        <div class="eyebrow">Seismic check</div><h2 style="font-size:52px;margin-top:10px">The PEMEX PSTM puts TEC-12 on the crest</h2>
        ${S(1, `<p style="margin-top:20px">Reef-top event auto-tracked across 14,880 traces of the PEMEX pre-stack time migration, tied to six wells.</p>`)}
        ${S(2, `<div class="kpis" style="grid-template-columns:1fr 1fr;margin-top:22px"><div class="kpi"><div class="v">−2,293<small>m</small></div><div class="l">El Abra top at TEC-12, ±~4 m: 3 m above TEC-9, 17 m above TEC-10</div></div><div class="kpi"><div class="v">97<small>%</small></div><div class="l">of the field's traces are later in time than TEC-12; only TEC-6 is earlier</div></div></div>`)}
        ${S(3, `<p style="margin-top:18px">The 2019 PSDM is sharper but images the top of the carbonate package. A marl over El Abra thickens off the crest, so it is not the reef top.</p>`)}
        </div><div class="src">PEMEX PSTM 554702 and DMI PSDM 2019, 8-bit display copies; PSTM shown in depth at the tie velocity (2,914–2,951 m/s). Inline through the TEC-12 bottom hole. docs/20.</div><div class="pg"></div>`;
      const [il, xl] = F.wellIJ('pstm', 'TEC-12');
      scene(ctx, { year: 2026.8, view: 'section', captions: false, highlight: 'TEC-12', slices: { vol: 'pstm', il: Math.round(il), xl: null, k: null, cmap: 'rwb' }, surfaceOpacity: 0.5, shift: [0.2, 0] });
      return [
        { say: 'Can we trust that map at the crest? We read the full PEMEX pre-stack time migration and the 2019 depth migration. This is an inline through the planned TEC-12 bottom hole, with the reef top grid draped over it.' },
        { say: 'On the PSTM we tracked the reef-top event across all fourteen thousand traces of the field and tied it to six wells. Time follows the well tops, with a correlation of plus point seven.' },
        { say: 'Converted with the crestal wells’ own velocities, the reef top at TEC-12 is at minus two thousand two hundred and ninety three metres, give or take four. That is three metres above TEC-9 and seventeen above TEC-10. Ninety seven percent of the field is lower in time; only TEC-6 is higher.', run: f => F.focusWell('TEC-12', f ? 0 : 2600, { dist: 1500, az: 0.2, el: 0.15, lift: 0 }) },
        { say: 'The depth migration looks sharper, but its strongest reflector is the top of the carbonate package, not the reef. A marl sits on the reef and thickens off the crest, which is the next slide.', run: f => F.setSlices({ vol: 'psdm', il: null, xl: Math.round(F.wellIJ('psdm', 'TEC-12')[1]), k: null, cmap: 'rwb' }) }
      ];
    }
  };

  // ---------------------------------------------------------------- the marl
  P.marl = {
    id: 'marl', title: 'The marl over the reef', section: 'Geology',
    build(el) {
      const body = std(el, { eyebrow: 'What the marl is', title: 'At the crest the window is reef; off the crest it is marl', src: 'Correlation panel hung on sea level; well spacing schematic. Tops: formation-tops table, TEC-10 cuttings XRD (RockWise, 62 samples), TEC-101 logs. Log values: TEC-10 2018 logs, P50 per unit (technical_tables.json “marl”).' });
      body.innerHTML = `<div class="row" style="gap:40px"><div id="marlX" style="width:1040px;height:720px"></div>
        <div class="col grow" style="gap:22px">
          ${S(2, `<h3>Tantoyuca marl</h3><p>Upper Eocene shale and silty marl that buried the eroded reef. At TEC-10 the cuttings are <b>31 % quartz, 9 % clay, 50 % calcite</b>, with pyrite; El Abra is <b>91–100 % calcite</b>.</p>`)}
          ${S(3, `<table class="st"><tr><th></th><th style="text-align:right">Marl</th><th style="text-align:right">El Abra</th></tr>
            <tr><td>Resistivity, ohm·m</td><td class="n">5.2</td><td class="n">16–47</td></tr><tr><td>Sonic, µs/ft</td><td class="n">71</td><td class="n">52–57</td></tr>
            <tr><td>Photo-electric, b/e</td><td class="n">3.9</td><td class="n">5.1</td></tr><tr><td>Gamma ray, API</td><td class="n">85</td><td class="n">45</td></tr></table>`)}
          ${S(4, `<p><b>Why it matters:</b> TEC-10's “wet” upper zone is this marl, not reservoir. It says nothing about El Abra at the crest, where the same depths are reef.</p>`)}
        </div></div>`;
      const wells = [['TEC-101', 2334.0, 'W flank'], ['TEC-6', 2294.1, 'crest'], ['TEC-12', 2293, 'plan'], ['TEC-9', 2295.9, 'crest'], ['TEC-2', 2301.6, 'N end'], ['TEC-10', 2312.9, 'SW (cuttings)']];
      const W = 1040, Hh = 720, m = { l: 110, r: 20, t: 50, b: 40 };
      const svg = d3.select('#marlX', el).append('svg').attr('viewBox', `0 0 ${W} ${Hh}`).attr('width', W).attr('height', Hh).style('font-family', 'IBM Plex Sans, sans-serif');
      const x = d3.scalePoint().domain(wells.map(w => w[0])).range([m.l + 40, W - m.r - 60]), y = d3.scaleLinear().domain([2270, 2350]).range([m.t, Hh - m.b]);
      const defs = svg.append('defs');
      const pm = defs.append('pattern').attr('id', 'marlpat').attr('width', 22).attr('height', 12).attr('patternUnits', 'userSpaceOnUse'); pm.append('rect').attr('width', 22).attr('height', 12).attr('fill', '#6b5a3e'); pm.append('line').attr('x1', 2).attr('x2', 12).attr('y1', 6).attr('y2', 6).attr('stroke', '#8a7650').attr('stroke-width', 2);
      const pr = defs.append('pattern').attr('id', 'reefpat').attr('width', 40).attr('height', 20).attr('patternUnits', 'userSpaceOnUse'); pr.append('rect').attr('width', 40).attr('height', 20).attr('fill', '#2f6d9a'); pr.append('path').attr('d', 'M0 10H40M20 0V10M0 10V20M40 10V20').attr('stroke', '#4c8cbb').attr('stroke-width', 1.5);
      const xs = wells.map(w => x(w[0])), top = wells.map(w => w[1]);
      const reefTop = d3.line().curve(d3.curveMonotoneX)(xs.map((xx, i) => [xx, y(top[i])]));
      const ext = (a, b) => `M${m.l},${y(a)} L${xs[0]},${y(top[0])} ` + reefTop.slice(1) + ` L${W - m.r},${y(top[top.length - 1])}`;
      svg.append('path').attr('d', `M${m.l},${y(2270)} H${W - m.r} V${y(top[top.length - 1])} ` + `L${xs[xs.length - 1]},${y(top[top.length - 1])} ` + d3.line().curve(d3.curveMonotoneX)(xs.map((xx, i) => [xx, y(top[i])]).reverse()).slice(1) + ` L${m.l},${y(top[0])} Z`).attr('fill', 'url(#marlpat)');
      svg.append('path').attr('d', `M${m.l},${y(2350)} H${W - m.r} V${y(top[top.length - 1])} L${xs[xs.length - 1]},${y(top[top.length - 1])} ` + d3.line().curve(d3.curveMonotoneX)(xs.map((xx, i) => [xx, y(top[i])]).reverse()).slice(1) + ` L${m.l},${y(top[0])} Z`).attr('fill', 'url(#reefpat)');
      svg.append('path').attr('d', d3.line().curve(d3.curveMonotoneX)([[m.l, y(top[0])], ...xs.map((xx, i) => [xx, y(top[i])]), [W - m.r, y(top[top.length - 1])]])).attr('fill', 'none').attr('stroke', '#bfe0ff').attr('stroke-width', 3);
      const ay = svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(8).tickFormat(d => '−' + d3.format(',')(d)));
      ay.selectAll('text').attr('fill', C.ink2).style('font-size', '20px'); ay.selectAll('line,path').attr('stroke', C.grid);
      svg.append('text').attr('x', 22).attr('y', (m.t + Hh - m.b) / 2).attr('transform', `rotate(-90,22,${(m.t + Hh - m.b) / 2})`).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '20px').text('m below sea level');
      const win = svg.append('g').attr('opacity', 0);
      win.append('rect').attr('x', m.l).attr('width', W - m.l - m.r).attr('y', y(2294)).attr('height', y(2311) - y(2294)).attr('fill', '#ffcf3a').attr('opacity', 0.18).attr('stroke', '#ffcf3a').attr('stroke-dasharray', '8 6');
      win.append('text').attr('x', W - m.r - 8).attr('y', y(2294) - 8).attr('text-anchor', 'end').attr('fill', '#ffe08a').style('font-size', '21px').attr('font-weight', 600).text('“window” −2,294 to −2,311 m');
      wells.forEach(([n, t, note]) => {
        const g = svg.append('g'); const xx = x(n);
        g.append('line').attr('x1', xx).attr('x2', xx).attr('y1', y(2270)).attr('y2', y(2350)).attr('stroke', n === 'TEC-12' ? '#ffcf3a' : '#e9eef3').attr('stroke-width', n === 'TEC-12' ? 4 : 3).attr('stroke-dasharray', n === 'TEC-12' ? '8 6' : null);
        g.append('text').attr('x', xx).attr('y', m.t - 18).attr('text-anchor', 'middle').attr('fill', n === 'TEC-12' ? '#ffe08a' : '#fff').style('font-size', '22px').attr('font-weight', 600).text(n);
        g.append('text').attr('x', xx + 8).attr('y', y(t) - 8).attr('fill', '#fff').style('font-size', '17px').attr('paint-order', 'stroke').attr('stroke', '#0b0f14').attr('stroke-width', 4).text('−' + d3.format(',.1f')(t));
      });
      svg.append('text').attr('x', m.l + 12).attr('y', y(2276)).attr('fill', '#f0e3c4').style('font-size', '22px').attr('font-weight', 600).text('Tantoyuca marl (Eocene)');
      svg.append('text').attr('x', m.l + 12).attr('y', y(2345)).attr('fill', '#d8ecff').style('font-size', '22px').attr('font-weight', 600).text('El Abra reef (Cretaceous)');
      return [
        { say: 'People ask what the marl is and why it keeps coming up. This is a correlation panel across the field, hung on sea level. Blue is the El Abra reef; brown is the Tantoyuca marl, an Eocene shale that buried the eroded reef top.' },
        { say: 'Now add the depth window that TEC-12 targets, two thousand two hundred and ninety four to two thousand three hundred and eleven metres. At the crest, at TEC-6, TEC-9 and TEC-12, that window is reef. At TEC-10 and TEC-101, where the reef top is lower, the same depths are still marl.', run: f => win.transition().duration(f ? 0 : 900).attr('opacity', 1) },
        { say: 'The rock tells them apart. The TEC-10 cuttings in the window are a third quartz with clay and pyrite; the reef is almost pure calcite.' },
        { say: 'On logs the marl reads about five ohm-metres, seventy one microseconds per foot on the sonic and a photo-electric factor near four. El Abra reads sixteen to forty seven ohm-metres, fifty two to fifty seven microseconds and above five.' },
        { say: 'So when someone says TEC-10’s upper zone was wet, the answer is that TEC-10 never had El Abra at those depths. It drilled marl. The same depths at the crest are reef, and that is what TEC-12 goes to measure.' }
      ];
    }
  };

  // ---------------------------------------------------------------- pressure
  P.pressure = {
    id: 'pressure', title: 'Pressure: almost unchanged', section: 'Reservoir',
    build(el) {
      const body = std(el, { eyebrow: 'Drive mechanism', title: 'Sixty-two years, two million barrels, 0.5 MPa', src: '21 surveys corrected to 2,300 mSS at 10.5 kPa/m (docs/05). Hollow: flowing or short shut-in, not reservoir pressure. Closed-reservoir line: N 11.2 MMbbl × ct 1.98×10⁻⁶ /kPa (IHS 2018 TEC-2 model) down to an assumed bubble point of 20 MPa (IHS model); illustrative.' });
      body.innerHTML = `<div class="row" style="gap:40px"><div id="pr1" style="width:900px"></div><div id="pr2" style="width:720px"></div></div>
        <div class="row" style="gap:60px">${S(1, `<div class="kpi"><div class="v" style="color:var(--blue)">24.65 → 24.14<small>MPa</small></div><div class="l">1956 to 2018 at 2,300 mSS: −0.51 MPa (−2 %)</div></div>`)}
        ${S(3, `<div class="kpi"><div class="v">&gt;99<small>%</small></div><div class="l">of produced volume replaced by water influx. Recovery depends on sweep and water handling, not on pressure.</div></div>`)}</div>`;
      const pr = D.pressure.map(p => ({ ...p, d: ymd(p.date) }));
      const c1 = timeChart($('#pr1', el), { W: 900, H: 470, xticks: 7, x: [ymd('1955-01'), ymd('2020-12')], yl: [0, 30], yticks: 6, ylabel: 'Pressure at 2,300 mSS, MPa', series: [
        { key: 'i', color: '#5b9bd5', values: [{ d: ymd('1955-01'), v: 24.65 }, { d: ymd('2020-12'), v: 24.65 }], dash: '8 8', width: 2 },
        { key: 's', type: 'dots', color: '#5b9bd5', r: 10, values: pr.filter(p => p.usable).map(p => ({ d: p.d, v: p.p_mpa })) },
        { key: 'n', type: 'dots', color: '#55606c', r: 8, values: pr.filter(p => !p.usable).map(p => ({ d: p.d, v: p.p_mpa })) }],
        events: [{ d: ymd('1956-05'), text: '1956  24.65 MPa (252 kg/cm²)', y: 0.08 }, { d: ymd('2018-05'), text: '2018  24.14', y: 0.08, left: true }] });
      const W2 = 720, H2 = 470, m = { l: 80, r: 30, t: 30, b: 70 };
      const svg = d3.select('#pr2', el).append('svg').attr('viewBox', `0 0 ${W2} ${H2}`).attr('width', W2).attr('height', H2).style('font-family', 'IBM Plex Sans, sans-serif');
      const gx = d3.scaleLinear().domain([0, 2.2]).range([m.l, W2 - m.r]), gy = d3.scaleLinear().domain([0, 30]).range([H2 - m.b, m.t]);
      const ax = svg.append('g').attr('transform', `translate(0,${H2 - m.b})`).call(d3.axisBottom(gx).ticks(5)); const ay = svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(gy).ticks(6));
      [ax, ay].forEach(a => { a.selectAll('text').attr('fill', C.ink2).style('font-size', '20px'); a.selectAll('line,path').attr('stroke', C.grid); });
      svg.append('text').attr('x', (m.l + W2 - m.r) / 2).attr('y', H2 - 18).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '20px').text('Cumulative oil produced, MMbbl');
      const ctl = svg.append('g').attr('opacity', 0);
      ctl.append('line').attr('x1', gx(0)).attr('y1', gy(24.65)).attr('x2', gx(0.103)).attr('y2', gy(20)).attr('stroke', C.gas).attr('stroke-width', 4);
      ctl.append('line').attr('x1', gx(0.103)).attr('y1', gy(20)).attr('x2', gx(0.103)).attr('y2', gy(2)).attr('stroke', C.gas).attr('stroke-width', 2).attr('stroke-dasharray', '6 6');
      ctl.append('text').attr('x', gx(0.14)).attr('y', gy(13)).attr('fill', '#ff8f87').style('font-size', '21px').text('Without an aquifer: bubble point');
      ctl.append('text').attr('x', gx(0.14)).attr('y', gy(13) + 26).attr('fill', '#ff8f87').style('font-size', '21px').text('after about 0.1 MMbbl');
      const act = svg.append('g').attr('opacity', 0);
      pr.filter(p => p.usable).forEach(p => act.append('circle').attr('cx', gx((p.np_bbl || 0) / 1e6)).attr('cy', gy(p.p_mpa)).attr('r', 10).attr('fill', '#5b9bd5').attr('stroke', C.bg).attr('stroke-width', 2));
      act.append('text').attr('x', gx(1.0)).attr('y', gy(24.65) - 22).attr('text-anchor', 'middle').attr('fill', '#9cc7f0').style('font-size', '22px').attr('font-weight', 600).text('Actual: flat to 2.06 MMbbl');
      return [
        { say: 'This is the single most important reservoir fact. Here is every pressure measurement in the field since 1956, corrected to one datum, on a scale that starts at zero. Discovery pressure was twenty four point six five megapascals. In 2018, after sixty two years, TEC-2 and TEC-10 both measured twenty four point one four. Half a megapascal. Two percent.', run: f => c1.revealAll(f ? 0 : 2400) },
        { say: 'The grey points are flowing pressures or very short shut-ins, which read low and are not reservoir pressure.' },
        { say: 'To see what that means, plot pressure against oil produced. If the reservoir were sealed, rock and fluid expansion alone would have taken it to the bubble point after about a hundred thousand barrels.', run: f => ctl.transition().duration(f ? 0 : 900).attr('opacity', 1) },
        { say: 'Instead it produced two million barrels with almost no pressure loss. More than ninety nine percent of the voidage was replaced by water. The drive is a strong bottom-water aquifer. Recovery here is about sweep and water handling, not pressure, and every new well should be designed for low drawdown.', run: f => act.transition().duration(f ? 0 : 900).attr('opacity', 1) }
      ];
    }
  };

  // ---------------------------------------------------------------- fluids and gas
  P.fluids = {
    id: 'fluids', title: 'Oil, gas and water', section: 'Reservoir',
    build(el) {
      const body = std(el, { eyebrow: 'Fluid analysis', title: 'Light, sour, slightly undersaturated oil; no lab PVT yet', src: 'SGS Deer Park (TEC-2 May 2018, TEC-10 Jul 2018), Intertek (TEC-10 tank, Nov 2018–Jan 2019), PEMEX Engler forms 1956–75, Stratascan/SGS gas and Stiff water analyses (2018), production database GOR (docs/04 §5). fluids_rock_core_notes.md.' });
      const gasC = D.tech?.gas?.compositions_mol_pct?.find(g => g.well === 'TEC-10') || { C1: 70.321, C2: 7.707, C3: 4.701, iC4: 1.119, nC4: 1.545, iC5: 0.505, nC5: 0.49, C6plus: 0.669, CO2: 11.142, H2S: 0.989, N2: 0.812 };
      body.innerHTML = `<div class="row" style="gap:46px;align-items:flex-start">
        <div class="col" style="width:560px">${S(0, `<h3>Oil</h3><div id="apiBars"></div><p style="font-size:24px">Stock-tank 28–31 °API across 1956–2019; sulphur 1.1–1.7 %; dead-oil viscosity 13.7 cSt at 40 °C. Reservoir 97.5–99 °C.</p>`)}</div>
        <div class="col" style="width:520px">${S(1, `<h3>Gas: TEC-10 separator, 2018</h3><div class="row" style="gap:20px;align-items:center"><div id="gasDonut"></div><div id="gasLeg"></div></div><p style="font-size:24px">Sour: H₂S 1.0–1.7 mol %, CO₂ 11 %. Flared under the evaluation-period approval.</p>`)}</div>
        <div class="col grow">${S(2, `<h3>Gas–oil ratio</h3><div id="gorBars"></div><p style="font-size:24px">Solution GOR about 550–570 scf/bbl from 27 years of production. TEC-2’s 1956 top test is possible evidence of a small crestal gas cap.</p>`)}
          ${S(3, `<p style="font-size:24px;color:var(--accent2)"><b>No PVT sample has ever been taken.</b> TEC-12's bottom-hole sample would be the field's first.</p>`)}</div></div>`;
      const api = [['TEC-6 1956', 30.2], ['TEC-7 1957', 30.8], ['TEC-2 1974', 33.2], ['TEC-2 2018', 28.4], ['TEC-10 2018', 26.5], ['TEC-10 tank 2018', 30.4], ['TEC-10 tank 2019', 30.1]];
      const b1 = hbars($('#apiBars', el), api.map(([l, v]) => ({ label: l, value: v, color: C.oil })), { W: 560, rowH: 46, labelW: 210, max: 36, ticks: 4, vfmt: d3.format('.1f') });
      const parts = [['C1 methane', gasC.C1, '#5b9bd5'], ['C2–C6+', gasC.C2 + gasC.C3 + gasC.iC4 + gasC.nC4 + gasC.iC5 + gasC.nC5 + gasC.C6plus, '#2fb38a'], ['CO₂', gasC.CO2, '#e0b341'], ['H₂S', gasC.H2S, '#e5534b'], ['N₂', gasC.N2, '#8b95a1']];
      const dn = donut($('#gasDonut', el), parts.map(([k, v, c]) => ({ key: k, value: v, color: c })), { S: 260, center: ['0.83', 'gas gravity'] });
      $('#gasLeg', el).innerHTML = parts.map(([k, v, c]) => `<div style="display:flex;gap:10px;align-items:center;font-size:20px;color:var(--ink2);margin:6px 0;white-space:nowrap;width:220px"><i style="width:16px;height:16px;border-radius:3px;background:${c};display:inline-block"></i>${k} <b class="ticker" style="margin-left:auto;padding-left:14px">${d3.format('.1f')(v)} %</b></div>`).join('');
      const gor = [['1956–73 initial tests', 576, '431–765'], ['TEC-6 survey 1964', 685], ['Field 1966–92 cum.', 565], ['Field 2003–12 cum.', 556], ['TEC-10 flowback 2018', 767], ['CNH filing 2021', 859], ['Flaring permit basis', 337]];
      const b3 = hbars($('#gorBars', el), gor.map(([l, v, t]) => ({ label: l, value: v, text: t || d3.format(',')(v), color: l.startsWith('Flaring') ? C.gas : C.water })), { W: 640, rowH: 46, labelW: 270, max: 1000, ticks: 4, vfmt: d3.format(',') });
      return [
        { say: 'The fluids. The oil is light: twenty eight to thirty one degrees API in every analysis from 1956 to 2019, with one to one point seven percent sulphur. Reservoir temperature is about ninety eight degrees Celsius.', run: f => b1.show(f) },
        { say: 'The gas is mostly methane, but sour: about eleven percent carbon dioxide and one to one point seven percent hydrogen sulphide. Sour-service materials are needed, and the gas is flared under the evaluation-period approval.', run: f => dn.show(f) },
        { say: 'The gas situation: twenty seven years of production give a solution gas–oil ratio of about five fifty to five seventy standard cubic feet per barrel, and TEC-10 tested at about seven seventy. TEC-2’s first test, at the crest in 1956, is possible evidence of a small gas cap; field GOR stayed low for decades, so any gas cap was small. One flag: the flaring permit was justified at three thirty seven, below every measured value. That needs reconciling with the regulator.', run: f => b3.show(f) },
        { say: 'And there has never been a laboratory PVT study. Every bubble point and formation volume factor in circulation is a correlation. TEC-12’s bottom-hole sample would be the field’s first.' }
      ];
    }
  };

  // ---------------------------------------------------------------- core
  P.core = {
    id: 'core', title: 'Core and rock', section: 'Reservoir',
    build(el) {
      const body = std(el, { eyebrow: 'Core analysis · TEC-10, 2018', title: 'Tight matrix, fractured flow', src: 'Stratascan core report and plug workbook (TEC-10 core 1, 2,352–2,362 mMD cut, 1.3 m recovered); IHS 2018 pressure-transient analysis; CMI image log. fluids_rock_core_notes.md §5–6.' });
      body.innerHTML = `<div class="row" style="gap:50px;align-items:flex-start"><div class="col" style="width:820px">
        ${S(0, `<table class="st"><tr><th>Plug, mMD</th><th style="text-align:right">Porosity</th><th style="text-align:right">k at 500 psi, mD</th><th style="text-align:right">k at 3,400 psi</th><th style="text-align:right">Oil, % PV</th></tr>
          <tr><td>N1H1 · 2,352.25</td><td class="n">2.3 %</td><td class="n">0.02</td><td class="n">0.004</td><td class="n">58.8</td></tr>
          <tr><td>N1H2 · 2,352.70</td><td class="n">6.7 %</td><td class="n">0.96</td><td class="n">0.36</td><td class="n">19.7</td></tr>
          <tr><td>N1H3 · 2,352.89</td><td class="n">7.6 %</td><td class="n">0.17</td><td class="n">0.08</td><td class="n">13.8</td></tr></table>
          <p style="font-size:22px;margin-top:10px">Klinkenberg permeability; Dean-Stark oil before cleaning, water-based mud. Grainstone of miliolid forams, strongly recrystallised; outer-platform setting.</p>`)}
        ${S(2, `<p>Only 1.3 m of the 10 m cored was recovered: the core was too fractured to leave its sleeve. The TEC-12 window has never been cored anywhere.</p>`)}</div>
        <div class="col grow">${S(1, `<div id="kBars"></div><p style="font-size:24px">The well test needs <b>18 mD</b> over 13 m; the matrix gives under 1. Oil flows through fractures and vugs: 0–7 fractures per metre on the image log.</p>`)}</div></div>`;
      const kb = hbars($('#kBars', el), [{ label: 'Core plugs, best', value: 0.96, color: C.ink3, text: '0.96 mD' }, { label: 'TEC-10 well test', value: 18, color: C.oil, text: '18 mD' }, { label: 'TEC-2 well test', value: 50, color: C.oil, text: '50 mD' }], { W: 760, rowH: 70, labelW: 260, max: 60, ticks: 4, vfmt: d3.format(',') });
      return [
        { say: 'The only core in the field is from TEC-10: ten metres cut in El Abra, one point three recovered, because the rock was so fractured it would not come out of its sleeve. Three plugs give two to eight percent porosity and well under a millidarcy of matrix permeability.' },
        { say: 'Yet the 2018 well tests need eighteen millidarcies at TEC-10 and about fifty at TEC-2. The oil flows through fractures and dissolution vugs. That is also why water moves fast and wells cone.', run: f => kb.show(f) },
        { say: 'Two gaps worth noting: the upper window that TEC-12 targets has never been cored anywhere, and there are no capillary-pressure or relative-permeability data. Both are cheap to fix in the next well.' }
      ];
    }
  };

  // ---------------------------------------------------------------- TEC-10 logs, clear version
  P.logs = {
    id: 'logs', title: 'TEC-10 logs, read simply', section: 'Reservoir',
    build(el) {
      const body = std(el, { eyebrow: 'TEC-10DES logs, 2018', title: 'Marl above, oil-bearing El Abra below, and the crest is higher', src: 'Weatherford 2018 triple combo (TECOLUTLA-10_LAS), depth on the directional survey (KB 6.13 m), 0.5 m medians. Tops: cuttings XRD (El Abra −2,312.9) and logs (−2,310). Perforations 2,349.5–2,353 mMD.' });
      body.innerHTML = `<div class="row" style="gap:40px;align-items:flex-start"><div id="lt" style="width:1080px"></div>
        <div class="col grow" style="gap:26px">
          ${S(1, `<p><b style="color:#d9b98a">Tantoyuca marl</b>, −2,294 to −2,311 m: low resistivity, higher gamma ray, low photo-electric factor. Not reservoir.</p>`)}
          ${S(2, `<p><b style="color:#7fc3ff">El Abra</b> from about −2,311 m: resistivity jumps to 15–50 ohm·m. Perforated at −2,314 to −2,318: 182 bbl/d on test.</p>`)}
          ${S(3, `<p><b style="color:#ffe08a">At TEC-12</b> the reef top is at −2,293, about 17 m higher. The depths that are marl here are reef there.</p>`)}</div></div>`;
      const rows = D.logs.tec10.map(r => ({ ...r }));
      const lt = logTracks($('#lt', el), rows, { W: 1080, H: 590, depth: [2278, 2372], ylabel: 'm below sea level',
        tracks: [{ title: 'Gamma ray', unit: 'API', domain: [0, 150], curves: [{ key: 'gr', color: '#7bd36a', width: 2.6 }] },
          { title: 'Resistivity', unit: 'ohm·m', domain: [1, 200], log: true, curves: [{ key: 'res_ild', color: '#ff6b5e', width: 2.8 }] },
          { title: 'Porosity', unit: 'v/v', domain: [0.3, -0.05], curves: [{ key: 'nprl', color: '#5b9bd5', width: 2.4 }, { key: 'dprl', color: '#e0b341', width: 2.4 }] },
          { title: 'Photo-electric', unit: 'b/e', domain: [2, 6], curves: [{ key: 'pe', color: '#c9b6ff', width: 2.4 }] }],
        zones: [{ id: 'marl', top: 2294, base: 2311, color: '#b8925a', opacity: 0.3 }, { id: 'abra', top: 2311, base: 2380, color: '#3d7fc0', opacity: 0.16, line: '#7fc3ff' }, { id: 'perf', top: 2314, base: 2318, color: '#ff7a2f', opacity: 0.55 }, { id: 't12', top: 2293, base: 2293.8, color: '#ffcf3a', opacity: 1 }] });
      const lg = legend($('#lt', el), [['#5b9bd5', 'neutron porosity', 'ln'], ['#e0b341', 'density porosity', 'ln'], ['#ff7a2f', 'perforations', 'sw']]); lg.style.marginTop = '10px';
      return [
        { say: 'These are TEC-10’s logs, drawn simply: gamma ray, resistivity, porosity and photo-electric factor against depth below sea level.', run: f => lt.draw(f) },
        { say: 'The brown band is the marl, from two thousand two hundred and ninety four to two thousand three hundred and eleven metres. Resistivity is about five ohm-metres and the photo-electric factor is low: clay and quartz, not limestone.', run: f => lt.zone('marl', f) },
        { say: 'At about two thousand three hundred and eleven metres the curves change together. Resistivity jumps to fifteen to fifty ohm-metres and the photo-electric factor rises to limestone. That is the El Abra top. Tonalli perforated four metres just below it and the well tested one hundred and eighty two barrels a day.', run: f => { lt.zone('abra', f); lt.zone('perf', f); } },
        { say: 'The yellow line is where the reef top is at TEC-12, seventeen metres higher. The interval that is marl at TEC-10 should be reef at the crest, and the well will log it before anything is perforated.', run: f => lt.zone('t12', f) }
      ];
    }
  };

  // ---------------------------------------------------------------- oil in place
  P.ooip = {
    id: 'ooip', title: 'Oil in place', section: 'Reserves',
    build(el) {
      const body = std(el, { eyebrow: 'Oil in place', title: '7.8 to 11.2 MMbbl: a petrophysics question, not a structure question', src: 'Five source estimates recomputed from their own inputs (docs/07): IFR Summary (GLJ) sheet, Petrel Robertson geomodel (three cases), CNH/PEMEX booked volume. Monte Carlo 20,000 draws on triangular inputs spanning the sources.' });
      const O = D.ooip;
      body.innerHTML = `<div class="row" style="gap:46px;align-items:flex-start"><div class="col" style="width:820px">${S(0, `<h3>By source, MMbbl</h3><div id="oo1"></div>`)}${S(2, `<h3>What moves it</h3><div id="oo3"></div>`)}</div>
        <div class="col grow">${S(1, `<h3>Probabilistic range</h3><div id="oo2"></div>`)}${S(3, `<div class="kpis" style="grid-template-columns:1fr 1fr"><div class="kpi"><div class="v">~0.9<small>MMbbl</small></div><div class="l">remaining recoverable at the trend recovery factor (0.3–1.6)</div></div><div class="kpi"><div class="v">25<small>%</small></div><div class="l">recovered to date on the CNH volume; reef-rim median 3P 31 %</div></div></div>`)}</div></div>`;
      const labs = { 'IFR': 'IFR (used by GLJ)', 'Petrel Robertson, deep': 'Petrel Robertson, all wells', 'Petrel Robertson, TEC-10': 'Petrel R., TEC-10 logs', 'Petrel Robertson, TEC-2': 'Petrel R., vintage logs', 'CNH': 'CNH / PEMEX booked' };
      const src = O.sources.map(s => ({ label: Object.entries(labs).find(([k]) => s.source.startsWith(k))?.[1] || s.source.slice(0, 26), value: s.ooip_mmbbl, color: s.ooip_mmbbl < 9 ? C.water : C.oil }));
      const b1 = hbars($('#oo1', el), src, { W: 820, rowH: 42, labelW: 330, max: 13, ticks: 6 });
      const hg = histogram($('#oo2', el), O.hist.filter(b => b.x0 >= 5.5 && b.x1 <= 15.5), { W: 800, H: 380, xlabel: 'Field OOIP, MMbbl', marks: [{ v: O.mc.p90, text: 'P90 ' + O.mc.p90.toFixed(1) }, { v: O.mc.p50, text: 'P50 ' + O.mc.p50.toFixed(1), color: '#ffe08a' }, { v: O.mc.p10, text: 'P10 ' + O.mc.p10.toFixed(1) }] });
      const sw = O.swing, nm = { phi: 'Porosity', ntg: 'Net-to-gross', area: 'Area', sw: 'Water saturation', gross: 'Gross thickness', bo: 'Formation volume factor' };
      const tn = tornado($('#oo3', el), Object.entries(sw).map(([k, [lo, hi]]) => ({ label: nm[k] || k, lo, hi })).sort((a, b) => (b.hi - b.lo) - (a.hi - a.lo)), O.mc.mode_case ?? 10.0, { W: 820, H: 330, xlabel: 'OOIP, MMbbl' });
      return [
        { say: 'How much oil was there? Five estimates are in the files and each recomputes exactly from its own inputs. PEMEX and CNH booked seven point eight million barrels. IFR’s volumetric, which GLJ uses, is eleven point two. The independent Petrel Robertson model gives either answer depending on which logs it is fed.', run: f => b1.show(f) },
        { say: 'Spanning those inputs, the range is eight to twelve million barrels, with ten as the P50.', run: f => hg.show(f) },
        { say: 'Porosity and net-to-gross move the answer most, by about two and a half million barrels each way. Area and structure matter much less. So the gap is a petrophysics question, which modern logs in a new well can answer.', run: f => tn.show(f) },
        { say: 'At the reef-rim average recovery, about nine hundred thousand barrels remain to be recovered, in a range of three hundred thousand to one point six million.' }
      ];
    }
  };

  // ---------------------------------------------------------------- recovery factor against the El Abra trend
  P.recovery = {
    id: 'recovery', title: 'Recovery against the trend', section: 'Reserves',
    build(el) {
      const body = std(el, { eyebrow: 'Recovery factor', title: 'Tecolutla has recovered about what its neighbours have, on the CNH volume', src: 'CNH El Abra trend table, 45 fields, production to Apr 2015 (analogue_rf.csv, docs/07 §3): recovery = cumulative ÷ CNH original volume. Tecolutla also shown on IFR’s 11.2 MMbbl. Neighbours: Miguel Hidalgo (NW) and Ignacio Allende (SE) blocks; Vicente Guerrero and Gutiérrez Zamora, mapped in IFR’s TM-01 deck.' });
      const AN = (D.ooip && D.ooip.analogues) || [];
      body.innerHTML = `<div class="row" style="gap:50px;align-items:flex-start"><div id="rfSc" style="width:980px;height:640px;flex:none"></div>
        <div class="col grow" style="gap:22px">${S(1, `<h3>Nearest El Abra pools · recovery to date</h3><div id="rfNb"></div>`)}
        ${S(2, `<div class="kpis" style="grid-template-columns:1fr 1fr"><div class="kpi"><div class="v">30<small>%</small></div><div class="l">reef-rim median to date (3P ultimate 31 %, best 53 %)</div></div><div class="kpi hot"><div class="v">18–25<small>%</small></div><div class="l">Tecolutla, on IFR’s 11.2 and CNH’s 7.8 MMbbl</div></div></div>`)}</div></div>`;
      const W = 980, Hh = 640, m = { l: 90, r: 30, t: 30, b: 70 };
      const svg = d3.select('#rfSc', el).append('svg').attr('viewBox', `0 0 ${W} ${Hh}`).attr('width', W).attr('height', Hh).style('font-family', 'IBM Plex Sans, sans-serif');
      const x = d3.scaleLog().domain([0.2, 2000]).range([m.l, W - m.r]), y = d3.scaleLinear().domain([0, 55]).range([Hh - m.b, m.t]);
      const ax = svg.append('g').attr('transform', `translate(0,${Hh - m.b})`).call(d3.axisBottom(x).tickValues([0.3, 1, 3, 10, 30, 100, 300, 1000]).tickFormat(d3.format('~g')));
      const ay = svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6).tickFormat(d => d + ' %'));
      [ax, ay].forEach(a => { a.selectAll('text').attr('fill', C.ink2).style('font-size', '20px'); a.selectAll('line,path').attr('stroke', C.grid); });
      svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', Hh - 18).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '20px').text('Original oil in place, MMbbl (log scale)');
      svg.append('text').attr('x', 22).attr('y', (m.t + Hh - m.b) / 2).attr('transform', `rotate(-90,22,${(m.t + Hh - m.b) / 2})`).attr('text-anchor', 'middle').attr('fill', C.ink2).style('font-size', '20px').text('Recovered to date, % of OOIP');
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(30)).attr('y2', y(30)).attr('stroke', '#9cc7f0').attr('stroke-dasharray', '8 6').attr('stroke-width', 2);
      svg.append('text').attr('x', x(1.15)).attr('y', y(30) - 10).attr('text-anchor', 'start').attr('fill', '#9cc7f0').style('font-size', '19px').attr('paint-order', 'stroke').attr('stroke', C.bg).attr('stroke-width', 5).text('reef-rim median 30 %');
      const NB = ['Miguel Hidalgo', 'Ignacio Allende', 'Vicente Guerrero', 'Gutiérrez Zamora'];
      const pts = AN.filter(a => a.field !== 'Tecolutla' && a.ooip_mmbbl > 0.1 && a.rf_current > 0);
      svg.append('g').selectAll('circle').data(pts).join('circle').attr('cx', a => x(a.ooip_mmbbl)).attr('cy', a => y(100 * a.rf_current)).attr('r', a => NB.includes(a.field) ? 10 : 7)
        .attr('fill', a => NB.includes(a.field) ? '#5b9bd5' : a.play === 'Reef Rim' ? '#7b8794' : '#4a525c').attr('stroke', C.bg).attr('stroke-width', 1.5);
      const nb = svg.append('g');
      const lab = { 'Miguel Hidalgo': [12, 22], 'Ignacio Allende': [12, -12], 'Vicente Guerrero': [12, -12], 'Gutiérrez Zamora': [12, -12] };
      pts.filter(a => NB.includes(a.field)).forEach(a => nb.append('text').attr('x', x(a.ooip_mmbbl) + lab[a.field][0]).attr('y', y(100 * a.rf_current) + lab[a.field][1]).text(a.field).attr('fill', '#cfe3ff').style('font-size', '19px').attr('paint-order', 'stroke').attr('stroke', C.bg).attr('stroke-width', 5));
      const tg = svg.append('g');
      tg.append('line').attr('x1', x(7.8)).attr('y1', y(24.5)).attr('x2', x(11.2)).attr('y2', y(17.7)).attr('stroke', C.accent).attr('stroke-width', 3).attr('stroke-dasharray', '5 5');
      [[7.8, 24.5, 'CNH 7.8'], [11.2, 17.7, 'IFR 11.2']].forEach(([o, r, t]) => { tg.append('circle').attr('cx', x(o)).attr('cy', y(r)).attr('r', 12).attr('fill', C.accent).attr('stroke', '#fff').attr('stroke-width', 2.5); tg.append('text').attr('x', x(o) + 16).attr('y', y(r) + 28).text(t).attr('fill', '#ffd0b0').style('font-size', '18px'); });
      tg.append('text').attr('x', x(7.8) - 16).attr('y', y(24.5) - 18).attr('text-anchor', 'end').text('Tecolutla').attr('fill', '#fff').style('font-size', '24px').attr('font-weight', 700).attr('paint-order', 'stroke').attr('stroke', C.bg).attr('stroke-width', 5);
      const lg = svg.append('g').attr('transform', `translate(${m.l + 20},${m.t + 10})`);
      [['#7b8794', 'reef-rim field'], ['#4a525c', 'platform-interior field'], ['#5b9bd5', 'nearest pools']].forEach(([c, t], i) => { lg.append('circle').attr('cx', 8).attr('cy', i * 28).attr('r', 8).attr('fill', c); lg.append('text').attr('x', 24).attr('y', i * 28 + 6).text(t).attr('fill', C.ink2).style('font-size', '18px'); });
      const near = [...NB.map(n => AN.find(a => a.field === n)).filter(Boolean).map(a => ({ label: a.field, value: 100 * a.rf_current, color: '#5b9bd5', text: `${(100 * a.rf_current).toFixed(0)} % · 3P ${(100 * a.rf_3p_eur).toFixed(0)} %` })),
        { label: 'Tecolutla, CNH', value: 24.5, color: C.accent, text: '25 % · 3P 27 %' }, { label: 'Tecolutla, IFR', value: 17.7, color: C.accent, text: '18 %' }].sort((a, b) => b.value - a.value);
      const nbB = hbars($('#rfNb', el), near, { W: 640, rowH: 50, labelW: 230, max: 45, ticks: 3, vfmt: d3.format('.0f'), m: { r: 170 } });
      return [
        { say: 'How does the recovery compare with other El Abra pools? This is the CNH table of forty five El Abra fields, recovery to date against the oil in place. Reef-rim fields have recovered a median of thirty percent; the best reach fifty. Tecolutla, in orange, has recovered about twenty five percent on the CNH volume, or eighteen on IFR’s larger volume.' },
        { say: 'Its nearest neighbours bracket it. Miguel Hidalgo, next door to the north-west, has recovered twenty two percent; Ignacio Allende, to the south-east, twenty seven; Vicente Guerrero thirty seven and Gutiérrez Zamora forty.', run: f => nbB.show(f) },
        { say: 'So on the CNH volume Tecolutla has done about what a typical small reef-rim pool does; on the IFR volume it is below the trend, with about a third of its trend recovery still ahead. Either way, the remaining oil is about nine hundred thousand barrels, and most of it sits at the crest.' }
      ];
    }
  };

  // ---------------------------------------------------------------- operating cost with oil and water
  P.opex = {
    id: 'opex', title: 'Operations and cost', section: 'Operations',
    build(el) {
      const body = std(el, { eyebrow: 'Operations and cost', title: 'Field opex fell by two-thirds once the water stayed in the field', src: 'Opex: Tonalli monthly summary Sep 2018–Dec 2019 (cash, USD); later years are annual LOS / P&L totals ÷ 12, drawn dashed (not monthly actuals). Oil: PEMEX statements and tickets; water: TEC-10 daily sheet and CNH filings. opex_monthly.csv, opex_notes.md.' });
      body.innerHTML = `<div id="opx"></div><div class="row" style="gap:40px">
        ${S(1, `<div class="kpi"><div class="v">70–80 → 24<small>k$/mo</small></div><div class="l">mid-2019 to Jul–Nov 2020, with similar oil and more water</div></div>`)}
        ${S(2, `<div class="grow" style="max-width:1100px"><p style="font-size:25px"><b>Why:</b> produced water went into TEC-7 from August 2019, ending water trucking and disposal fees; the separator and injection-pump rentals ended; a TEC-10 to TEC-2 flowline and one supervision contract replaced site engineers.</p></div>`)}</div>`;
      const ox = D.opex.filter(r => r.month >= '2018-09');
      const dim = m => { const [y, mo] = m.split('-').map(Number); return new Date(Date.UTC(y, mo, 0)).getUTCDate(); };
      const oil = ox.map(r => ({ d: ymd(r.month), v: r.oil_bbl != null ? r.oil_bbl / dim(r.month) : null }));
      const wat = ox.map(r => ({ d: ymd(r.month), v: r.water_bbl != null ? r.water_bbl / dim(r.month) : null }));
      const opA = ox.map(r => ({ d: ymd(r.month), v: r.opex_usd != null ? r.opex_usd / 1000 : null }));
      const opB = ox.map(r => ({ d: ymd(r.month), v: r.opex_usd == null && r.opex_period_avg_usd_per_month != null ? r.opex_period_avg_usd_per_month / 1000 : null }));
      const ch = timeChart($('#opx', el), { W: 1680, H: 430, right: true, x: [ymd('2018-08'), ymd('2026-01')], yl: [0, 300], yr: [0, 100], yticks: 6, ylabel: 'Oil and water, bbl/d', yrlabel: 'Field opex, k USD per month',
        series: [{ key: 'w', color: C.water, values: wat, width: 3, type: 'area', opacity: 0.25 }, { key: 'o', color: C.oil, values: oil, width: 3.5 }, { key: 'a', color: C.accent, values: opA, axis: 'r', width: 4.5, type: 'step' }, { key: 'b', color: C.accent, values: opB, axis: 'r', width: 3.5, type: 'step', dash: '10 8' }],
        bands: [{ from: ymd('2022-02'), to: ymd('2026-01'), color: '#ffffff', opacity: 0.04 }],
        events: [{ d: ymd('2019-08'), text: 'Aug 2019: water into TEC-7', y: 0.05 }, { d: ymd('2020-03'), text: 'Mar 2020: separator rental ends', y: 0.14 }, { d: ymd('2022-02'), text: 'Feb 2022: field shut in', y: 0.05 }, { d: ymd('2023-01'), text: '2023 care & maintenance, no split', y: 0.24 }] });
      legend($('#opx', el), [[C.oil, 'oil, bbl/d', 'ln'], [C.water, 'produced water, bbl/d', 'sw'], [C.accent, 'opex, monthly actual', 'ln'], [C.accent, 'opex, annual ÷ 12 (dashed)', 'ln']]);
      return [
        { say: 'Operations. The green line is oil, the blue area is produced water, and orange is field operating cost per month. In 2018 and 2019, with TEC-10 and TEC-2 on, the field cost seventy to eighty thousand dollars a month to run.', run: f => ch.revealTo(ymd('2020-01'), f ? 0 : 3000) },
        { say: 'Then the costs came down by two thirds, to about twenty four thousand dollars a month in mid 2020, while oil held and water actually rose.', run: f => ch.revealTo(ymd('2022-01'), f ? 0 : 3000) },
        { say: 'The reason is water. From August 2019 the produced water went down TEC-7 as an injector instead of onto trucks, which ended trucking and disposal fees. Rented separators and pumps were returned, a flowline joined TEC-10 to TEC-2, and one supervision contract replaced the site engineers. After the 2022 shut-in the field cost twenty to fifty thousand dollars a month to hold.', run: f => ch.revealAll(f ? 0 : 2500) }
      ];
    }
  };

  // ---------------------------------------------------------------- cost structure: lean month and drilling costs
  P.costs = {
    id: 'costs', title: 'What things cost here', section: 'Operations',
    build(el) {
      const body = std(el, { eyebrow: 'Cost breakdown', title: 'A lean field costs about USD 28 k a month; a well costs 2–3 MM', src: 'Sep 2020 cost sheet (MXN at the 21 MXN/USD stated in the sheet); Dec 2023 tax-pool schedule; TEC-11 cost summary (4.40 MM incl. 0.96 MM Workstrings invoices of unknown status, G-64). drilling_costs.json, opex_breakdown.json.' });
      const ob = D.opex_breakdown?.sep_2020_cost_sheet?.items || [];
      const short = s => s.replace(/\s*\(.*\)/, '').replace('Crew / field supervision', 'Crew and supervision');
      body.innerHTML = `<div class="row" style="gap:60px;align-items:flex-start"><div class="col" style="width:780px">${S(0, `<h3>Operating cost, Sep 2020 run-rate · USD/month</h3><div id="c1"></div><p style="font-size:22px">Total 28,155. Excludes G&amp;A and area charges (USD 5.2 k/month as paid).</p>`)}</div>
        <div class="col grow">${S(1, `<h3>Capital per well, tax basis · USD MM</h3><div id="c2"></div>`)}${S(2, `<p style="font-size:24px">TEC-12 AFE: <b>USD 1.57 MM</b> (Nov 2020) → <b>2.04 MM</b> indexed to 2026 on the US drilling PPI. TEC-10 actually cost 2.96 MM all-in, so the high case (2.20 MM) deserves weight.</p>`)}</div></div>`;
      const c1 = hbars($('#c1', el), ob.map(i => ({ label: short(i.category), value: i.usd_per_month, color: C.accent })).sort((a, b) => b.value - a.value), { W: 780, rowH: 50, labelW: 290, max: 15000, ticks: 3, vfmt: d3.format(',.0f') });
      const aw = D.costs?.actual_wells?.tax_pool_basis?.wells || [];
      const rows = aw.filter(w => w.usd > 50000).map(w => ({ label: w.label, value: w.usd / 1e6, color: /TEC-11/.test(w.label) ? C.gas : /TEC-10/.test(w.label) ? C.oil : C.blue }));
      rows.splice(2, 0, { label: 'TEC-12 AFE (2026 $)', value: 2.04, color: '#ffcf3a' });
      const c2 = hbars($('#c2', el), rows, { W: 820, rowH: 52, labelW: 330, max: 4.0, ticks: 4, vfmt: d3.format('.2f') });
      return [
        { say: 'At its leanest, in September 2020, the field’s running cost was about twenty eight thousand dollars a month. Nearly half is the field crew and supervision, then a vacuum truck, diesel, tanks and sampling. Area charges add about five thousand two hundred a month.', run: f => c1.show(f) },
        { say: 'On capital, TEC-10 cost just under three million dollars all-in including its core, site and casing. The horizontal TEC-11 cost three and a half million on the tax basis, and up to four point four with completion invoices whose status is unresolved. The TEC-2 workovers came to under nine hundred thousand.', run: f => c2.show(f) },
        { say: 'TEC-12’s 2020 AFE was one point five seven million, which indexes to two point oh four million today. Because TEC-10 came in higher than its own budget, we carry a high case of two point two million.' }
      ];
    }
  };

  // ---------------------------------------------------------------- TEC-12 target (3-D)
  P.target = {
    id: 'target', kind: '3d', title: 'TEC-12: the target', section: 'TEC-12',
    build(el) {
      el.innerHTML = `<div class="glass pe" style="position:absolute;left:90px;top:80px;width:800px">
        <div class="eyebrow">TEC-12 · the target</div><h2 style="font-size:52px;margin-top:10px">The top of El Abra at the crest</h2>
        ${S(2, `<p style="margin-top:20px"><b>Never produced.</b> The crest wells left the top 14–27 m of El Abra unperforated; nothing has produced from −2,294 to −2,303 m anywhere.</p>`)}
        ${S(3, `<p style="margin-top:16px"><b>Oil-bearing where seen.</b> TEC-7's 1957 E-log, before production: top 7 m at Sw 0.13, porosity 0.17. TEC-9, 118 m away: top 8 m porous (~15 %), at parity with its 353 kbbl producer, cemented by PEMEX, never perforated.</p>`)}
        ${S(4, `<p style="margin-top:16px"><b>Highest on seismic.</b> −2,293 m on the PSTM: 3 m above TEC-9, 17 m above TEC-10.</p>`)}
        ${S(4, `<p style="margin-top:16px;color:var(--accent2)"><b>Restated target:</b> the top ~8 m of El Abra, 14–20 m higher than at TEC-10; fallback the proven interval below.</p>`)}</div>
        <div class="src">TEC-7 expediente p.85, TEC-9 1973 logs, PEMEX PSTM, RockWise XRD · docs/19, docs/20, G-47. Pads drawn schematically at the surface locations; TEC-12 path from the Feb 2021 programme. Perforations shown in orange (active) and grey (squeezed).</div><div class="pg"></div>`;
      const PADS = [{ name: 'TEC-10 / TEC-12 pad', sub: 'TEC-12 kicks off here', x: 707578, y: 2262431, w: 110, h: 90, dx: -120, dy: 30 }, { name: 'TEC-6', sub: 'plugged 2007', x: 707494, y: 2262529, w: 70, h: 70, dx: -60 },
        { name: 'TEC-2 / TEC-11 pad', x: 707596, y: 2263008, w: 100, h: 110 }, { name: 'TEC-9', sub: 'surface location', x: 707834, y: 2262336, w: 70, h: 70, dx: 40, dy: 50 }, { name: 'TEC-7', sub: 'injector', x: 707946, y: 2262706, w: 70, h: 70 }];
      const TRACES = [{ well: 'TEC-12', color: 0xff8a3d, r: 10, label: '<b>TEC-12 bottom hole</b><i>~175 m ENE of the pad</i>', dx: -30, dy: -24 }, { well: 'TEC-9', color: 0xd6dde4, label: '<b>TEC-9 bottom hole</b>', dx: 130, dy: 10 }, { well: 'TEC-10', color: 0xd6dde4, label: '<b>TEC-10 bottom hole</b>', dy: 60 }, { well: 'TEC-11', color: 0xb9a6ff, label: '<b>TEC-11 lateral</b>' }];
      scene(ctx, { year: 2026.8, highlight: 'TEC-12', dim: true, columns: false, target: { well: 'TEC-12', z: 2293, label: '<b>TEC-12 reaches the crest</b><i>top El Abra −2,293 m, the highest point on the PSTM</i>' }, surfaceOpacity: 0.4, shift: [0.2, 0], pads: PADS, labels: false, traces: TRACES, override: { 'TEC-10': { status: 'restorable' }, 'TEC-2': { status: 'restorable' } } });
      F.flyTo(F.P(707640, 2262640, 0), 3200, -0.15, 1.25, ctx.fast ? 0 : 2400);
      return [
        { say: 'So to TEC-12, starting at the surface. These are the well pads. TEC-12 is drilled from the existing TEC-10 pad, beside the old TEC-6 location, so there is no new lease, road or flowline. From there it is a deviated S-shaped well: it kicks off and steps out about a hundred and seventy five metres east-north-east to the crest, finishing between TEC-6, TEC-9 and TEC-10.', run: f => F.flyTo(F.P(707660, 2262480, 0), 1900, -0.15, 1.2, f ? 0 : 3000) },
        { say: 'Follow the well down. The target is the top of El Abra at the crest, about two thousand three hundred metres below sea level.', run: f => { F.labelsOn = true; F.showSurface(true, 0.92); F.focusWell('TEC-12', f ? 0 : 3200, { dist: 1500, az: -1.15, el: 0.36, lift: 0 }); } },
        { say: 'First, it has never been produced. Every crest well perforated below the top fourteen to twenty seven metres of the reef, chasing the water upward from below. Nothing anywhere has produced from minus two thousand two hundred and ninety four to minus two thousand three hundred and three.', run: f => F.focusWell('TEC-9', f ? 0 : 2400, { dist: 1300, az: -0.4, el: 0.2, lift: 0 }) },
        { say: 'Second, where that top unit has been logged it is oil-bearing. PEMEX’s 1957 electric log in TEC-7, run before any production, shows the top seven metres at thirteen percent water saturation and seventeen percent porosity. TEC-9, a hundred and eighteen metres away, shows its top eight metres porous and at the same saturation as the interval that made three hundred and fifty thousand barrels. PEMEX cemented it and never perforated it.' },
        { say: 'Third, it is the highest point on the seismic. So the target is the top eight metres or so of El Abra, reached fourteen to twenty metres higher than at TEC-10, with the proven interval below as the fallback.', run: f => F.focusWell('TEC-12', f ? 0 : 2400, { dist: 1150, az: -0.95, el: 0.42, lift: 0 }) }
      ];
    }
  };

  // ---------------------------------------------------------------- TEC-12 design and AFE
  P.design = {
    id: 'design', title: 'TEC-12: the well', section: 'TEC-12',
    build(el) {
      const body = std(el, { eyebrow: 'TEC-12 · the well', title: 'An appraisal-producer that measures before it perforates', src: 'TEC-12 drilling and completion programmes (2021); AFE (Nov 2020) by category and by day, indexed ×1.297 (FRED PCU213111213111); forecast docs/06; GLJ report 25269. drilling_costs.json.' });
      const af = D.costs?.tec12_afe || {};
      body.innerHTML = `<div class="row" style="gap:56px;align-items:flex-start"><div class="col" style="width:820px">
        ${S(1, `<table class="st"><tr><th>Item</th><th>Plan</th></tr><tr><td>Trajectory</td><td>S-shape from the TEC-10 pad, 175 m ENE; El Abra at −2,296 (2,323 mMD); TD 2,360 mMD</td></tr>
          <tr><td>Casing</td><td>7 in to TD; about 13 rig days</td></tr><tr><td>Data first</td><td>Density–neutron–PE, resistivity, image log over −2,290 to −2,335; pressures; bottom-hole fluid sample</td></tr>
          <tr><td>Decision rule</td><td>Perforate the window on low clay and hydrocarbon; otherwise −2,311 to −2,332</td></tr><tr><td>Forecast</td><td>Base 180 bbl/d, EUR 218 kbbl on TEC-10's decline; GLJ 1P/2P/3P EUR 250/399/578 kbbl</td></tr></table>`)}</div>
        <div class="col grow">${S(2, `<h3>AFE by category · USD k, Nov 2020</h3><div id="afe1"></div><p style="font-size:22px">Total 1,573 k → <b>2,040 k</b> in 2026 dollars.</p>`)}</div></div>`;
      const b = hbars($('#afe1', el), (af.by_category || []).map(c => ({ label: c.label, value: c.usd_2020 / 1000, color: C.accent })), { W: 760, rowH: 50, labelW: 280, max: 480, ticks: 4, vfmt: d3.format(',.0f') });
      return [
        { say: 'The well itself is conventional: an S-shaped deviated well from the TEC-10 pad, about thirteen rig days, seven-inch casing to total depth.' },
        { say: 'What makes it an appraisal well is the data. Before anything is perforated it logs density, neutron, photo-electric factor, resistivity and an image across the whole window, takes formation pressures and a bottom-hole sample. The decision rule is simple: if the top unit shows low clay and hydrocarbon, perforate it; otherwise complete in the proven interval below.' },
        { say: 'The AFE is dominated by the rig, tubulars and mud. One point five seven million in 2020, two point oh four million today.', run: f => b.show(f) }
      ];
    }
  };

  // ---------------------------------------------------------------- risks
  P.risks = {
    id: 'risks', title: 'TEC-12: the risks', section: 'TEC-12',
    build(el) {
      const body = std(el, { eyebrow: 'TEC-12 · the risks', title: 'Each risk has a measurement in the programme', src: 'July 2019 Tonalli deck, PEMEX TEC-2 reports, TEC-12 drilling programme · G-47, G-63, G-75.' });
      const R = [['Top unit thin or shaly', 'The marl thickens off the crest: nil at TEC-9, 17 m at TEC-10', 'Density–neutron–PE and image log before completion'], ['Transition zone', 'Operator 2019: free-water level may have risen from −2,380 to ~−2,316', 'Resistivity, pressures and a fluid sample; perforate on the data'], ['Gas at the crest', 'TEC-2 1956 top test GOR ~6,500 scf/bbl; PEMEX gas–oil level ~−2,315 (1971)', 'Neutron–density crossover and the sample'], ['Water coning', 'Strong aquifer; every well watered out', 'Low drawdown, TEC-7 disposal, solvent clean-ups'], ['Execution', 'TEC-11 lost its lateral; TEC-6 on the pad has a parted casing', 'Conventional S-well, anti-collision plan, 7 in to TD']];
      body.innerHTML = `<table class="st">${'<tr><th style="width:22%">Risk</th><th style="width:40%">Evidence</th><th>How the well answers it</th></tr>'}${R.map((r, i) => `<tr data-step="${i}"><td><b>${r[0]}</b></td><td>${r[1]}</td><td>${r[2]}</td></tr>`).join('')}</table>`;
      return [
        { say: 'The risks, and how the programme answers each one. The top unit could be thin or shaly, because the marl thickens off the crest. The logs answer that before completion.' },
        { say: 'There may be a transition zone: in 2019 the operator thought the free-water level might have risen. Resistivity, pressures and the sample answer it, and nothing is perforated until they do.' },
        { say: 'There was gas at the crest in 1956. Neutron–density and the sample answer that.' },
        { say: 'Water coning is a certainty in this field, managed with low drawdown, in-field disposal and solvent clean-ups.' },
        { say: 'And execution: TEC-11 lost its lateral, and TEC-6 on the same pad has a parted casing. TEC-12 is a conventional S-well with an anti-collision plan.' }
      ];
    }
  };

  // ---------------------------------------------------------------- reserves
  P.reserves = {
    id: 'reserves', title: 'Reserves', section: 'Reserves',
    build(el) {
      const body = std(el, { eyebrow: 'Reserves', title: 'Bookings rest almost entirely on TEC-12', src: 'GLJ reports YE2018–YE2025 (25269 for Kinjal Gas); CNH reserves table at 1 Jan 2015. kbbl at 100 % (YE2018 gross lease); NPV10 before tax, USD MM.' });
      const R = [['Jan 2015, PEMEX', 0, 0, 100, '–'], ['YE2018, gross', 1466, 1892, 2309, '–'], ['YE2019', 74, 847, 1195, '6.5'], ['YE2020', 326, 862, 1238, '7.5'], ['YE2021', 329, 885, 1279, '9.9'], ['YE2022', 355, 917, 1313, '10.7'], ['YE2023 (PRMS)', 353, 918, 1408, '10.4'], ['YE2025, Kinjal', 348, 903, 1383, '8.1']];
      body.innerHTML = `<div class="row" style="gap:56px;align-items:flex-start"><div style="width:980px">${S(0, `<table class="st"><tr><th>Effective</th><th style="text-align:right">1P</th><th style="text-align:right">2P</th><th style="text-align:right">3P</th><th style="text-align:right">2P NPV10</th></tr>${R.map((r, i) => `<tr class="${i === R.length - 1 ? 'hl' : ''}"><td>${r[0]}</td><td class="n">${d3.format(',')(r[1])}</td><td class="n">${d3.format(',')(r[2])}</td><td class="n">${d3.format(',')(r[3])}</td><td class="n">${r[4]}</td></tr>`).join('')}</table>`)}</div>
        <div class="col grow">${S(1, `<p>No producing reserves since YE2022. TEC-12 has been GLJ's main undeveloped entity since YE2020: EUR <b>250 / 399 / 578 kbbl</b>.</p>`)}${S(2, `<p>Our base case, calibrated on TEC-10's own decline, is <b>218 kbbl</b>. GLJ still carries TEC-10 at a 300 kbbl 2P EUR against 77 kbbl produced, so GLJ's type well looks generous.</p>`)}</div></div>`;
      return [
        { say: 'Reserves. GLJ has evaluated the field every year since 2018. At year-end 2025, for Kinjal, it carries three hundred and forty eight thousand barrels proved, nine hundred and three thousand proved plus probable, and one point three eight million possible.' },
        { say: 'There have been no producing reserves since 2022. Almost all of it is TEC-12, which GLJ books at two fifty, four hundred and five seventy eight thousand barrels.' },
        { say: 'Our own base case for TEC-12 is lower, two hundred and eighteen thousand barrels, because we calibrate on TEC-10’s actual decline. That is the number the economics use.' }
      ];
    }
  };

  // ---------------------------------------------------------------- economics
  P.economics = {
    id: 'economics', title: 'Economics', section: 'Economics',
    build(el) {
      const body = std(el, { eyebrow: 'Economics', title: 'TEC-12 pays for an owner already running the field', src: 'GLJ 1 Oct 2026 price deck, realised 0.81 × WTI (37 PEMEX settlements), contract fiscal terms (31.22 % bid royalty, basic royalty, 30 % tax), costs +2 %/yr, AFE 2.04 MM; area charges as paid. src/econ_rebuild.py, docs/10.' });
      const cs = D.econ.cases, v = k => cs[k].npv10_btax / 1e6;
      body.innerHTML = `<div class="row" style="gap:56px;align-items:flex-start"><div class="col" style="width:900px">${S(0, `<h3>NPV10 before tax, USD MM</h3><div id="ec1"></div>`)}</div>
        <div class="col grow" style="gap:30px">${S(1, `<div class="kpi"><div class="v" style="color:var(--oil)">+0.47<small>MM</small></div><div class="l">incremental base: +0.11 after tax; payout 27 months; IRR 29 %</div></div>`)}
        ${S(2, `<div class="kpi"><div class="v" style="color:var(--gas)">−0.57<small>MM</small></div><div class="l">stand-alone, carrying all field costs and area charges</div></div>`)}
        ${S(3, `<div class="kpi"><div class="v">66 / 86</div><div class="l">flat-WTI break-even, USD/bbl, incremental / stand-alone</div></div>`)}</div></div>`;
      const rows = [['Incremental, high', v('high_bpd|incremental')], ['Incremental, base', v('base_bpd|incremental')], ['Incremental, low', v('low_bpd|incremental')], ['Stand-alone, high', v('high_bpd|stand-alone')], ['Stand-alone, base', v('base_bpd|stand-alone')], ['Stand-alone, low', v('low_bpd|stand-alone')]];
      const b = hbars($('#ec1', el), rows.map(([l, x]) => ({ label: l, value: x, color: x >= 0 ? C.oil : C.gas, text: (x >= 0 ? '+' : '') + d3.format('.2f')(x) })), { W: 900, rowH: 64, labelW: 290, ticks: 6, vfmt: d3.format('.2f'), m: { r: 90 } });
      return [
        { say: 'Economics, on GLJ’s October 2026 price deck, at the realised eighty one percent of WTI, with the contract’s royalties and tax.', run: f => b.show(f) },
        { say: 'The key distinction is incremental versus stand-alone. For an owner already running the field, with TEC-10 back on and carrying the battery, disposal and area charges, TEC-12 adds about point four seven million dollars of NPV before tax, pays out in twenty seven months, at a twenty nine percent rate of return.' },
        { say: 'As a stand-alone project carrying the whole field’s costs it is negative, minus point five seven million. That is why TEC-10 and TEC-2 coming back on matters.' },
        { say: 'Flat-price break-evens are sixty six dollars WTI incremental and eighty six stand-alone.' }
      ];
    }
  };

  // ---------------------------------------------------------------- bridge to GLJ
  P.bridge = {
    id: 'bridge', title: 'Bridge to GLJ', section: 'Economics',
    build(el) {
      const body = std(el, { eyebrow: 'Against GLJ’s booking', title: 'The gap to GLJ is cost basis, not volume', src: 'src/econ_rebuild.py bridge (bridge.csv); GLJ Jan 2026 price deck; GLJ report 25269 (TEC-12 1P entity NPV10 BT USD 2.08 MM) · figure 24.' });
      body.innerHTML = `<div id="br"></div>${S(1, `<p style="max-width:1600px">GLJ's TEC-12 1P entity is worth <b>USD 2.08 MM</b>. Rebuilt step by step from our 0.47 MM, the big step is costs: GLJ charges nothing for water handling, while ours charges water at 40–85 % cut, as the 2020–21 actuals did.</p>`)}`;
      const B = D.econ.bridge; const lab = ['Ours, incremental', 'GLJ price deck', 'GLJ timing', 'GLJ capex', 'GLJ costs', 'GLJ type well'];
      const rows = B.map((r, i) => ({ label: lab[i] || r.step.slice(0, 20), value: i === 0 ? r.npv10_btax / 1e6 : r.delta / 1e6, kind: i === 0 ? 'total' : 'step' }));
      rows.push({ label: 'Rebuilt GLJ', value: B[B.length - 1].npv10_btax / 1e6, kind: 'total', color: '#ffcf3a' });
      const wf = waterfall($('#br', el), rows, { W: 1680, H: 560, ylabel: 'NPV10 BT, USD MM' });
      return [
        { say: 'GLJ values the same well at about two point oh eight million. We can rebuild their number from ours, one assumption at a time. Price deck and timing are small. Their capex is a little lower. Their type well adds about half a million.', run: f => wf.show(f) },
        { say: 'The big step, one and a half million, is operating cost: GLJ charges nothing for water handling, while we charge for water at forty to eighty five percent cut, as the actual 2020 and 2021 costs did. Both cases are internally consistent; ours is the more conservative.' }
      ];
    }
  };

  // ---------------------------------------------------------------- netback history
  P.netback = {
    id: 'netback', title: 'Netback history', section: 'Economics',
    build(el) {
      const body = std(el, { eyebrow: 'Commercial history', title: 'Two wells could not carry the field alone', src: 'Field lease operating statements; USD thousands except per barrel; *2018 is Sep–Dec · acc_findings.md. LOS reconcile to PEMEX settlements (exact 2020–21, within 0.6 % in 2022). Sales point: CNH Nov 2022 monthly format and DGM balances (wells_ops_reserves_notes.md).' });
      const R = [['2018*', 15209, 917, 382, 291], ['2019', 32702, 1732, 706, 839], ['2020', 19041, 682, 283, 336], ['2021', 17546, 939, 394, 349], ['2022', 2756, 178, 89, 168], ['2023', 530, 30, 17, 627]];
      body.innerHTML = `<div class="row" style="gap:50px;align-items:flex-start"><div id="nb" style="width:1100px"></div>
        <div class="col grow" style="gap:24px">${S(1, `<div class="kpi"><div class="v" style="color:var(--accent2)">≈ 0</div><div class="l">2018–23 revenue less royalties, fees and opex, before G&amp;A and about USD 7.6 MM of capital</div></div>`)}
        ${S(2, `<p>Royalties and fees took 41–56 % of revenue. A crestal well with a low water cut changes that ratio; more water does not.</p>`)}
        ${S(0, `<p style="font-size:23px;color:var(--ink2)"><b>Sales point:</b> trucked to PEMEX <b>CAB Poza Rica</b> (Central de Almacenamiento y Bombeo; fiscal turbine meter), delivered at the Ezequiel Ordóñez pumping station, La Guásima, Papantla. Price 0.81 × WTI (2020–22), tariffs 2.7–3.3 USD/bbl.</p>`)}</div></div>`;
      const v = vstack($('#nb', el), R.map(r => ({ label: r[0], parts: [{ key: 'roy', value: r[3], color: '#9a7fe0' }, { key: 'opex', value: r[4], color: C.accent }, { key: 'net', value: Math.max(0, r[2] - r[3] - r[4]), color: C.oil }] })), { W: 1100, H: 560, ylabel: 'USD thousands', totfmt: d3.format(',') });
      legend($('#nb', el), [['#9a7fe0', 'royalties and fees'], [C.accent, 'field opex'], [C.oil, 'left over (net)']]);
      return [
        { say: 'Here is the field’s commercial record under Tonalli, from the lease operating statements. The crude was trucked to PEMEX’s Central de Almacenamiento y Bombeo, the CAB Poza Rica, where it is measured on the fiscal meter and sold, through the Ezequiel Ordóñez pumping station at La Guásima, Papantla. Each bar is a year: royalties and fees, operating cost, and what was left. Over 2018 to 2023, revenue less royalties and opex is about zero, before overheads and seven point six million dollars of capital.', run: f => v.show(f) },
        { say: 'Royalties and fees took forty one to fifty six percent of revenue. Put plainly: two watered-out wells could not carry the field.' },
        { say: 'What changes the ratio is a well with a low water cut at the crest. More of the same water does not.' }
      ];
    }
  };

  // ---------------------------------------------------------------- commercial
  P.commercial = {
    id: 'commercial', title: 'Contract and regulatory', section: 'Commercial',
    build(el) {
      const body = std(el, { eyebrow: 'Contract and regulatory', title: 'A long licence with items to settle', src: 'Licence contract, 2017 evaluation plan, LSH (DOF 18-03-2025), Tonalli P&L, GLJ YE2025 · G-49, G-60, G-64 to G-67.' });
      const K = [['Licence', 'CNH-R01-L03-A24/2016, 7.16 km². Term to Aug 2041 plus two 5-year extensions; guarantee USD 1.76 MM; pre-reform terms kept by the 2025 law.'], ['Fiscal and offtake', '31.22 % bid royalty plus basic royalty; 30 % tax; area charges ~USD 5.2 k/month. Crude trucked to PEMEX CAB Poza Rica (fiscal meter) at 0.81 × WTI.'], ['To settle before closing', 'CNH consent to the change of control (clause 23.2). Shut-in cause and date: GLJ says permit, early 2023; filings say February/July 2022.'], ['Exposures', 'Flaring justified at GOR 337 scf/bbl against 742–859 measured; ~0.96 MM of TEC-11 invoices of unknown status; abandonment reserve USD 411 k.']];
      body.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:28px">${K.map((k, i) => S(i, `<div class="card" style="height:100%"><h3>${k[0]}</h3><p style="margin-top:12px">${k[1]}</p></div>`)).join('')}</div>`;
      return [
        { say: 'On the contract: a Round one point three licence to 2041 with two five-year extensions, and the 2025 hydrocarbons law keeps its terms.' },
        { say: 'The fiscal take is a thirty one percent bid royalty plus the basic royalty and thirty percent tax. Crude is trucked to PEMEX’s CAB Poza Rica storage and pumping centre and sold at about eighty one percent of WTI.' },
        { say: 'Before closing, the change of control needs regulator consent, and the shut-in cause and date need reconciling: GLJ says a permit issue in early 2023, the filings say 2022.' },
        { say: 'And three exposures to price in: the flaring basis, about a million dollars of TEC-11 invoices of unknown status, and the abandonment reserve.' }
      ];
    }
  };

  // ---------------------------------------------------------------- close (3-D)
  P.close = {
    id: 'close', kind: '3d', title: 'What TEC-12 settles', section: 'Close',
    build(el) {
      el.innerHTML = `<div class="glass pe" style="position:absolute;left:90px;top:90px;width:1000px;padding:44px 50px">
        <div class="eyebrow">The next step</div><h2 style="margin-top:10px">What TEC-12 settles</h2>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px 40px;margin-top:30px">
        ${S(1, `<h3>The crest's top unit</h3><p style="font-size:24px">Thickness, clay and saturation of the top ~8 m of El Abra, never produced.</p>`)}
        ${S(2, `<h3>Contact and gas</h3><p style="font-size:24px">Today's water level and any crestal gas, from pressures and logs.</p>`)}
        ${S(3, `<h3>The first PVT</h3><p style="font-size:24px">A bottom-hole sample, replacing correlations.</p>`)}
        ${S(4, `<h3>The reserves basis</h3><p style="font-size:24px">Modern petrophysics behind the 4 MMbbl in-place range and GLJ's type well.</p>`)}</div>
        ${S(5, `<p style="margin-top:30px;font-family:var(--serif);font-size:36px;line-height:1.35;color:var(--ink)">One well, about USD 2 MM, at the highest unproduced El Abra in the field, with a proven interval below as the fallback.</p>`)}</div>
        <div class="src">Data package and gap register available on request · this presentation: Presentation, Field in 3-D and Data tabs</div><div class="pg"></div>`;
      scene(ctx, { year: 2026.8, focus: 'TEC-12', focusOpts: { dist: 3200, az: 0.9, el: 0.35, lift: 200 }, highlight: 'TEC-12', orbit: true, orbitSpeed: 0.3, shift: [0.22, 0], override: { 'TEC-10': { status: 'restorable' }, 'TEC-2': { status: 'restorable' } } });
      return [
        { say: 'To close. TEC-12 settles four things at once.' },
        { say: 'Whether the top unit of the reef at the crest is there, clean and oil-bearing.' },
        { say: 'Where the water is today, and whether there is gas at the top.' },
        { say: 'The field’s first fluid sample.' },
        { say: 'And the petrophysics behind a four million barrel range in oil in place, and behind the reserves.' },
        { say: 'One well, about two million dollars, at the highest unproduced El Abra in the field, with a proven interval below as the fallback. Thank you.' }
      ];
    }
  };
  return P;
}
