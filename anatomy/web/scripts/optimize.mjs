#!/usr/bin/env node
// Post-process the per-system .glb files: dedup, prune, quantize and Meshopt-compress,
// keeping node names and extras (organ ids) intact. Reads/writes web/public/assets.
//
//   node optimize.mjs [--draco] [systems...]
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, quantize, reorder, flatten, join, weld } from '@gltf-transform/functions';
import { MeshoptEncoder } from 'meshoptimizer';
import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const cfg = JSON.parse(readFileSync(path.join(here, '..', '..', 'pipeline', 'config.json'), 'utf8'));
const assets = path.resolve(here, '..', '..', 'pipeline', cfg.output_dir);
const args = process.argv.slice(2);
const useDraco = args.includes('--draco');
const wanted = args.filter(a => !a.startsWith('--'));

await MeshoptEncoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ 'meshopt.encoder': MeshoptEncoder });
if (useDraco) {
  const draco3d = await import('draco3dgltf');
  io.registerDependencies({ 'draco3d.encoder': await draco3d.createEncoderModule() });
}

const files = readdirSync(assets).filter(f => f.endsWith('.glb') && !f.endsWith('.opt.glb') && (wanted.length === 0 || wanted.includes(f.replace('.glb', ''))));
for (const f of files) {
  const src = path.join(assets, f);
  const t = Date.now();
  const doc = await io.read(src);
  await doc.transform(
    dedup(),                              // shared tile textures and materials collapse to one copy
    weld({ tolerance: 0 }),
    prune(),
    quantize({ quantizePosition: 14, quantizeNormal: 10, quantizeTexcoord: 12, quantizeColor: 8 }),
    reorder({ encoder: MeshoptEncoder }),
  );
  if (useDraco) {
    doc.createExtension((await import('@gltf-transform/extensions')).KHRDracoMeshCompression).setRequired(true).setEncoderOptions({ method: 'edgebreaker' });
  } else {
    doc.createExtension((await import('@gltf-transform/extensions')).EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: 'filter' });
  }
  const out = src.replace(/\.glb$/, '.opt.glb');
  await io.write(out, doc);
  const a = statSync(src).size, b = statSync(out).size;
  console.log(`${f}: ${(a / 1e6).toFixed(1)} MB -> ${(b / 1e6).toFixed(1)} MB (${Math.round(100 * b / a)}%) in ${((Date.now() - t) / 1000).toFixed(1)}s`);
}
if (files.length === 0) console.log('nothing to optimise in', assets);
