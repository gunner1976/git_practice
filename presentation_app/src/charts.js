// ---------------------------------------------------------------- charts (D3 v7 global), drawn at stage scale (1920 x 1080 px)
const d3 = window.d3;
export const C = {
  ink: '#ece6db', ink2: '#aab4bf', ink3: '#7d8894', grid: '#2a3542', bg: '#0f151c', panel: '#161f29',
  oil: '#5dbb63', water: '#4a90d9', gas: '#e5534b', press: '#f0b44c', accent: '#e8894f', blue: '#5b9bd5', grey: '#6b7682', violet: '#a58ae0',
  wells: { 'TEC-2': '#4a90d9', 'TEC-6': '#e8894f', 'TEC-7': '#2fb38a', 'TEC-9': '#e0b341', 'TEC-10': '#e87ba4', 'TEC-11': '#9a7fe0', FIELD: '#9aa6b2' }
};
const FONT = "'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif", MONO = "'IBM Plex Mono', ui-monospace, Menlo, monospace";
export const fmt = { int: d3.format(',.0f'), k: d3.format(',.0f'), one: d3.format(',.1f'), two: d3.format(',.2f'), pct: d3.format('.0%') };

function frame(host, W, H, m) {
  const svg = d3.select(host).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H).attr('class', 'chart')
    .style('font-family', FONT).style('overflow', 'visible');
  const g = svg.append('g').attr('transform', `translate(${m.l},${m.t})`);
  return { svg, g, w: W - m.l - m.r, h: H - m.t - m.b };
}
function axisStyle(sel, size = 22) {
  sel.selectAll('text').attr('fill', C.ink2).style('font-size', size + 'px').style('font-family', FONT);
  sel.selectAll('line').attr('stroke', C.grid); sel.selectAll('path.domain').attr('stroke', C.grid);
}
function label(g, x, y, txt, o = {}) {
  return g.append('text').attr('x', x).attr('y', y).text(txt).attr('fill', o.fill || C.ink2).style('font-size', (o.size || 22) + 'px')
    .attr('text-anchor', o.anchor || 'start').attr('font-weight', o.weight || 400).style('font-family', o.mono ? MONO : FONT)
    .attr('dominant-baseline', o.base || 'auto').attr('transform', o.rot ? `rotate(${o.rot},${x},${y})` : null);
}
export function legend(host, items, o = {}) {
  const el = document.createElement('div'); el.className = 'legend' + (o.cls ? ' ' + o.cls : '');
  el.innerHTML = items.map(([c, t, kind]) => `<span><i class="${kind || 'sw'}" style="--c:${c}"></i>${t}</span>`).join(''); host.append(el); return el;
}

