import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EXRLoader } from 'three/addons/loaders/EXRLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { GTAOPass } from 'three/addons/postprocessing/GTAOPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { SSSPass } from './sss';
import { loadManifest, loadSystem, type LoadedSystem, type OrganMesh } from './loader';
import { allTissueMaterials, setClipPlane, sssUniforms } from './materials';
import type { Manifest } from './types';

const ASSETS = './assets/';
const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

// ---------------------------------------------------------------- renderer
const canvas = $<HTMLCanvasElement>('view');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.NoToneMapping;          // OutputPass applies ACES at the end of the chain
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0e1013);
const camera = new THREE.PerspectiveCamera(32, 1, 0.02, 20);
camera.position.set(0.0, 1.05, 2.6);
const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 0.95, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 0.08;
controls.maxDistance = 6;

// image-based lighting plus one key light for shadows
const pmrem = new THREE.PMREMGenerator(renderer);
pmrem.compileEquirectangularShader();
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;   // until the HDRI arrives
scene.environmentIntensity = 0.55;
const key = new THREE.DirectionalLight(0xfff2e6, 1.5);
key.position.set(1.6, 2.8, 2.2);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
key.shadow.bias = -0.00015;
key.shadow.normalBias = 0.004;
key.shadow.radius = 4;
const cam = key.shadow.camera as THREE.OrthographicCamera;
cam.left = -1.2; cam.right = 1.2; cam.top = 1.4; cam.bottom = -1.4; cam.near = 0.5; cam.far = 8;
scene.add(key, key.target);
key.target.position.set(0, 0.9, 0);
const rim = new THREE.DirectionalLight(0xbcd4ff, 0.35);
rim.position.set(-2.2, 1.8, -2.0);
scene.add(rim);

// HDRIs: CC0 Poly Haven sets repackaged by @pmndrs/assets (see LICENSES.md)
const HDRIS: Record<string, () => Promise<{ default: string }>> = {
  studio: () => import('@pmndrs/assets/hdri/studio.exr'),
  lab: () => import('@pmndrs/assets/hdri/lab.exr'),
  warehouse: () => import('@pmndrs/assets/hdri/warehouse.exr'),
  hall: () => import('@pmndrs/assets/hdri/hall.exr'),
  sky: () => import('@pmndrs/assets/hdri/sky.exr'),
};
async function useHdri(name: string) {
  const mod = await HDRIS[name]();
  const tex = await new EXRLoader().loadAsync(mod.default);
  tex.mapping = THREE.EquirectangularReflectionMapping;
  const env = pmrem.fromEquirectangular(tex).texture;
  scene.environment = env;
  tex.dispose();
}
const hdriSel = $<HTMLSelectElement>('hdri');
for (const k of Object.keys(HDRIS)) hdriSel.add(new Option(k, k));
hdriSel.value = 'studio';
hdriSel.onchange = () => useHdri(hdriSel.value).catch(console.error);
useHdri('studio').catch(console.error);

// ---------------------------------------------------------------- post chain
const size = new THREE.Vector2();
renderer.getSize(size);
const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(size.x, size.y, { type: THREE.HalfFloatType }));
const sssPass = new SSSPass(scene, camera, size.x, size.y);
const gtao = new GTAOPass(scene, camera, size.x, size.y);
gtao.output = GTAOPass.OUTPUT.Default;
gtao.updateGtaoMaterial({ radius: 0.05, distanceExponent: 1, thickness: 0.6, scale: 1.2, samples: 12, distanceFallOff: 1 });
gtao.blendIntensity = 0.85;
const outline = new OutlinePass(size, scene, camera);
outline.edgeStrength = 4; outline.edgeGlow = 0.25; outline.edgeThickness = 1.5; outline.pulsePeriod = 0;
outline.visibleEdgeColor.set(0x7fc4ff); outline.hiddenEdgeColor.set(0x1e4a6f);
const bloom = new UnrealBloomPass(size, 0.12, 0.45, 1.25);   // only true highlights bloom: threshold above white
const output = new OutputPass();
renderer.toneMapping = THREE.ACESFilmicToneMapping;   // OutputPass reads the renderer's tone mapping
renderer.toneMappingExposure = 0.72;
const smaa = new SMAAPass();
composer.addPass(sssPass);
composer.addPass(gtao);
composer.addPass(outline);
composer.addPass(bloom);
composer.addPass(output);
composer.addPass(smaa);

