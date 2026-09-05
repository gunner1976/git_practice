import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { computeBoundsTree, disposeBoundsTree, acceleratedRaycast } from 'three-mesh-bvh';
import type { Manifest, OrganEntry } from './types';
import { tissueMaterial, applyMaskUniforms, sssMaskMaterial, organTint, type TissueMaterial } from './materials';

// three-mesh-bvh: fast raycasts over thousands of organ meshes
(THREE.BufferGeometry.prototype as any).computeBoundsTree = computeBoundsTree;
(THREE.BufferGeometry.prototype as any).disposeBoundsTree = disposeBoundsTree;
(THREE.Mesh.prototype as any).raycast = acceleratedRaycast;

export interface OrganMesh extends THREE.Mesh {
  material: TissueMaterial;
  userData: { zid: string; organ: OrganEntry; system: string; hidden?: boolean };
}

export interface LoadedSystem {
  name: string;
  group: THREE.Group;
  meshes: OrganMesh[];
  tris: number;
}

const loader = new GLTFLoader();
loader.setMeshoptDecoder(MeshoptDecoder);

export async function loadManifest(base: string): Promise<Manifest> {
  const r = await fetch(`${base}manifest.json`);
  if (!r.ok) throw new Error(`manifest: ${r.status}`);
  return r.json();
}

/** Prefer the Meshopt-compressed build if the pipeline produced one. */
async function pickUrl(base: string, file: string): Promise<string> {
  const opt = `${base}${file.replace(/\.glb$/, '.opt.glb')}`;
  try {
    const h = await fetch(opt, { method: 'HEAD' });
    if (h.ok) return opt;
  } catch { /* fall through */ }
  return `${base}${file}`;
}

export async function loadSystem(base: string, manifest: Manifest, name: string, onProgress?: (f: number) => void): Promise<LoadedSystem> {
  const sys = manifest.systems[name];
  const url = await pickUrl(base, sys.file);
  const gltf = await loader.loadAsync(url, (e) => { if (onProgress && e.total) onProgress(e.loaded / e.total); });
  const group = new THREE.Group();
  group.name = name;
  const meshes: OrganMesh[] = [];
  let tris = 0;
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.traverse((o) => {
    if (!(o as THREE.Mesh).isMesh) return;
    const src = o as THREE.Mesh;
    const zid: string | undefined = src.userData?.zid ?? src.parent?.userData?.zid;
    const organ = zid ? manifest.organs[zid] : undefined;
    if (!organ) return;
    const geom = src.geometry;
    // multi-material organs arrive as one primitive per material; the material name carries the tissue class
    const srcMat = src.material as THREE.MeshStandardMaterial;
    const cls = (srcMat?.name || '').replace(/^tissue_/, '').replace(/\.\d+$/, '') in manifest.tissue_classes ? (srcMat.name.replace(/^tissue_/, '').replace(/\.\d+$/, '')) : organ.tissue;
    const params = manifest.tissue_classes[cls] ?? manifest.tissue_classes['organ'];
    const mat = tissueMaterial(name, cls, params, srcMat);
    const mesh = new THREE.Mesh(geom, mat) as unknown as OrganMesh;
    // keep the node transform on the object: quantized (normalized int16) positions cannot hold metres if baked into the attribute
    mesh.applyMatrix4(src.matrixWorld);
    mesh.name = zid!;
    mesh.userData = { zid: zid!, organ, system: name };
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.frustumCulled = true;
    // the SSS mask pass draws every organ with one override material; feed it this organ's tissue values
    const tint = organTint(zid!);
    mesh.onBeforeRender = (_r, _s, _c, _g, material) => { if (material === sssMaskMaterial) applyMaskUniforms(mesh.material); else mesh.material.userData.uniforms!.uTint.value.copy(tint); };
    (geom as any).computeBoundsTree({ targetLeafSize: 8 });
    tris += (geom.index ? geom.index.count : geom.attributes.position.count) / 3;
    meshes.push(mesh);
    group.add(mesh);
  });
  return { name, group, meshes, tris: Math.round(tris) };
}