// ---------------------------------------------------------------- time series with progressive reveal
// series: [{key, label, color, values:[{d:Date, v}], type:'line'|'area'|'step', axis:'l'|'r', width, dash}], stack: [{key,color,label,values}] (stacked area)
export function timeChart(host, o) {
  const W = o.W || 1600, H = o.H || 600, m = Object.assign({ l: 96, r: o.right ? 96 : 30, t: 30, b: 56 }, o.m || {});
  const { svg, g, w, h } = frame(host, W, H, m);
  const x = d3.scaleTime().domain(o.x).range([0, w]);
  const y = o.ylog ? d3.scaleLog().domain(o.yl).range([h, 0]) : d3.scaleLinear().domain(o.yl).range([h, 0]);
  const yr = o.right ? d3.scaleLinear().domain(o.yr).range([h, 0]) : null;
  g.append('g').attr('class', 'grid').call(d3.axisLeft(y).ticks(o.yticks || 5, o.ylog ? '~s' : undefined).tickSize(-w).tickFormat('')).call(s => { s.selectAll('line').attr('stroke', C.grid).attr('stroke-opacity', 0.7); s.select('.domain').remove(); });
  const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(o.xticks || 10).tickSizeOuter(0)); axisStyle(ax);
  const ay = g.append('g').call(d3.axisLeft(y).ticks(o.yticks || 5, o.yfmt || (o.ylog ? '~s' : ',~f')).tickSizeOuter(0)); axisStyle(ay); ay.select('.domain').remove();
  if (yr) { const ar = g.append('g').attr('transform', `translate(${w},0)`).call(d3.axisRight(yr).ticks(o.yticks || 5, o.yrfmt || ',~f').tickSizeOuter(0)); axisStyle(ar); ar.select('.domain').remove(); }
  if (o.ylabel) label(g, -72, h / 2, o.ylabel, { anchor: 'middle', rot: -90, size: 22 });
  if (o.yrlabel) label(g, w + m.r - 20, h / 2, o.yrlabel, { anchor: 'middle', rot: 90, size: 22 });
  const clipId = 'c' + Math.random().toString(36).slice(2); const clip = svg.append('clipPath').attr('id', clipId).append('rect').attr('x', 0).attr('y', -40).attr('height', h + 60).attr('width', o.reveal === false ? w : 0);
  const body = g.append('g').attr('clip-path', `url(#${clipId})`);
  // bands (e.g. shut-in eras)
  for (const b of o.bands || []) {
    body.append('rect').attr('x', x(b.from)).attr('width', Math.max(1, x(b.to) - x(b.from))).attr('y', 0).attr('height', h).attr('fill', b.color || '#ffffff').attr('opacity', b.opacity ?? 0.05);
    if (b.hatch) { const pid = 'h' + Math.random().toString(36).slice(2); const pt = svg.append('defs').append('pattern').attr('id', pid).attr('width', 10).attr('height', 10).attr('patternUnits', 'userSpaceOnUse').attr('patternTransform', 'rotate(45)'); pt.append('line').attr('y2', 10).attr('stroke', b.hatch).attr('stroke-width', 3).attr('stroke-opacity', 0.45);
      body.append('rect').attr('x', x(b.from)).attr('width', Math.max(1, x(b.to) - x(b.from))).attr('y', 0).attr('height', h).attr('fill', `url(#${pid})`); }
    if (b.label) label(g, (x(b.from) + x(b.to)) / 2 + (b.vertical ? 6 : 0), b.ly ?? h / 2, b.label, { anchor: 'middle', size: b.size || 18, fill: b.lcolor || C.ink2, rot: b.vertical ? -90 : 0 }).attr('paint-order', 'stroke').attr('stroke', C.bg).attr('stroke-width', 5);
  }
  if (o.stack) {
    const keys = o.stack.map(s => s.key), dates = o.stackDates;
    const rows = dates.map((d, i) => { const r = { d }; for (const s of o.stack) r[s.key] = s.values[i] || 0; return r; });
    const st = d3.stack().keys(keys)(rows);
    const area = d3.area().curve(d3.curveStepAfter).x(d => x(d.data.d)).y0(d => y(Math.max(o.ylog ? 1 : 0, d[0]))).y1(d => y(Math.max(o.ylog ? 1 : 0, d[1])));
    st.forEach((layer, i) => body.append('path').datum(layer).attr('d', area).attr('fill', o.stack[i].color).attr('opacity', 0.92));
  }
  for (const s of o.series || []) {
    const sc = s.axis === 'r' ? yr : y, vals = s.values.filter(p => p.v != null && (!o.ylog || p.v > 0));
    if (s.type === 'dots') { body.selectAll(null).data(vals).join('circle').attr('cx', p => x(p.d)).attr('cy', p => sc(p.v)).attr('r', s.r || 7).attr('fill', s.color).attr('stroke', C.bg).attr('stroke-width', 2); continue; }
    const line = d3.line().defined(p => p.v != null && (!o.ylog || p.v > 0)).curve(s.type === 'step' ? d3.curveStepAfter : d3.curveMonotoneX).x(p => x(p.d)).y(p => sc(p.v));
    if (s.type === 'area') body.append('path').datum(s.values).attr('d', d3.area().defined(p => p.v != null).curve(d3.curveStepAfter).x(p => x(p.d)).y0(h).y1(p => sc(p.v))).attr('fill', s.color).attr('opacity', s.opacity ?? 0.35);
    body.append('path').datum(s.values).attr('d', line).attr('fill', 'none').attr('stroke', s.color).attr('stroke-width', s.width || 3).attr('stroke-dasharray', s.dash || null).attr('opacity', s.alpha ?? 1);
  }
  // event markers: [{d, text, y (0..1 from top)}]
  const ev = g.append('g');
  const evs = (o.events || []).map((e, i) => {
    const gx = ev.append('g').attr('class', 'ev').attr('opacity', 0);
    gx.append('line').attr('x1', x(e.d)).attr('x2', x(e.d)).attr('y1', 0).attr('y2', h).attr('stroke', e.color || C.ink3).attr('stroke-dasharray', '4 5').attr('stroke-width', 1.5);
    const ty = (e.y ?? (0.06 + (i % 4) * 0.075)) * h;
    const tx = label(gx, x(e.d) + (e.left ? -10 : 10), ty, e.text, { size: e.size || 21, fill: e.color || C.ink, anchor: e.left ? 'end' : 'start' });
    tx.attr('paint-order', 'stroke').attr('stroke', C.bg).attr('stroke-width', 6);
    return { e, gx };
  });
  const api = {
    x, y, yr, g, w, h, svg,
    revealTo(date, dur = 0) { const px = Math.max(0, Math.min(w, x(date))); (dur ? clip.transition().duration(dur).ease(d3.easeLinear) : clip.interrupt()).attr('width', px); evs.forEach(({ e, gx }) => gx.transition().duration(dur ? 400 : 0).attr('opacity', e.d <= date ? 1 : 0)); },
    revealAll(dur = 1600) { api.revealTo(o.x[1], dur); },
    cursor(date) { if (!api._cur) { api._cur = g.append('line').attr('y1', -10).attr('y2', h).attr('stroke', C.accent).attr('stroke-width', 2.5); } api._cur.attr('x1', x(date)).attr('x2', x(date)); }
  };
  if (o.reveal === false) evs.forEach(({ gx }) => gx.attr('opacity', 1));
  return api;
}

