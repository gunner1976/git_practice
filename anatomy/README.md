# Anatomy Explorer

An interactive, photoreal human anatomy explorer for the web: mesh-based PBR
rendering of the Z-Anatomy atlas (CC-BY-SA 4.0), one glTF per organ system,
with per-organ selection, layering, peeling, section planes and lazy loading.

Everything is open source. See `LICENSES.md` for every asset and dependency.

## Layout

```
anatomy/
  LICENSES.md          every asset/dependency, license, compatibility verdict
  pipeline/
    config.json        systems, polygon budgets, exclusions, tissue rules, tissue material params
    build_assets.py    Blender (bpy) pipeline: source -> per-system .glb + manifest.json
    optimize.mjs       gltf-transform: dedup, quantize, Meshopt -> *.opt.glb
  web/                 Vite + TypeScript + three.js app
    src/main.ts        scene, lights, post chain, UI, selection, peel, section planes
    src/materials.ts   per-tissue MeshPhysicalMaterial (+ AO from COLOR_0, wrap SSS, clipping)
    src/sss.ts         screen-space separable subsurface scattering pass
    src/loader.ts      manifest + glTF loading, BVH raycasting
    public/assets/     pipeline output (CC-BY-SA 4.0): manifest.json, tiles/, <system>.glb
```

## Phase 1: asset pipeline

Requirements: Python 3.11 with `pip install bpy==5.0.1 numpy` (Blender as a
module, GPL, build-time only), Node 22 for the optimiser. The Z-Anatomy
repository (FBX exports) or its `.blend` files as input.

```
cd pipeline
python3 build_assets.py                      # all systems -> ../web/public/assets
python3 build_assets.py --systems skeletal   # one system
python3 build_assets.py --tiles-only         # just bake the tissue texture tiles
cd ../web && npm install && npm run optimize # Meshopt-compressed *.opt.glb
```

What the script does, per system (see the docstring for the full list):
import, keep names and the `.g` group hierarchy, drop helper objects and the
meshes whose upstream license is not open-source compatible, classify tissue
from source material + name, decimate to the per-system budget (proportional
share with a per-mesh floor), box-project UVs at a physical scale, bake
per-organ ambient occlusion into `COLOR_0` with only that system present,
assign one baked PBR tissue material per class, export `.glb` with the organ id
in each node's extras, and write `manifest.json`.

Textures: the tissue materials are authored procedurally in Blender nodes
(fibres, cavities, colour variation, bump) and baked to tileable albedo /
normal / roughness maps per tissue class. Per-organ maps are the AO bake. Full
per-organ unwrapped 4-map bakes for all ~5,000 meshes are not done in this
environment (hours of CPU time) and are not needed for the acceptance test;
the pipeline structure supports adding them for hero organs.

## Phase 2: renderer

`cd web && npm run dev` (or `npm run build && npm run preview`).

- `MeshPhysicalMaterial` per tissue class with the baked tiles, sheen,
  clearcoat and specular per class; `COLOR_0` drives indirect and specular
  occlusion, not albedo.
- Subsurface: a second render target receives the tissue's transmission colour
  and strength; a depth-aware, per-channel (red widest) separable blur of the
  lit image is blended back where tissue scatters (Jimenez-style), plus a
  wrapped/back-scatter diffuse term in the material for thin tissue.
- Lighting: CC0 Poly Haven HDRI through PMREM, one shadowed key light, a rim.
- Post: GTAO, bloom, ACES (OutputPass), SMAA, outline for selection.

## Phase 3: interaction

Raycast selection (three-mesh-bvh) with outline + callout, per-system
visibility/opacity, "peel" slider in anatomical order, sagittal / coronal /
transverse section planes, skeleton loads first and the rest lazily.

## Next: articulation (joints, ligaments, ranges of motion)

Z-Anatomy ships a joints file (capsules, ligaments, cartilage, menisci). The
plan is a joint database (type, axes, physiological range of motion per
degree of freedom, coupled motions) driving a skeleton rig, with ligaments and
muscles following their attachments, so that every actuation respects its
anatomical limits. Not started yet.
