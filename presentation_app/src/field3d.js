// ---------------------------------------------------------------- 3-D field scene (three.js)
// Frame: x = east (m from E0), z = -(north from N0), y = -depth * VE (m). Depth is metres below sea level, positive down.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const E0 = 707600, N0 = 2262700;
export const STATUS_COL = {
  producing: 0x5dbb63, testing: 0xe8894f, workover: 0xe8894f, drilling: 0xffffff, shut_in: 0xe0b341,
  injector: 0x4a90d9, plugged: 0x6b7682, dry_abandoned: 0x6b7682, planned: 0xe8894f, restorable: 0x9fd86b, none: 0x6b7682
};
export const STATUS_LABEL = {
  producing: 'producing', testing: 'testing', workover: 'workover', drilling: 'drilling', shut_in: 'shut in',
  injector: 'water injector', plugged: 'plugged', dry_abandoned: 'dry, plugged', planned: 'planned', restorable: 'shut in, restorable'
};

// blue (deep) -> red (high) ramp, perceptually smooth (turbo-like, trimmed at both ends)
const RAMP = ['#30123b', '#4145ab', '#4675ed', '#39a2fc', '#1bcfd4', '#24eca6', '#61fc6c', '#a4fc3b', '#d1e834', '#f3c63a', '#fe9b2d', '#f36315', '#d93806', '#b11901', '#7a0403'];
export function rampColor(f) {
  f = Math.min(1, Math.max(0, f)); const n = RAMP.length - 1, i = Math.min(n - 1, Math.floor(f * n)), t = f * n - i;
  const a = new THREE.Color(RAMP[i]), b = new THREE.Color(RAMP[i + 1]); return a.lerp(b, t);
}
export const RAMP_CSS = RAMP;

function seismicLUT(kind) {
  const lut = new Uint8Array(256 * 4);
  for (let v = 0; v < 256; v++) {
    const s = (v - 127.5) / 127.5; let r, g, b;
    if (kind === 'grey') { const q = Math.round(128 + 127 * Math.tanh(1.6 * s)); r = g = b = q; }
    else { // red / white / blue: positive red, negative blue
      const a = Math.min(1, Math.abs(s) * 1.6);
      if (s >= 0) { r = 255 - 40 * a; g = 255 - 225 * a; b = 255 - 230 * a; } else { r = 255 - 235 * a; g = 255 - 175 * a; b = 255 - 60 * a; }
    }
    lut.set([r, g, b, 255], v * 4);
  }
  return lut;
}

async function loadAtlas(url, info) {
  const img = new Image(); img.src = url; await img.decode();
  const cv = document.createElement('canvas'); cv.width = img.width; cv.height = img.height;
  const cx = cv.getContext('2d', { willReadFrequently: true }); cx.drawImage(img, 0, 0);
  const px = cx.getImageData(0, 0, img.width, img.height).data;
  const { ni, nj, nk } = info, cols = info.atlas.cols, W = img.width, vol = new Uint8Array(ni * nj * nk);
  for (let k = 0; k < nk; k++) {
    const r = Math.floor(k / cols), c = k % cols;
    for (let i = 0; i < ni; i++) {
      const row = (r * ni + i) * W + c * nj, o = (k * ni + i) * nj;
      for (let j = 0; j < nj; j++) vol[o + j] = px[(row + j) * 4];
    }
  }
  return vol;
}