// ---------------------------------------------------------------- bars: rows [{label, value, color, note}] horizontal
export function hbars(host, rows, o = {}) {
  const W = o.W || 900, rowH = o.rowH || 54, H = o.H || rows.length * rowH + 60, m = Object.assign({ l: o.labelW || 300, r: 120, t: 10, b: 40 }, o.m || {});
  const { g, w, h } = frame(host, W, H, m);
  const max = o.max ?? d3.max(rows, r => r.value) * 1.05;
  const x = d3.scaleLinear().domain([Math.min(0, d3.min(rows, r => r.value)), max]).range([0, w]);
  const yb = d3.scaleBand().domain(rows.map((r, i) => i)).range([0, h]).padding(0.28);
  if (o.axis !== false) { const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(o.ticks || 5, o.tickfmt || ',~f')); axisStyle(ax); }
  const bars = g.selectAll(null).data(rows).join('g').attr('transform', (r, i) => `translate(0,${yb(i)})`);
  bars.append('text').attr('x', -16).attr('y', yb.bandwidth() / 2).attr('text-anchor', 'end').attr('dominant-baseline', 'middle').text(r => r.label).attr('fill', C.ink).style('font-size', (o.fs || 23) + 'px');
  const rect = bars.append('rect').attr('x', r => x(Math.min(0, r.value))).attr('y', 0).attr('height', yb.bandwidth()).attr('width', 0).attr('rx', 3).attr('fill', r => r.color || C.blue);
  const val = bars.append('text').attr('x', r => x(Math.max(0, r.value)) + 12).attr('y', yb.bandwidth() / 2).attr('dominant-baseline', 'middle').text(r => r.text ?? (o.vfmt || fmt.one)(r.value)).attr('fill', C.ink).style('font-size', (o.fs || 23) + 'px').style('font-family', MONO).attr('opacity', 0);
  return { show(fast) { rect.transition().duration(fast ? 0 : 900).delay((r, i) => fast ? 0 : i * 90).attr('width', r => Math.abs(x(r.value) - x(0))); val.transition().duration(fast ? 0 : 400).delay((r, i) => fast ? 0 : 500 + i * 90).attr('opacity', 1); }, x, g };
}

