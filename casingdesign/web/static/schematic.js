// Well schematic (SVG) and pressure-window chart (Plotly) that redraw from the well object.
const Schematic = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const el = (t, a = {}, ...k) => { const e = document.createElementNS(NS, t); for (const [x, y] of Object.entries(a)) e.setAttribute(x, y); for (const c of k) e.append(c); return e; };

  // Minimum-curvature TVD for MD, reproducing the engine for display purposes.
  function tvdFn(stations) {
    const st = [...stations].sort((a, b) => a.md - b.md); if (!st.length || st[0].md !== 0) st.unshift({md: 0, inclination: 0, azimuth: 0});
    const tvd = [0];
    for (let i = 1; i < st.length; i++) {
      const i1 = st[i - 1].inclination * Math.PI / 180, i2 = st[i].inclination * Math.PI / 180, a1 = st[i - 1].azimuth * Math.PI / 180, a2 = st[i].azimuth * Math.PI / 180;
      const cosdl = Math.cos(i2 - i1) - Math.sin(i1) * Math.sin(i2) * (1 - Math.cos(a2 - a1)); const dl = Math.acos(Math.max(-1, Math.min(1, cosdl)));
      const rf = dl < 1e-9 ? 1 : 2 / dl * Math.tan(dl / 2);
      tvd.push(tvd[i - 1] + (st[i].md - st[i - 1].md) / 2 * (Math.cos(i1) + Math.cos(i2)) * rf);
    }
    return md => { if (md <= st[0].md) return tvd[0]; for (let i = 1; i < st.length; i++) if (md <= st[i].md) { const f = (md - st[i - 1].md) / (st[i].md - st[i - 1].md); return tvd[i - 1] + f * (tvd[i] - tvd[i - 1]); } return tvd.at(-1) + (md - st.at(-1).md) * Math.cos(st.at(-1).inclination * Math.PI / 180); };
  }

  // Draw strings against MD (so laterals have length). Widths scale with OD.
  function draw(container, well) {
    const strings = (well.strings || []).filter(s => s.shoe_md > 0 && s.od > 0);
    const W = 340, H = 440, top = 26, bottom = H - 16, cx = 120;
    const maxMd = Math.max(1, ...strings.map(s => s.shoe_md), well.trajectory.stations.at(-1)?.md || 0);
    const y = md => top + (bottom - top) * md / maxMd;
    const maxOd = Math.max(...strings.map(s => Math.max(s.od, s.hole_size || 0)), 10);
    const hw = od => Math.max(3, od / maxOd * 60);
    const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, class: 'schematic', role: 'img', 'aria-label': 'well schematic'});
    svg.append(el('line', {x1: 10, x2: W - 10, y1: top, y2: top, class: 'ground'}));
    const sorted = [...strings].sort((a, b) => b.od - a.od);
    for (const s of sorted) {
      const hole = hw(s.hole_size || s.od + 1.5), od = hw(s.od), yt = y(s.hanger_md || 0), ys = Math.max(y(s.shoe_md), yt + 1), ytoc = Math.min(ys, y(Math.max(s.toc_md || 0, s.hanger_md || 0)));
      svg.append(el('rect', {x: cx - hole, y: yt, width: 2 * hole, height: ys - yt, class: 'hole'}));
      svg.append(el('rect', {x: cx - hole, y: ytoc, width: 2 * hole, height: ys - ytoc, class: 'cement'}));
      svg.append(el('rect', {x: cx - od, y: yt, width: 2 * od, height: ys - yt, class: 'casing' + (s.type === 'liner' ? ' liner' : '')}));
      const t = el('text', {x: cx + hole + 6, y: ys - 2, class: 'lbl'}); t.textContent = `${s.od}" ${s.type === 'liner' ? 'liner' : 'csg'} @ ${Math.round(s.shoe_md).toLocaleString()}'`; svg.append(t);
      if (s.type === 'liner') { const t2 = el('text', {x: cx + hole + 6, y: yt + 10, class: 'lbl muted'}); t2.textContent = `top ${Math.round(s.hanger_md).toLocaleString()}'`; svg.append(t2); }
    }
    const ax = el('text', {x: 10, y: 14, class: 'lbl muted'}); ax.textContent = 'MD, not to scale across OD'; svg.append(ax);
    container.replaceChildren(svg);
  }

  function pressureWindow(container, well) {
    if (!window.Plotly) return;
    const f = well.formation, tvd = tvdFn(well.trajectory.stations);
    const pp = f.pore_pressure.points, fg = f.fracture_gradient.points;
    const maxTvd = Math.max(...pp.map(p => p.tvd), ...fg.map(p => p.tvd), ...well.strings.map(s => tvd(s.shoe_md)), 1000);
    const traces = [
      {x: pp.map(p => p.value), y: pp.map(p => p.tvd), name: 'Pore pressure', mode: 'lines+markers', line: {color: '#1f5fbf'}},
      {x: fg.map(p => p.value), y: fg.map(p => p.tvd), name: 'Fracture gradient', mode: 'lines+markers', line: {color: '#c0392b'}},
    ];
    const prev = {};
    for (const s of well.strings) {
      const t0 = tvd(s.hanger_md || 0), t1 = tvd(s.shoe_md);
      traces.push({x: [s.mud_weight, s.mud_weight], y: [t0, t1], name: `${s.name} mud ${s.mud_weight} ppg`, mode: 'lines', line: {color: '#1e8e4f', width: 3}});
      traces.push({x: [0, 25], y: [t1, t1], mode: 'lines', showlegend: false, line: {color: '#888', dash: 'dot', width: 1}, hoverinfo: 'skip'});
      if (s.next_hole_mud_weight && s.next_section_td_md) traces.push({x: [s.next_hole_mud_weight, s.next_hole_mud_weight], y: [t1, tvd(s.next_section_td_md)], name: `next section ${s.next_hole_mud_weight} ppg`, mode: 'lines', line: {color: '#16a085', width: 3, dash: 'dash'}});
    }
    const allx = traces.flatMap(t => t.x).filter(x => x > 0 && x < 25);
    Plotly.newPlot(container, traces, {margin: {l: 55, r: 10, t: 10, b: 45}, height: 440, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: {color: getComputedStyle(document.body).color, size: 11},
      xaxis: {title: 'Equivalent mud weight (ppg)', range: [Math.min(...allx) - 1, Math.max(...allx) + 1], gridcolor: 'rgba(128,128,128,.25)'},
      yaxis: {title: 'TVD (ft)', range: [maxTvd * 1.03, 0], gridcolor: 'rgba(128,128,128,.25)'}, legend: {orientation: 'h', y: -0.18, font: {size: 10}}}, {responsive: true, displaylogo: false, staticPlot: false});
  }

  return {draw, pressureWindow, tvdFn};
})();