function resize() {
  const w = canvas.clientWidth || innerWidth, h = canvas.clientHeight || innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  composer.setSize(w, h);
  sssPass.setSize(w * renderer.getPixelRatio(), h * renderer.getPixelRatio());
}
addEventListener('resize', resize);
resize();

// ---------------------------------------------------------------- state
let manifest: Manifest;
const systems = new Map<string, LoadedSystem>();
const sysOpacity = new Map<string, number>();
const sysVisible = new Map<string, boolean>();
let peel = 0;
let showAttachments = false;   // muscle origin/insertion footprints (Z-Anatomy .ol/.or/.el/.er) are hidden until asked for
let selected: OrganMesh | null = null;
const status = $('status');

function applyVisibility() {
  const order = manifest.peel_order;
  for (const [name, sys] of systems) {
    const i = order.indexOf(name);
    const peelFade = i < 0 ? 1 : THREE.MathUtils.clamp(1 - (peel * order.length - i), 0, 1);
    const op = (sysOpacity.get(name) ?? 1) * peelFade;
    const vis = (sysVisible.get(name) ?? true) && op > 0.002;
    sys.group.visible = vis;
    for (const m of sys.meshes) {
      m.visible = vis && !m.userData.hidden && (showAttachments || (m.userData.organ.role ?? 'organ') === 'organ');
      const mat = m.material;
      mat.transparent = op < 0.999;
      mat.opacity = op;
      mat.depthWrite = op > 0.5;
    }
  }
}

// ---------------------------------------------------------------- UI: systems
function systemRow(name: string) {
  const sys = manifest.systems[name];
  const row = document.createElement('div');
  row.className = 'sys loading';
  row.dataset.name = name;
  row.innerHTML = `<input type="checkbox" checked title="visible" /><div class="name">${name}<small>${sys.meshes} parts · ${(sys.tris / 1000).toFixed(0)}k tris</small></div><input type="range" min="0" max="1" step="0.01" value="1" title="opacity" /><button class="solo" title="show only this system">solo</button>`;
  const [chk, rng] = [...row.querySelectorAll('input')] as HTMLInputElement[];
  chk.onchange = () => { sysVisible.set(name, chk.checked); ensureLoaded(name); applyVisibility(); };
  rng.oninput = () => { sysOpacity.set(name, +rng.value); ensureLoaded(name); applyVisibility(); };
  (row.querySelector('.solo') as HTMLButtonElement).onclick = () => {
    for (const r of document.querySelectorAll<HTMLDivElement>('.sys')) {
      const on = r.dataset.name === name;
      (r.querySelector('input[type=checkbox]') as HTMLInputElement).checked = on;
      sysVisible.set(r.dataset.name!, on);
    }
    ensureLoaded(name); applyVisibility();
  };
  return row;
}

const loading = new Map<string, Promise<void>>();
function ensureLoaded(name: string) {
  if (systems.has(name) || loading.has(name)) return loading.get(name) ?? Promise.resolve();
  const row = document.querySelector<HTMLDivElement>(`.sys[data-name="${name}"]`);
  const p = loadSystem(ASSETS, manifest, name, (f) => { status.textContent = `loading ${name} ${(f * 100).toFixed(0)}%`; })
    .then((sys) => {
      systems.set(name, sys);
      scene.add(sys.group);
      row?.classList.remove('loading');
      applyVisibility();
      status.textContent = `${[...systems.values()].reduce((a, s) => a + s.tris, 0).toLocaleString()} triangles in ${systems.size} systems`;
    })
    .catch((e) => { console.error(e); status.textContent = `failed to load ${name}: ${e.message ?? e}`; row?.classList.add('failed'); })
    .finally(() => loading.delete(name));
  loading.set(name, p);
  return p;
}