// stacked vertical bars: cats [{label, parts:[{key,value,color}]}]
export function vstack(host, cats, o = {}) {
  const W = o.W || 1000, H = o.H || 560, m = Object.assign({ l: 90, r: 20, t: 20, b: 64 }, o.m || {});
  const { g, w, h } = frame(host, W, H, m);
  const tot = cats.map(c => d3.sum(c.parts, p => Math.max(0, p.value)));
  const y = d3.scaleLinear().domain([0, (o.max ?? d3.max(tot)) * 1.08]).range([h, 0]);
  const x = d3.scaleBand().domain(cats.map(c => c.label)).range([0, w]).padding(0.32);
  g.append('g').call(d3.axisLeft(y).ticks(5).tickSize(-w).tickFormat('')).call(s => { s.selectAll('line').attr('stroke', C.grid); s.select('.domain').remove(); });
  const ay = g.append('g').call(d3.axisLeft(y).ticks(5, o.yfmt || ',~f')); axisStyle(ay); ay.select('.domain').remove();
  const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).tickSizeOuter(0)); axisStyle(ax, o.xfs || 22);
  if (o.ylabel) label(g, -66, h / 2, o.ylabel, { anchor: 'middle', rot: -90 });
  const rects = [];
  cats.forEach((c, ci) => { let acc = 0; c.parts.forEach(p => { const y0 = acc, y1 = acc + p.value; acc = y1; rects.push(g.append('rect').attr('x', x(c.label)).attr('width', x.bandwidth()).attr('y', h).attr('height', 0).attr('fill', p.color).datum({ y0, y1, ci })); }); });
  const tl = cats.map((c, i) => label(g, x(c.label) + x.bandwidth() / 2, y(tot[i]) - 12, (o.totfmt || fmt.int)(tot[i]), { anchor: 'middle', fill: C.ink, size: 22, mono: true }).attr('opacity', 0));
  return { show(fast) { rects.forEach(r => r.transition().duration(fast ? 0 : 800).delay(fast ? 0 : r.datum().ci * 110).attr('y', y(r.datum().y1)).attr('height', y(r.datum().y0) - y(r.datum().y1))); tl.forEach((t, i) => t.transition().delay(fast ? 0 : 600 + i * 110).attr('opacity', 1)); }, y, x, g, h };
}

// ---------------------------------------------------------------- waterfall [{label, value, kind:'total'|'step'}]
export function waterfall(host, rows, o = {}) {
  const W = o.W || 1500, H = o.H || 560, m = { l: 90, r: 20, t: 40, b: 70 };
  const { g, w, h } = frame(host, W, H, m);
  let acc = 0; const bars = rows.map(r => { if (r.kind === 'total') { const b = { ...r, y0: 0, y1: r.value }; acc = r.value; return b; } const b = { ...r, y0: acc, y1: acc + r.value }; acc += r.value; return b; });
  const y = d3.scaleLinear().domain([Math.min(0, d3.min(bars, b => Math.min(b.y0, b.y1))) - 0.2, d3.max(bars, b => Math.max(b.y0, b.y1)) * 1.15]).range([h, 0]);
  const x = d3.scaleBand().domain(rows.map(r => r.label)).range([0, w]).padding(0.3);
  g.append('g').call(d3.axisLeft(y).ticks(6).tickSize(-w).tickFormat('')).call(s => { s.selectAll('line').attr('stroke', C.grid); s.select('.domain').remove(); });
  const ay = g.append('g').call(d3.axisLeft(y).ticks(6, o.yfmt || '.1f')); axisStyle(ay); ay.select('.domain').remove();
  const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).tickSizeOuter(0)); axisStyle(ax, 21);
  ax.selectAll('text').call(t => t.each(function () { const s = d3.select(this), words = s.text().split(' '); if (words.length > 2) { s.text(''); s.append('tspan').attr('x', 0).attr('dy', '0.9em').text(words.slice(0, 2).join(' ')); s.append('tspan').attr('x', 0).attr('dy', '1.1em').text(words.slice(2).join(' ')); } }));
  g.append('line').attr('x1', 0).attr('x2', w).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', C.ink3);
  if (o.ylabel) label(g, -64, h / 2, o.ylabel, { anchor: 'middle', rot: -90 });
  const els = bars.map((b, i) => {
    const col = b.kind === 'total' ? (b.color || C.blue) : (b.value >= 0 ? C.oil : C.gas);
    const r = g.append('rect').attr('x', x(b.label)).attr('width', x.bandwidth()).attr('y', y(Math.max(b.y0, b.y1))).attr('height', 0).attr('fill', col).attr('rx', 3);
    const t = label(g, x(b.label) + x.bandwidth() / 2, y(Math.max(b.y0, b.y1)) - 12, (b.kind === 'total' ? '' : b.value >= 0 ? '+' : '') + d3.format('.2f')(b.value), { anchor: 'middle', fill: C.ink, size: 24, mono: true }).attr('opacity', 0);
    return { r, t, b };
  });
  return { show(fast) { els.forEach(({ r, t, b }, i) => { r.transition().duration(fast ? 0 : 600).delay(fast ? 0 : i * 380).attr('height', Math.abs(y(b.y0) - y(b.y1))); t.transition().delay(fast ? 0 : i * 380 + 400).attr('opacity', 1); }); } };
}

