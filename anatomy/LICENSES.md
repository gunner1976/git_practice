# Licenses and provenance

Every asset and dependency used by the anatomy explorer, with its license,
where it comes from, and how it is used. All entries were verified against
the upstream license text or the package registry metadata on 2026-09-05.
Nothing proprietary is used.

Two license families are involved and they are kept apart:

- **Code** (this repository's pipeline and web app, and the libraries it
  uses): permissive licenses (MIT, Apache-2.0, Zlib, GPL for Blender as a
  build tool only). Our own code is released under MIT (see `LICENSE`).
- **Anatomy assets** (meshes, textures baked from them, the manifest of organ
  names): **CC-BY-SA 4.0**, because they derive from Z-Anatomy / BodyParts3D.
  ShareAlike means every exported glTF, baked texture and the manifest is
  also CC-BY-SA 4.0 and must carry the attribution below. This does not
  affect the license of the code that loads them.

## Anatomy models

| Asset | Source | License | Compatible | Use |
|---|---|---|---|---|
| Z-Anatomy models (FBX exports, `Resources/Models/FBX/*.fbx`, and the `.blend` sources distributed by the project) | https://github.com/LluisV/Z-Anatomy, https://www.z-anatomy.com/atlas | CC-BY-SA 4.0 | Yes (share-alike) | Source meshes, organ names, system hierarchy |
| BodyParts3D (the model Z-Anatomy derives from) | Database Center for Life Science, Japan | CC-BY-SA 2.1 JP | Yes; SA 2.1 permits relicensing derivatives under a later SA version, which Z-Anatomy did (4.0) | Indirect, via Z-Anatomy |
| Z-Anatomy layer CSVs (`Resources/Layers/*.csv`) and organ descriptions (`Resources/Descriptions/*`) | same repository | CC-BY-SA 4.0 | Yes | System/collection membership for the manifest; optional descriptions |
| "Cranial Nerves and Foramina" (University of Dundee, CAHID), bundled inside Z-Anatomy | Z-Anatomy `License.txt` | CC-BY 4.0 | Yes | Part of the nervous system file |
| "Brainder" and "White matter" (University of Washington), bundled inside Z-Anatomy | Z-Anatomy `License.txt` | License not stated by upstream | **Unverified**: kept out of the build until the upstream license is confirmed (`EXCLUDE_UNVERIFIED` in the pipeline) | Brain surface / white matter meshes |
| "Anatomy of the Inner Ear" (University of Dundee School of Medicine), bundled inside Z-Anatomy | Z-Anatomy `License.txt` | CC-BY-NC-SA 4.0 | **No** (non-commercial clause is not open-source compatible) | Excluded from the build by name (cochlea, semicircular ducts, vestibule, etc.) |
| "Kidney" (lissiecowley), bundled inside Z-Anatomy | Z-Anatomy `License.txt` | CC-BY-NC 4.0 | **No** (non-commercial) | Excluded from the build by name (`Kidney.l`, `Kidney.r`); a CC-BY-SA replacement or an in-house model is needed |

Required attribution, shown in the app's About panel and in this file:

> "BodyParts3D - The Database Center for Life Science - CC-BY-SA 2.1 Japan"
> "Z-Anatomy - The open source atlas of anatomy - CC-BY-SA 4.0"
> "Cranial Nerves and Foramina - by University of Dundee, CAHID - CC-BY 4.0"

## Lighting

| Asset | Source | License | Compatible | Use |
|---|---|---|---|---|
| Poly Haven HDRIs (`studio`, `lab`, `warehouse`, ...) as repackaged 512x512 EXRs in `@pmndrs/assets` 1.7.0 | https://polyhaven.com/hdris via npm `@pmndrs/assets` | CC0-1.0 (package and assets) | Yes | Image-based lighting (PMREM). Full-resolution originals can be dropped into `web/public/hdri/` from polyhaven.com under the same CC0 license |

## Tools (build time only, not shipped)

| Tool | Version | License | Compatible | Use |
|---|---|---|---|---|
| Blender as a Python module (`bpy`) | 5.0.1 (PyPI) | GPL-2.0-or-later | Yes (tool; its license does not attach to the exported data) | FBX/.blend import, cleanup, decimation, procedural materials, texture baking, glTF export |
| Python | 3.11 | PSF | Yes | Pipeline scripts |
| Node.js / npm | 22 / 10 | MIT | Yes | Web build |
| `@gltf-transform/cli`, `core`, `functions`, `extensions` | 4.5.0 | MIT | Yes | glTF optimisation, Meshopt/Draco compression, texture resizing |
| `meshoptimizer` (JS) | 1.2.0 | MIT | Yes | Meshopt compression (encoder in the pipeline, decoder in the browser) |
| `draco3dgltf` | 1.5.7 | Apache-2.0 | Yes | Optional alternative compression |
| Vite | 8.2.2 | MIT | Yes | Dev server and bundler |
| TypeScript | 7.0.2 | Apache-2.0 | Yes | App language |

## Runtime libraries (shipped in the web bundle)

| Library | Version | License | Compatible | Use |
|---|---|---|---|---|
| three.js | 0.185.1 | MIT | Yes | Renderer, MeshPhysicalMaterial, PMREM, loaders, post-processing (`three/addons`) |
| three-mesh-bvh | 0.9.14 | MIT | Yes | Fast raycast selection over hundreds of meshes |
| `postprocessing` (pmndrs) | 6.39.4 | Zlib | Yes | SSAO/GTAO, bloom, SMAA effect passes (fallback: three's own `EffectComposer`) |
| `@pmndrs/assets` | 1.7.0 | CC0-1.0 | Yes | HDRIs (see Lighting) |
| Babylon.js (alternative renderer, only if three.js SSS quality is insufficient) | 8.x | Apache-2.0 | Yes | Not used unless the acceptance test fails |

## Not used, and why

- Google Drive `.blend` distribution of Z-Anatomy: same license as the FBX
  exports, but this build environment cannot reach Google Drive. The pipeline
  accepts either `.blend` or `.fbx` input; drop the `.blend` files into
  `pipeline/input/` to use them.
- Any commercial anatomy asset packs, Unity/Unreal SDKs, or hosted rendering
  services: excluded by the project constraints.