export class Field3D {
  constructor(meta, base) {
    this.meta = meta; this.base = base; this.ve = 2.5; this.vols = {}; this.lut = seismicLUT('rwb');
    this.year = 2026.8; this.wellState = {}; this.labelsOn = true; this.highlight = null;
    const r = this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: false });
    r.setPixelRatio(Math.min(2, window.devicePixelRatio || 1)); r.setClearColor(0x0d131a, 1);
    this.dom = r.domElement; this.dom.className = 'gl';
    this.scene = new THREE.Scene(); this.scene.fog = new THREE.Fog(0x0d131a, 9000, 26000);
    this.camera = new THREE.PerspectiveCamera(38, 16 / 9, 10, 60000);
    this.controls = new OrbitControls(this.camera, this.dom); this.controls.enableDamping = true; this.controls.dampingFactor = 0.08;
    this.controls.maxPolarAngle = Math.PI * 0.62;
    this.scene.add(new THREE.HemisphereLight(0xdfe8f2, 0x1a2230, 1.1));
    const d = new THREE.DirectionalLight(0xffffff, 1.4); d.position.set(3000, 6000, 2500); this.scene.add(d);
    this.root = new THREE.Group(); this.scene.add(this.root);
    this.labels = document.createElement('div'); this.labels.className = 'gl-labels';
    this._build(); this.setVE(this.ve); this.view('overview', 0);
    this._tick = this._tick.bind(this); this._running = false; this.tweens = [];
  }
  P(x, y, z) { return new THREE.Vector3(x - E0, -z * this.ve, -(y - N0)); }       // UTM x, y, depth mSS
  mount(container) {
    this.container = container; container.appendChild(this.dom); container.appendChild(this.labels);
    this.resize(); if (!this._running) { this._running = true; requestAnimationFrame(this._tick); }
  }
  resize() {
    if (!this.container) return; const w = this.container.clientWidth, h = this.container.clientHeight; if (!w || !h) return;
    this.renderer.setSize(w, h, false); this.dom.style.width = w + 'px'; this.dom.style.height = h + 'px';
    this.camera.aspect = w / h; this._applyShift(w, h);
  }
  setShift(fx = 0, fy = 0) { this.shift = [fx, fy]; if (this.container) this._applyShift(this.container.clientWidth, this.container.clientHeight); }
  _applyShift(w, h) { const [fx, fy] = this.shift || [0, 0]; if (fx || fy) this.camera.setViewOffset(w, h, -fx * w, fy * h, w, h); else this.camera.clearViewOffset(); this.camera.updateProjectionMatrix(); }
  _tick(t) {
    requestAnimationFrame(this._tick);
    if (this.paused || !this.container || !this.container.isConnected || this.container.offsetParent === null) return;
    const now = performance.now();
    this.tweens = this.tweens.filter(tw => { const f = Math.min(1, (now - tw.t0) / tw.dur); tw.fn(f < 0.5 ? 4 * f * f * f : 1 - Math.pow(-2 * f + 2, 3) / 2); return f < 1; });
    this.controls.update();
    const pulse = 0.5 + 0.5 * Math.sin(now / 380);
    for (const w of Object.values(this.wellObj)) if (w.ring.visible) { const s = w.ringBase * (1 + 0.18 * pulse); w.ring.scale.set(s, s, s); w.ring.material.opacity = 0.35 + 0.35 * (1 - pulse); }
    this.renderer.render(this.scene, this.camera); this._labels();
  }
  // ---------------------------------------------------------------- build
  _build() {
    const m = this.meta;
    // ground plane and grid
    const g = new THREE.GridHelper(9000, 18, 0x33414f, 0x222c37); g.position.set(0, 0, 0); this.ground = g; this.root.add(g);
    // El Abra top, Jan 2019 depth grid
    const G = m.grid2019; this.zmin = 2280; this.zmax = 2420;
    const geo = new THREE.BufferGeometry(), pos = [], col = [], idx = [], id = (a, b) => a * G.nx + b;
    for (let j = 0; j < G.ny; j++) for (let i = 0; i < G.nx; i++) {
      const z = Math.min(G.z[j][i] ?? 2900, 2445); const p = this.P(G.x0 + i * G.dx, G.y0 + j * G.dy, z); pos.push(p.x, p.y, p.z);
      const c = rampColor((this.zmax - z) / (this.zmax - this.zmin)); col.push(c.r, c.g, c.b);
    }
    for (let j = 0; j < G.ny - 1; j++) for (let i = 0; i < G.nx - 1; i++) {
      const cz = [G.z[j][i], G.z[j][i + 1], G.z[j + 1][i], G.z[j + 1][i + 1]];
      if (cz.some(v => v == null) || Math.min(...cz) > 2440) continue;
      idx.push(id(j, i), id(j + 1, i), id(j, i + 1), id(j, i + 1), id(j + 1, i), id(j + 1, i + 1));
    }
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); geo.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
    geo.setIndex(idx); geo.computeVertexNormals(); this.surfGeo = geo; this.surfZ = G;
    this.surface = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75, metalness: 0.0, side: THREE.DoubleSide, transparent: true, opacity: 0.95 }));
    this.root.add(this.surface);
    // contour lines every 10 m on the surface
    this.contours = this._contours(G, 10); this.root.add(this.contours);
    // oil-water reference plane (lowest known oil -2,374 mSS) as a translucent sheet
    const owc = new THREE.Mesh(new THREE.PlaneGeometry(4300, 4300), new THREE.MeshBasicMaterial({ color: 0x3b7fd0, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false }));
    owc.rotation.x = -Math.PI / 2; this.owc = owc; this.root.add(owc);
    // wells
    this.wellObj = {};
    for (const w of m.wells) this.wellObj[w.well] = this._well(w);
    // seismic slice planes (created lazily per volume)
    this.slices = new THREE.Group(); this.root.add(this.slices); this.sliceState = null;
  }
  _contours(G, step) {
    const pts = [], dep = [];
    const lv0 = Math.ceil(this.zmin / step) * step;
    for (let lv = lv0; lv <= 2440; lv += step) {
      for (let j = 0; j < G.ny - 1; j++) for (let i = 0; i < G.nx - 1; i++) {
        const c = [G.z[j][i], G.z[j][i + 1], G.z[j + 1][i + 1], G.z[j + 1][i]]; if (c.some(v => v == null)) continue;
        const xy = [[i, j], [i + 1, j], [i + 1, j + 1], [i, j + 1]], cross = [];
        for (let e = 0; e < 4; e++) { const a = c[e], b = c[(e + 1) % 4]; if ((a - lv) * (b - lv) < 0) { const t = (lv - a) / (b - a); const p = xy[e], q = xy[(e + 1) % 4]; cross.push([p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t]); } }
        if (cross.length >= 2) for (let k = 0; k + 1 < cross.length; k += 2) for (const [a, b] of [cross[k], cross[k + 1]]) { const P = this.P(G.x0 + a * G.dx, G.y0 + b * G.dy, lv); pts.push(P.x, P.y + 2, P.z); dep.push(lv); }
      }
    }
    const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3)); this.contDepth = dep;
    return new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: 0x0b0f14, transparent: true, opacity: 0.45 }));
  }
  _well(w) {
    const grp = new THREE.Group(); grp.userData = w; this.root.add(grp);
    const o = { w, grp, status: 'none' };
    o.make = () => {
      grp.clear();
      const pts = w.path.map(p => this.P(p[0], p[1], p[2]));
      const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal');
      const mat = new THREE.MeshStandardMaterial({ color: STATUS_COL.none, roughness: 0.5, emissive: 0x000000 });
      o.mat = mat; o.curve = curve;
      o.tube = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(24, pts.length * 4), 9, 8, false), mat); grp.add(o.tube);
      if (w.planned) { mat.transparent = true; mat.opacity = 0.75; }
      // perforations
      o.perfs = [];
      for (const pf of w.perfs || []) {
        const seg = this._pathBetween(w, pf.top, pf.base); if (seg.length < 2) continue;
        const c = new THREE.CatmullRomCurve3(seg.map(p => this.P(p[0], p[1], p[2])));
        const active = /ACTIVE/i.test(pf.status) && !/INACT/i.test(pf.status);
        const pm = new THREE.Mesh(new THREE.TubeGeometry(c, 8, 20, 10, false), new THREE.MeshStandardMaterial({ color: active ? 0xff7a2f : 0xa0a7ad, emissive: active ? 0x5a2000 : 0x000000 }));
        pm.userData = pf; grp.add(pm); o.perfs.push(pm);
      }
      // wellhead marker and pulse ring at the reservoir
      const top = pts[0]; o.head = new THREE.Mesh(new THREE.CylinderGeometry(26, 26, 10, 18), new THREE.MeshStandardMaterial({ color: 0xdfe6ee })); o.head.position.copy(top); grp.add(o.head);
      const res = this._resPoint(w); o.resP = res;
      o.ring = new THREE.Mesh(new THREE.RingGeometry(40, 58, 40), new THREE.MeshBasicMaterial({ color: 0x5dbb63, transparent: true, opacity: 0.6, side: THREE.DoubleSide, depthWrite: false }));
      o.ring.rotation.x = -Math.PI / 2; o.ring.position.copy(res); o.ring.visible = false; o.ringBase = 1; grp.add(o.ring);
      // cumulative-oil column above the wellhead (height grows with cumulative)
      o.colMat = new THREE.MeshStandardMaterial({ color: 0x5dbb63, transparent: true, opacity: 0.85, emissive: 0x0b2a0e });
      o.col = new THREE.Mesh(new THREE.CylinderGeometry(34, 34, 1, 20), o.colMat); o.col.position.set(res.x + 70, res.y + 20, res.z); o.col.visible = false; grp.add(o.col);
      o.waterCol = new THREE.Mesh(new THREE.CylinderGeometry(22, 22, 1, 20), new THREE.MeshStandardMaterial({ color: 0x4a90d9, transparent: true, opacity: 0.55 }));
      o.waterCol.visible = false; grp.add(o.waterCol);
      // X marker for dry/plugged
      const xm = new THREE.Group(); const bar = new THREE.BoxGeometry(110, 10, 10), xmat = new THREE.MeshBasicMaterial({ color: 0x8b95a1 });
      const b1 = new THREE.Mesh(bar, xmat), b2 = new THREE.Mesh(bar, xmat); b1.rotation.y = Math.PI / 4; b2.rotation.y = -Math.PI / 4; xm.add(b1, b2);
      xm.position.set(top.x, 6, top.z); xm.visible = false; o.xmark = xm; grp.add(xm);
      // label anchor
      o.labelEl = o.labelEl || Object.assign(document.createElement('span'), { className: 'wl' });
      if (!o.labelEl.isConnected) this.labels.appendChild(o.labelEl);
      o.labelEl.textContent = w.well;
      this._applyState(o, this.wellState[w.well] || {});
    };
    o.make(); return o;
  }
  _pathBetween(w, ztop, zbase) {   // points of the path between two subsea depths
    const p = w.path, out = [];
    const at = z => { for (let i = 0; i + 1 < p.length; i++) { const a = p[i], b = p[i + 1]; if ((a[2] - z) * (b[2] - z) <= 0 && a[2] !== b[2]) { const t = (z - a[2]) / (b[2] - a[2]); return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, z]; } } return null; };
    if (w.well === 'TEC-11') { // lateral: perforations given in mSS are ambiguous along a near-horizontal hole; place by MD if present
      if (w.md && w.perfMD) return [];
    }
    const a = at(ztop), b = at(zbase); if (!a || !b) return [];
    out.push(a); for (const q of p) if (q[2] > ztop && q[2] < zbase) out.push(q); out.push(b); return out;
  }
  _resPoint(w) {
    const z = w.top_mss || 2300; const p = w.path; let best = p[p.length - 1];
    for (let i = 0; i + 1 < p.length; i++) { const a = p[i], b = p[i + 1]; if ((a[2] - z) * (b[2] - z) <= 0 && a[2] !== b[2]) { const t = (z - a[2]) / (b[2] - a[2]); best = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, z]; break; } }
    return this.P(best[0], best[1], best[2]);
  }
  setVE(ve) {
    this.ve = ve;
    // surface
    const G = this.surfZ, pos = this.surfGeo.attributes.position; let n = 0;
    for (let j = 0; j < G.ny; j++) for (let i = 0; i < G.nx; i++) { const z = Math.min(G.z[j][i] ?? 2900, 2445); pos.setY(n++, -z * ve); }
    pos.needsUpdate = true; this.surfGeo.computeVertexNormals();
    const cp = this.contours.geometry.attributes.position;
    for (let i = 0; i < cp.count; i++) cp.setY(i, -this.contDepth[i] * ve + 3); cp.needsUpdate = true;
    this.owc.position.y = -2374.2 * ve;
    for (const o of Object.values(this.wellObj)) o.make();
    if (this.sliceState) this.setSlices(this.sliceState);
  }
  // ---------------------------------------------------------------- well state for a given time
  setWellStates(states) { // {well: {status, oil_bpd, cum_oil, cum_water, visible}}
    this.wellState = states;
    for (const [k, o] of Object.entries(this.wellObj)) this._applyState(o, states[k] || { visible: false });
  }
  _applyState(o, s) {
    const vis = s.visible !== false && s.status !== undefined;
    o.grp.visible = vis; if (o.labelEl) o.labelEl.style.display = vis && this.labelsOn ? '' : 'none';
    if (!vis) return;
    const st = s.status || 'none'; o.status = st;
    o.mat.color.setHex(STATUS_COL[st] ?? STATUS_COL.none);
    o.mat.emissive.setHex(this.highlight === o.w.well ? 0x553311 : (st === 'producing' ? 0x0d2a10 : 0x000000));
    const q = s.oil_bpd || 0; o.ring.visible = st === 'producing' && q > 0.5;
    o.ringBase = 0.6 + Math.sqrt(q) / 6; o.ring.material.color.setHex(st === 'injector' ? 0x4a90d9 : 0x5dbb63);
    if (st === 'injector') { o.ring.visible = true; o.ringBase = 1.2; }
    const cum = s.cum_oil || 0, h = cum / 1000 * 0.6;     // 0.6 scene units of column per 1,000 bbl, standing on the reef top (display scale)
    const R = o.resP; o.col.visible = h > 1; o.col.scale.y = Math.max(1, h); o.col.position.set(R.x + 70, R.y + 30 + h / 2, R.z);
    const hw = (s.cum_water || 0) / 1000 * 0.6; o.waterCol.visible = hw > 1;
    o.waterCol.scale.y = Math.max(1, hw); o.waterCol.position.set(R.x + 130, R.y + 30 + hw / 2, R.z);
    o.xmark.visible = st === 'plugged' || st === 'dry_abandoned';
    o.labelEl.dataset.status = st; o.labelEl.innerHTML = `<b>${o.w.well}</b>${s.caption ? `<i>${s.caption}</i>` : ''}`;
  }
  setHighlight(well) { this.highlight = well; this.setWellStates(this.wellState); for (const [k, o] of Object.entries(this.wellObj)) o.labelEl.classList.toggle('hl', k === well); }
  _labels() {
    if (!this.container) return; const w = this.container.clientWidth, h = this.container.clientHeight, placed = [];
    const items = [];
    for (const o of Object.values(this.wellObj)) {
      if (!o.grp.visible || !this.labelsOn) { o.labelEl.style.display = 'none'; continue; }
      const p = o.resP.clone(); p.y += (o.col.visible ? o.col.scale.y + 90 : 160);
      const v = p.project(this.camera); if (v.z > 1) { o.labelEl.style.display = 'none'; continue; }
      o.labelEl.style.display = ''; items.push({ o, x: (v.x * 0.5 + 0.5) * w, y: (-v.y * 0.5 + 0.5) * h, lw: o.labelEl.offsetWidth || 90, lh: o.labelEl.offsetHeight || 30 });
    }
    items.sort((a, b) => (b.o.w.well === this.highlight) - (a.o.w.well === this.highlight) || a.y - b.y);
    for (const it of items) {      // greedy: move a label up until it clears the ones already placed
      let y = it.y;
      for (let pass = 0; pass < 8; pass++) {
        const hit = placed.find(q => Math.abs(q.x - it.x) < (q.lw + it.lw) / 2 + 4 && y > q.y - it.lh - 2 && y - it.lh < q.y + 2);
        if (!hit) break; y = hit.y - hit.lh - 4;
      }
      placed.push({ x: it.x, y, lw: it.lw, lh: it.lh });
      it.o.labelEl.style.transform = `translate(${it.x}px, ${y}px) translate(-50%, -100%)`;
    }
  }
  // ---------------------------------------------------------------- camera
  views() {
    const c = this.P(707650, 2262620, 2300);
    return {
      overview: { target: c, dist: 6200, az: -0.62, el: 0.52 },
      crest: { target: this.P(707680, 2262500, 2300), dist: 2600, az: -0.3, el: 0.42 },
      surface: { target: this.P(707650, 2262620, 2280), dist: 4300, az: -0.75, el: 0.38 },
      section: { target: this.P(707680, 2262560, 2310), dist: 2300, az: 0.08, el: 0.12 },
      top: { target: c, dist: 6500, az: 0.0001, el: 1.45 },
    };
  }
  view(name, dur = 1800) { const v = this.views()[name]; if (v) this.flyTo(v.target, v.dist, v.az, v.el, dur); }
  focusWell(name, dur = 2200, opts = {}) {
    const o = this.wellObj[name]; if (!o) return;
    const t = o.resP.clone(); t.y += (opts.lift ?? 300);
    this.flyTo(t, opts.dist ?? 1900, opts.az ?? -0.5, opts.el ?? 0.33, dur);
  }
  flyTo(target, dist, az, el, dur = 1800) {
    const cam = this.camera, ctl = this.controls;
    const endPos = new THREE.Vector3(target.x + dist * Math.cos(el) * Math.sin(az), target.y + dist * Math.sin(el), target.z + dist * Math.cos(el) * Math.cos(az));
    if (!dur) { cam.position.copy(endPos); ctl.target.copy(target); ctl.update(); return; }
    const p0 = cam.position.clone(), t0 = ctl.target.clone();
    this.tweens = this.tweens.filter(t => !t.cam);
    this.tweens.push({ cam: true, t0: performance.now(), dur, fn: f => { cam.position.lerpVectors(p0, endPos, f); ctl.target.lerpVectors(t0, target, f); } });
  }
  orbit(on, speed = 0.25) { this.controls.autoRotate = on; this.controls.autoRotateSpeed = speed; }
  // ---------------------------------------------------------------- seismic
  async loadVolume(key) {
    if (this.vols[key]) return this.vols[key];
    const info = this.meta[key]; const vol = await loadAtlas(this.base + info.atlas.file, info);
    return (this.vols[key] = { info, vol });
  }
  async setSlices(s) { // {vol:'pstm'|'psdm', il, xl, k (indices or null), cmap}
    this.sliceState = s; this.slices.clear(); if (!s || !s.vol) return;
    const V = await this.loadVolume(s.vol); if (this.sliceState !== s) return;
    if (s.cmap) this.lut = seismicLUT(s.cmap);
    const { info, vol } = V, { ni, nj, nk } = info;
    const zOf = k => info.axis === 'time_ms' ? (info.k0 + k * info.dk) / 2000 * info.v_field_mps : info.k0 + k * info.dk;
    const xyOf = (i, j) => [info.origin[0] + i * info.di[0] + j * info.dj[0], info.origin[1] + i * info.di[1] + j * info.dj[1]];
    const mk = (W, H, get, corners) => {
      const data = new Uint8Array(W * H * 4);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const v = get(x, y); data.set(this.lut.subarray(v * 4, v * 4 + 4), (y * W + x) * 4); }
      const tex = new THREE.DataTexture(data, W, H, THREE.RGBAFormat); tex.needsUpdate = true; tex.colorSpace = THREE.SRGBColorSpace;
      tex.magFilter = THREE.LinearFilter; tex.minFilter = THREE.LinearFilter;
      const g = new THREE.BufferGeometry(); const [a, b, c, d] = corners;
      g.setAttribute('position', new THREE.Float32BufferAttribute([...a, ...b, ...c, ...d], 3));
      g.setAttribute('uv', new THREE.Float32BufferAttribute([0, 0, 1, 0, 1, 1, 0, 1], 2)); g.setIndex([0, 1, 2, 0, 2, 3]);
      const mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: tex, side: THREE.DoubleSide, transparent: true, opacity: s.opacity ?? 1 }));
      this.slices.add(mesh);
    };
    const V3 = (i, j, k) => { const [x, y] = xyOf(i, j); const p = this.P(x, y, zOf(k)); return [p.x, p.y, p.z]; };
    const at = (i, j, k) => vol[(k * ni + i) * nj + j];
    if (s.il != null) { const i = Math.round(s.il); mk(nj, nk, (x, y) => at(i, x, y), [V3(i, 0, 0), V3(i, nj - 1, 0), V3(i, nj - 1, nk - 1), V3(i, 0, nk - 1)]); }
    if (s.xl != null) { const j = Math.round(s.xl); mk(ni, nk, (x, y) => at(x, j, y), [V3(0, j, 0), V3(ni - 1, j, 0), V3(ni - 1, j, nk - 1), V3(0, j, nk - 1)]); }
    if (s.k != null) { const k = Math.round(s.k); mk(nj, ni, (x, y) => at(y, x, k), [V3(0, 0, k), V3(0, nj - 1, k), V3(ni - 1, nj - 1, k), V3(ni - 1, 0, k)]); }
  }
  wellIJ(key, well) { // grid index of a well's reservoir point in a volume
    const info = this.meta[key], o = this.wellObj[well]; const w = o.w, p = w.path[w.path.length - 1];
    const [ox, oy] = info.origin, [a, b] = info.di, [c, d] = info.dj, dx = p[0] - ox, dy = p[1] - oy, det = a * d - b * c;
    return [(dx * d - dy * c) / det, (a * dy - b * dx) / det];
  }
  showSurface(on, opacity = 0.95) { this.surface.visible = on; this.contours.visible = on; this.surface.material.opacity = opacity; }
}