// ---------------------------------------------------------------- donut
export function donut(host, parts, o = {}) {
  const S = o.S || 420, R = S / 2 - 10; const svg = d3.select(host).append('svg').attr('viewBox', `0 0 ${S} ${S}`).attr('width', S).attr('height', S);
  const g = svg.append('g').attr('transform', `translate(${S / 2},${S / 2})`);
  const pie = d3.pie().sort(null).value(p => p.value)(parts), arc = d3.arc().innerRadius(R * 0.58).outerRadius(R);
  const paths = g.selectAll(null).data(pie).join('path').attr('fill', d => d.data.color).attr('stroke', C.bg).attr('stroke-width', 3).attr('d', d => arc({ ...d, endAngle: d.startAngle }));
  if (o.center) { g.append('text').attr('text-anchor', 'middle').attr('dy', '-0.1em').text(o.center[0]).attr('fill', C.ink).style('font-size', '44px').style('font-family', "'Source Serif 4', Georgia, serif").attr('font-weight', 600); g.append('text').attr('text-anchor', 'middle').attr('dy', '1.4em').text(o.center[1]).attr('fill', C.ink2).style('font-size', '20px'); }
  return { show(fast) { paths.transition().duration(fast ? 0 : 1100).attrTween('d', d => { const i = d3.interpolate(d.startAngle, d.endAngle); return t => arc({ ...d, endAngle: i(t) }); }); } };
}

// ---------------------------------------------------------------- histogram with P90/P50/P10 markers
export function histogram(host, bins, o = {}) {
  const W = o.W || 1000, H = o.H || 460, m = { l: 70, r: 20, t: 50, b: 64 };
  const { g, w, h } = frame(host, W, H, m);
  const x = d3.scaleLinear().domain([bins[0].x0, bins[bins.length - 1].x1]).range([0, w]);
  const y = d3.scaleLinear().domain([0, d3.max(bins, b => b.n) * 1.1]).range([h, 0]);
  const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(8)); axisStyle(ax);
  if (o.xlabel) label(g, w / 2, h + 58, o.xlabel, { anchor: 'middle' });
  const r = g.selectAll(null).data(bins).join('rect').attr('x', b => x(b.x0) + 1).attr('width', b => Math.max(1, x(b.x1) - x(b.x0) - 2)).attr('y', h).attr('height', 0).attr('fill', o.color || C.oil).attr('opacity', 0.85);
  const marks = (o.marks || []).map(mk => { const gg = g.append('g').attr('opacity', 0); gg.append('line').attr('x1', x(mk.v)).attr('x2', x(mk.v)).attr('y1', -10).attr('y2', h).attr('stroke', mk.color || C.ink).attr('stroke-width', 2.5).attr('stroke-dasharray', mk.dash || null); label(gg, x(mk.v), -18, mk.text, { anchor: 'middle', fill: mk.color || C.ink, size: 22, weight: 600 }); return gg; });
  return { show(fast) { r.transition().duration(fast ? 0 : 900).delay((b, i) => fast ? 0 : i * 12).attr('y', b => y(b.n)).attr('height', b => h - y(b.n)); marks.forEach((mm, i) => mm.transition().delay(fast ? 0 : 900 + i * 250).attr('opacity', 1)); }, x };
}