// ---------------------------------------------------------------- UI: peel, section, look
const peelInput = $<HTMLInputElement>('peel');
peelInput.oninput = () => { peel = +peelInput.value; $('peel-label').textContent = peel > 0 ? `${(peel * 100).toFixed(0)}%` : ''; applyVisibility(); };
const clipAxis = $<HTMLSelectElement>('clip-axis');
const clipPos = $<HTMLInputElement>('clip-pos');
let clipFlip = 1;
$('clip-flip').onclick = () => { clipFlip *= -1; updateClip(); };
function updateClip() {
  const n = { sagittal: new THREE.Vector3(1, 0, 0), coronal: new THREE.Vector3(0, 0, 1), transverse: new THREE.Vector3(0, 1, 0) }[clipAxis.value];
  if (!n) { setClipPlane(null); return; }
  const box = sceneBounds();
  const c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
  const half = Math.max(s.x, s.y, s.z) * 0.5;
  const d = c.dot(n) + (+clipPos.value) * half;
  const nn = n.clone().multiplyScalar(clipFlip);
  setClipPlane(nn, nn.dot(n) > 0 ? d : -d);
}
clipAxis.onchange = updateClip;
clipPos.oninput = updateClip;
$<HTMLInputElement>('opt-sss').onchange = (e) => { const on = (e.target as HTMLInputElement).checked; sssPass.enabledSSS = on; sssUniforms.uSSS.value = on ? 1 : 0; };
$<HTMLInputElement>('opt-ao').onchange = (e) => { gtao.enabled = (e.target as HTMLInputElement).checked; };
$<HTMLInputElement>('opt-bloom').onchange = (e) => { bloom.enabled = (e.target as HTMLInputElement).checked; };
$<HTMLInputElement>('opt-attach').onchange = (e) => { showAttachments = (e.target as HTMLInputElement).checked; applyVisibility(); };

function sceneBounds() {
  const box = new THREE.Box3();
  for (const sys of systems.values()) if (sys.group.visible) box.expandByObject(sys.group);
  if (box.isEmpty()) box.set(new THREE.Vector3(-0.5, 0, -0.5), new THREE.Vector3(0.5, 1.8, 0.5));
  return box;
}

// ---------------------------------------------------------------- selection
const raycaster = new THREE.Raycaster();
(raycaster as any).firstHitOnly = true;
const pointer = new THREE.Vector2();
let downAt = 0, downPos = [0, 0];
canvas.addEventListener('pointerdown', (e) => { downAt = performance.now(); downPos = [e.clientX, e.clientY]; });
canvas.addEventListener('pointerup', (e) => {
  if (performance.now() - downAt > 350 || Math.hypot(e.clientX - downPos[0], e.clientY - downPos[1]) > 6) return;
  pointer.set((e.clientX / canvas.clientWidth) * 2 - 1, -(e.clientY / canvas.clientHeight) * 2 + 1);
  raycaster.setFromCamera(pointer, camera);
  const meshes: OrganMesh[] = [];
  for (const s of systems.values()) if (s.group.visible) for (const m of s.meshes) if (m.visible) meshes.push(m);
  const hits = raycaster.intersectObjects(meshes, false);
  const hit = hits[0]?.object as OrganMesh | undefined;
  if (hit && e.shiftKey) { hit.userData.hidden = true; hit.visible = false; if (selected === hit) select(null); return; }
  select(hit ?? null, hits[0]?.point);
});
addEventListener('keydown', (e) => { if (e.key === 'Escape') select(null); if (e.key === 'u') { for (const s of systems.values()) for (const m of s.meshes) m.userData.hidden = false; applyVisibility(); } });