// ---------------------------------------------------------------- tornado [{label, lo, hi}] about base
export function tornado(host, rows, base, o = {}) {
  const W = o.W || 900, H = o.H || rows.length * 62 + 80, m = { l: 220, r: 40, t: 40, b: 50 };
  const { g, w, h } = frame(host, W, H, m);
  const x = d3.scaleLinear().domain([d3.min(rows, r => r.lo) - 0.5, d3.max(rows, r => r.hi) + 0.5]).range([0, w]);
  const y = d3.scaleBand().domain(rows.map(r => r.label)).range([0, h]).padding(0.3);
  const ax = g.append('g').attr('transform', `translate(0,${h})`).call(d3.axisBottom(x).ticks(6)); axisStyle(ax);
  g.append('line').attr('x1', x(base)).attr('x2', x(base)).attr('y1', -10).attr('y2', h).attr('stroke', C.ink).attr('stroke-width', 2);
  label(g, x(base), -16, `base ${base}`, { anchor: 'middle', fill: C.ink, size: 21 });
  const bars = [];
  rows.forEach(r => {
    label(g, -14, y(r.label) + y.bandwidth() / 2, r.label, { anchor: 'end', base: 'middle', fill: C.ink, size: 22 });
    bars.push([g.append('rect').attr('x', x(base)).attr('width', 0).attr('y', y(r.label)).attr('height', y.bandwidth()).attr('fill', C.gas).attr('opacity', 0.85), x(r.lo), x(base) - x(r.lo), 'lo']);
    bars.push([g.append('rect').attr('x', x(base)).attr('width', 0).attr('y', y(r.label)).attr('height', y.bandwidth()).attr('fill', C.oil).attr('opacity', 0.85), x(base), x(r.hi) - x(base), 'hi']);
    label(g, x(r.lo) - 8, y(r.label) + y.bandwidth() / 2, d3.format('.1f')(r.lo), { anchor: 'end', base: 'middle', size: 19, mono: true });
    label(g, x(r.hi) + 8, y(r.label) + y.bandwidth() / 2, d3.format('.1f')(r.hi), { base: 'middle', size: 19, mono: true });
  });
  if (o.xlabel) label(g, w / 2, h + 46, o.xlabel, { anchor: 'middle' });
  return { show(fast) { bars.forEach(([r, x0, wd], i) => r.transition().duration(fast ? 0 : 800).delay(fast ? 0 : i * 60).attr('x', x0).attr('width', wd)); } };
}

// ---------------------------------------------------------------- well-log tracks; depth down
// tracks: [{title, unit, curves:[{key,color,width}], domain:[a,b], log}], zones: [{top, base, color, text}]
export function logTracks(host, rows, o) {
  const W = o.W || 1100, H = o.H || 820, m = { l: 110, r: 20, t: 70, b: 20 }, gap = 18;
  const { g, w, h } = frame(host, W, H, m);
  const y = d3.scaleLinear().domain(o.depth).range([0, h]);
  rows = rows.filter(r => r.mss >= o.depth[0] && r.mss <= o.depth[1]);
  const n = o.tracks.length, tw = (w - gap * (n - 1)) / n;
  const ay = g.append('g').call(d3.axisLeft(y).ticks(8).tickFormat(d => d3.format(',')(d))); axisStyle(ay); ay.select('.domain').remove();
  label(g, -86, h / 2, o.ylabel || 'm subsea', { anchor: 'middle', rot: -90 });
  const zonesG = g.append('g');
  for (const z of o.zones || []) {
    const zz = zonesG.append('g').attr('class', 'zone').attr('opacity', 0).attr('data-zone', z.id || '');
    zz.append('rect').attr('x', 0).attr('width', w).attr('y', y(z.top)).attr('height', y(z.base) - y(z.top)).attr('fill', z.color).attr('opacity', z.opacity ?? 0.22);
    if (z.line) zz.append('line').attr('x1', -8).attr('x2', w).attr('y1', y(z.top)).attr('y2', y(z.top)).attr('stroke', z.line).attr('stroke-width', 3);
    z._g = zz;
  }
  const curves = [];
  o.tracks.forEach((t, ti) => {
    const gx = g.append('g').attr('transform', `translate(${ti * (tw + gap)},0)`);
    gx.append('rect').attr('width', tw).attr('height', h).attr('fill', 'none').attr('stroke', C.grid);
    const x = (t.log ? d3.scaleLog() : d3.scaleLinear()).domain(t.domain).range(t.reverse ? [tw, 0] : [0, tw]).clamp(true);
    (t.log ? [1, 10, 100] : x.ticks(4)).forEach(v => gx.append('line').attr('x1', x(v)).attr('x2', x(v)).attr('y1', 0).attr('y2', h).attr('stroke', C.grid).attr('stroke-opacity', 0.6));
    label(gx, tw / 2, -44, t.title, { anchor: 'middle', fill: C.ink, size: 23, weight: 600 });
    label(gx, 4, -12, String(t.domain[t.reverse ? 1 : 0]), { size: 17, mono: true }); label(gx, tw - 4, -12, String(t.domain[t.reverse ? 0 : 1]) + (t.unit ? ' ' + t.unit : ''), { anchor: 'end', size: 18, mono: true });
    for (const c of t.curves) {
      const line = d3.line().defined(r => r[c.key] != null && isFinite(r[c.key]) && (!t.log || r[c.key] > 0)).x(r => x(r[c.key])).y(r => y(r.mss));
      const p = gx.append('path').datum(rows).attr('d', line).attr('fill', 'none').attr('stroke', c.color).attr('stroke-width', c.width || 2.2);
      const L = p.node().getTotalLength(); p.attr('stroke-dasharray', `${L} ${L}`).attr('stroke-dashoffset', L); curves.push([p, L]);
    }
  });
  const zl = (o.zones || []).map(z => { const t = label(g, w + 0, (y(z.top) + y(z.base)) / 2, '', {}); return t; });
  return {
    draw(fast) { curves.forEach(([p, L]) => p.transition().duration(fast ? 0 : 2200).ease(d3.easeCubicInOut).attr('stroke-dashoffset', 0)); },
    zone(id, fast) { (o.zones || []).filter(z => z.id === id).forEach(z => z._g.transition().duration(fast ? 0 : 700).attr('opacity', 1)); },
    y, g, w, h
  };
}

// ---------------------------------------------------------------- structure map (canvas raster + contours) from a regular grid
export function structureMap(host, G, o) {
  const W = o.W || 900, H = o.H || 900;
  const wrap = document.createElement('div'); wrap.className = 'smap'; wrap.style.width = W + 'px'; wrap.style.height = H + 'px'; host.append(wrap);
  const xr = o.xr, yr = o.yr; // UTM extent to show
  const sx = d3.scaleLinear().domain(xr).range([0, W]), sy = d3.scaleLinear().domain(yr).range([H, 0]);
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H; wrap.append(cv); const cx = cv.getContext('2d');
  const img = cx.createImageData(W, H); const ramp = o.ramp;
  const zAt = (x, y) => { const fi = (x - G.x0) / G.dx, fj = (y - G.y0) / G.dy, i = Math.floor(fi), j = Math.floor(fj); if (i < 0 || j < 0 || i >= G.nx - 1 || j >= G.ny - 1) return null; const a = G.z[j][i], b = G.z[j][i + 1], c = G.z[j + 1][i], d = G.z[j + 1][i + 1]; if ([a, b, c, d].some(v => v == null)) return null; const tx = fi - i, ty = fj - j; return a * (1 - tx) * (1 - ty) + b * tx * (1 - ty) + c * (1 - tx) * ty + d * tx * ty; };
  for (let py = 0; py < H; py++) for (let px = 0; px < W; px++) {
    const z = zAt(sx.invert(px + 0.5), sy.invert(py + 0.5)), k = (py * W + px) * 4;
    if (z == null) { img.data.set([22, 30, 40, 255], k); continue; }
    const f = Math.max(0, Math.min(1, (o.zmax - z) / (o.zmax - o.zmin))); const c = d3.rgb(ramp(f));
    img.data.set([c.r, c.g, c.b, 255], k);
  }
  cx.putImageData(img, 0, 0);
  const svg = d3.select(wrap).append('svg').attr('viewBox', `0 0 ${W} ${H}`).attr('width', W).attr('height', H).style('position', 'absolute').style('left', 0).style('top', 0).style('font-family', FONT).style('overflow', 'visible');
  // contours from the grid
  const vals = []; for (let j = 0; j < G.ny; j++) for (let i = 0; i < G.nx; i++) vals.push(G.z[j][i] == null ? -9999 : -G.z[j][i]);
  const conts = d3.contours().size([G.nx, G.ny]).thresholds(d3.range(-2460, -2279, 10))(vals);
  const tr = d3.geoTransform({ point(px, py) { this.stream.point(sx(G.x0 + px * G.dx), sy(G.y0 + py * G.dy)); } });
  svg.append('g').selectAll('path').data(conts).join('path').attr('d', d3.geoPath(tr)).attr('fill', 'none').attr('stroke', d => d.value % 50 === 0 ? '#0b0f14' : 'rgba(11,15,20,0.55)').attr('stroke-width', d => d.value % 50 === 0 ? 2 : 1);
  return { svg, sx, sy, wrap };
}