const callout = $('callout');
let calloutAnchor: THREE.Vector3 | null = null;
function select(m: OrganMesh | null, point?: THREE.Vector3) {
  selected = m;
  outline.selectedObjects = m ? [m] : [];
  const sel = $('selection');
  if (!m) { sel.innerHTML = '<p class="muted">Click an organ to identify it. Shift-click hides it, U unhides all.</p>'; callout.hidden = true; calloutAnchor = null; return; }
  const o = m.userData.organ;
  const side = o.side === 'l' ? 'left' : o.side === 'r' ? 'right' : '';
  sel.innerHTML = `<h2>${o.name}${side ? ` <small class="muted">(${side})</small>` : ''}</h2>
    <div class="meta">${o.system} · ${o.tissue}${o.role !== 'organ' ? ` · muscle ${o.role}` : ''}${o.optional ? ' · variant structure' : ''} · ${o.tris.toLocaleString()} tris</div>
    <div class="path">${[...o.parents].reverse().join(' › ')}</div>
    ${o.description ? `<div class="desc">${o.description}</div>` : ''}`;
  $('callout-name').textContent = o.name + (side ? ` (${side})` : '');
  $('callout-meta').textContent = `${o.system} · ${o.tissue}`;
  calloutAnchor = point ? point.clone() : new THREE.Box3().setFromObject(m).getCenter(new THREE.Vector3());
  callout.hidden = false;
}
function updateCallout() {
  if (!calloutAnchor || callout.hidden) return;
  const p = calloutAnchor.clone().project(camera);
  const x = (p.x + 1) / 2 * canvas.clientWidth, y = (1 - p.y) / 2 * canvas.clientHeight;
  callout.style.left = `${x}px`; callout.style.top = `${y}px`;
  callout.style.opacity = p.z < 1 ? '1' : '0';
}

// ---------------------------------------------------------------- boot
async function boot() {
  manifest = await loadManifest(ASSETS);
  const names = Object.keys(manifest.systems).sort((a, b) => manifest.systems[a].order - manifest.systems[b].order);
  const list = $('systems');
  for (const n of names) list.appendChild(systemRow(n));
  $('about').innerHTML = `Models: ${manifest.attribution.map((a) => a.replace(/ - /g, ' · ')).join('<br>')}<br>Derived assets ${manifest.license}. Code MIT.`;
  // skeleton first, the others on demand or when the peel/visibility asks for them
  const first = names.includes('skeletal') ? 'skeletal' : names[0];
  for (const n of names) if (n !== first) sysVisible.set(n, false);
  for (const r of document.querySelectorAll<HTMLDivElement>('.sys')) (r.querySelector('input[type=checkbox]') as HTMLInputElement).checked = r.dataset.name === first;
  await ensureLoaded(first);
  frameAll();
  // prefetch the rest in anatomical order, idle
  const rest = manifest.peel_order.filter((n) => n !== first && names.includes(n));
  const next = () => { const n = rest.shift(); if (n) ensureLoaded(n).then(() => setTimeout(next, 50)); };
  setTimeout(next, 800);
}
function frameAll() {
  const box = sceneBounds();
  const c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
  controls.target.copy(c);
  const dist = Math.max(s.y, s.x) / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2)) * 1.15;
  camera.position.set(c.x, c.y, c.z + dist);
  controls.update();
}
boot().catch((e) => { console.error(e); status.textContent = `error: ${e.message ?? e}`; });

renderer.setAnimationLoop(() => {
  controls.update();
  composer.render();
  updateCallout();
});

// debugging hooks
(window as any).anatomy = { scene, camera, controls, renderer, systems, materials: allTissueMaterials, sssPass, gtao, bloom, frameAll, select, ensureLoaded, applyVisibility };
