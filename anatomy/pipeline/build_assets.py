#!/usr/bin/env python3
"""
Z-Anatomy -> per-system glTF asset pipeline (Blender as a Python module).

    python3 build_assets.py [--systems skeletal,muscular] [--no-bake] [--no-decimate]
                            [--tiles-only] [--limit N] [--config config.json]

For every organ system listed in config.json this script
  1. imports the Z-Anatomy source file (FBX from the repository, or the .blend
     distributed by the project; either works),
  2. keeps the organ names and the group hierarchy as authored (".g" groups),
  3. drops helper objects and every mesh whose upstream license is not
     open-source compatible (see LICENSES.md),
  4. classifies every mesh into a tissue class from its source material name
     and its anatomical name,
  5. decimates each mesh so that the whole system fits its polygon budget,
  6. gives every mesh a box-projected UV set so tissue textures tile at a
     physical scale,
  7. bakes ambient occlusion per organ into vertex colours (COLOR_0), with only
     that system present so peeling never leaves baked shadows behind,
  8. bakes the procedural tissue materials to albedo / normal / roughness tiles
     once, and assigns one exportable PBR material per tissue class,
  9. exports one .glb per system with the organ id in each node's extras,
 10. writes manifest.json (mesh id -> organ name, system, parent chain, side,
     tissue class, display metadata, description) plus the attribution block.

Everything is deterministic and repeatable; re-running only rebuilds what is
requested. Run `node optimize.mjs` afterwards for Meshopt compression.
"""
import argparse, json, math, os, re, sys, time, hashlib
import numpy as np
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------
def log(*a):
    print('[pipeline]', *a, flush=True)


def slug(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s or 'x'


# Z-Anatomy name suffixes: .l/.r side; .j and .i are 6-triangle label anchors (landmarks);
# .ol/.or and .el/.er are muscle origin and insertion footprints (left/right).
ROLE_SUFFIX = {'j': 'landmark', 'i': 'landmark', 'ol': 'origin', 'or': 'origin', 'el': 'insertion', 'er': 'insertion'}


def strip_suffix(name):
    """'Deltoid muscle.l' -> ('Deltoid muscle', 'l', 'organ'); 'Deltoid muscle.ol' -> (..., 'l', 'origin')."""
    name = re.sub(r'\.\d{3}$', '', name)
    side, role = None, 'organ'
    m = re.match(r'^(.*)\.([a-zA-Z]{1,2})$', name)
    if m and (m.group(2).lower() in ('l', 'r') or m.group(2).lower() in ROLE_SUFFIX):
        suf = m.group(2).lower()
        name = m.group(1)
        if suf in ('l', 'r'):
            side = suf
        else:
            role = ROLE_SUFFIX[suf]
            if suf in ('ol', 'el'):
                side = 'l'
            elif suf in ('or', 'er'):
                side = 'r'
    return name, side, role


def display_name(name):
    n = name.strip()
    n = re.sub(r'^\((.*)\)$', r'\1', n)          # optional structures are bracketed upstream
    return n


def ancestors(obj):
    chain = []
    p = obj.parent
    while p is not None:
        chain.append(p.name)
        p = p.parent
    return chain  # nearest first


def valid_op_kwargs(op, kwargs):
    """Only pass properties the installed exporter actually has (names drift between Blender versions)."""
    props = set(op.get_rna_type().properties.keys())
    out = {k: v for k, v in kwargs.items() if k in props}
    dropped = [k for k in kwargs if k not in props]
    if dropped:
        log('exporter does not know', dropped, '- skipped')
    return out


def read_descriptions(d):
    out = {}
    if not d or not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        if not fn.endswith('.txt'):
            continue
        key = display_name(fn[:-4])
        try:
            with open(os.path.join(d, fn), encoding='utf-8', errors='replace') as f:
                txt = f.read().strip()
        except OSError:
            continue
        # upstream files start with the name in capitals; keep the body
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        if lines and lines[0].strip('()').upper() == key.upper():
            lines = lines[1:]
        body = ' '.join(lines).strip()
        if body:
            out[key.lower()] = body
    return out


# ----------------------------------------------------------------------------
# procedural tissue materials (authored in nodes, baked to tiles, never hand painted)
# ----------------------------------------------------------------------------
def make_procedural_material(cls, p):
    """A Cycles node tree for one tissue class. Fibrous classes get anisotropic striations,
    everything gets multi-octave colour variation, pores/cavities and a bump field."""
    mat = bpy.data.materials.new('proc_' + cls)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n = nt.nodes
    L = nt.links
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = n.new('ShaderNodeTexCoord')
    mapping = n.new('ShaderNodeMapping')
    L.new(tc.outputs['UV'], mapping.inputs['Vector'])
    fib = float(p.get('fibrous', 0.0))
    # stretch the noise along V for fibres
    mapping.inputs['Scale'].default_value = (1.0, 1.0 + 6.0 * fib, 1.0)

    def noise(scale, detail=4.0, rough=0.5, distortion=0.0):
        nd = n.new('ShaderNodeTexNoise')
        nd.inputs['Scale'].default_value = scale
        nd.inputs['Detail'].default_value = detail
        nd.inputs['Roughness'].default_value = rough
        nd.inputs['Distortion'].default_value = distortion
        L.new(mapping.outputs['Vector'], nd.inputs['Vector'])
        return nd

    # colour: base tone with two octaves of hue/value variation, darker cavities
    base = n.new('ShaderNodeRGB')
    c = p['color']
    base.outputs[0].default_value = (c[0], c[1], c[2], 1.0)
    var = noise(4.0, 6.0, 0.55)
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.72, 0.68, 0.66, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (1.18, 1.14, 1.10, 1)
    L.new(var.outputs['Fac'], ramp.inputs['Fac'])
    mixv = n.new('ShaderNodeMix')
    mixv.data_type = 'RGBA'
    mixv.blend_type = 'MULTIPLY'
    mixv.inputs['Factor'].default_value = 1.0
    L.new(base.outputs[0], mixv.inputs[6])
    L.new(ramp.outputs['Color'], mixv.inputs[7])
    cav = noise(18.0, 3.0, 0.7)
    cramp = n.new('ShaderNodeValToRGB')
    cramp.color_ramp.elements[0].position = 0.42
    cramp.color_ramp.elements[0].color = (1 - 0.45 * p['cavity'],) * 3 + (1,)
    cramp.color_ramp.elements[1].position = 0.6
    cramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    L.new(cav.outputs['Fac'], cramp.inputs['Fac'])
    mixc = n.new('ShaderNodeMix')
    mixc.data_type = 'RGBA'
    mixc.blend_type = 'MULTIPLY'
    mixc.inputs['Factor'].default_value = 1.0
    L.new(mixv.outputs[2], mixc.inputs[6])
    L.new(cramp.outputs['Color'], mixc.inputs[7])
    color_out = mixc.outputs[2]
    if fib > 0:
        wave = n.new('ShaderNodeTexWave')
        wave.wave_type = 'BANDS'
        wave.bands_direction = 'Y'
        wave.inputs['Scale'].default_value = 14.0 * (0.5 + fib)
        wave.inputs['Distortion'].default_value = 2.5
        wave.inputs['Detail'].default_value = 3.0
        L.new(mapping.outputs['Vector'], wave.inputs['Vector'])
        wramp = n.new('ShaderNodeValToRGB')
        wramp.color_ramp.elements[0].position = 0.3
        wramp.color_ramp.elements[0].color = (1 - 0.22 * fib,) * 3 + (1,)
        wramp.color_ramp.elements[1].position = 0.8
        wramp.color_ramp.elements[1].color = (1.06, 1.04, 1.03, 1)
        L.new(wave.outputs['Fac'], wramp.inputs['Fac'])
        mixw = n.new('ShaderNodeMix')
        mixw.data_type = 'RGBA'
        mixw.blend_type = 'MULTIPLY'
        mixw.inputs['Factor'].default_value = 1.0
        L.new(color_out, mixw.inputs[6])
        L.new(wramp.outputs['Color'], mixw.inputs[7])
        color_out = mixw.outputs[2]
    L.new(color_out, bsdf.inputs['Base Color'])

    # roughness: base +/- variation, wetter in cavities
    rn = noise(9.0, 4.0, 0.6)
    rmap = n.new('ShaderNodeMapRange')
    rmap.inputs['From Min'].default_value = 0.0
    rmap.inputs['From Max'].default_value = 1.0
    rmap.inputs['To Min'].default_value = max(0.02, p['roughness'] - 0.12)
    rmap.inputs['To Max'].default_value = min(0.98, p['roughness'] + 0.12)
    L.new(rn.outputs['Fac'], rmap.inputs['Value'])
    L.new(rmap.outputs['Result'], bsdf.inputs['Roughness'])

    # bump: cavities plus fibres
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = p['bump']
    bump.inputs['Distance'].default_value = 0.02
    bn = noise(22.0, 5.0, 0.6, 0.3)
    if fib > 0:
        bmix = n.new('ShaderNodeMix')
        bmix.data_type = 'FLOAT'
        bmix.inputs['Factor'].default_value = 0.5 * fib
        L.new(bn.outputs['Fac'], bmix.inputs[2])
        L.new(wave.outputs['Fac'], bmix.inputs[3])
        L.new(bmix.outputs[0], bump.inputs['Height'])
    else:
        L.new(bn.outputs['Fac'], bump.inputs['Height'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    bsdf.inputs['Metallic'].default_value = 0.0
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = p['specular']
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = p['clearcoat']
        bsdf.inputs['Coat Roughness'].default_value = p['coat_rough']
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = p['sheen']
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = p['sss']
        sc = p['sss_color']
        if 'Subsurface Radius' in bsdf.inputs:
            bsdf.inputs['Subsurface Radius'].default_value = (sc[0] * 0.02, sc[1] * 0.02, sc[2] * 0.02)
    return mat


def bake_tiles(cfg, tiles_dir, force=False):
    """Bake every tissue class's procedural material to albedo / normal / roughness tiles on a unit plane."""
    res = int(cfg.get('tile_resolution', 1024))
    os.makedirs(tiles_dir, exist_ok=True)
    classes = cfg['tissue_classes']
    todo = [c for c in classes if force or not all(os.path.exists(os.path.join(tiles_dir, f'{c}_{k}.png')) for k in ('albedo', 'normal', 'roughness'))]
    if not todo:
        log('tiles: all', len(classes), 'classes present')
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1                      # colour/roughness/normal bakes are deterministic: one sample is exact
    scene.cycles.use_denoising = False
    scene.render.bake.margin = 8
    world = bpy.data.worlds.new('w')
    scene.world = world
    # a flat unit plane with a 0..1 UV
    mesh = bpy.data.meshes.new('plane')
    mesh.from_pydata([(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [], [(0, 1, 2, 3)])
    uv = mesh.uv_layers.new(name='UVMap')
    uv.data.foreach_set('uv', [0, 0, 1, 0, 1, 1, 0, 1])
    plane = bpy.data.objects.new('plane', mesh)
    scene.collection.objects.link(plane)
    for cls in todo:
        p = classes[cls]
        mat = make_procedural_material(cls, p)
        plane.data.materials.clear()
        plane.data.materials.append(mat)
        nt = mat.node_tree
        for kind, btype, cs in (('albedo', 'DIFFUSE', 'sRGB'), ('normal', 'NORMAL', 'Non-Color'), ('roughness', 'ROUGHNESS', 'Non-Color')):
            img = bpy.data.images.new(f'{cls}_{kind}', res, res, alpha=False, float_buffer=False)
            img.colorspace_settings.name = cs
            tex = nt.nodes.new('ShaderNodeTexImage')
            tex.image = img
            nt.nodes.active = tex
            t = time.time()
            with bpy.context.temp_override(object=plane, active_object=plane, selected_objects=[plane], selected_editable_objects=[plane]):
                kw = dict(type=btype, margin=8, use_clear=True)
                if btype == 'DIFFUSE':
                    kw.update(pass_filter={'COLOR'})
                if btype == 'NORMAL':
                    kw.update(normal_space='TANGENT')
                bpy.ops.object.bake(**kw)
            path = os.path.join(tiles_dir, f'{cls}_{kind}.png')
            img.filepath_raw = path
            img.file_format = 'PNG'
            img.save()
            nt.nodes.remove(tex)
            bpy.data.images.remove(img)
            log(f'tile {cls} {kind} {res}px {time.time()-t:.1f}s')
        bpy.data.materials.remove(mat)


def make_export_material(cls, p, tiles_dir, cache):
    """Exportable PBR material: baked tiles + constant sheen/coat/specular, tinted by class colour."""
    if cls in cache:
        return cache[cls]
    mat = bpy.data.materials.new('tissue_' + cls)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n, L = nt.nodes, nt.links
    out = n.new('ShaderNodeOutputMaterial')
    bsdf = n.new('ShaderNodeBsdfPrincipled')
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

    def image(kind, cs):
        path = os.path.join(tiles_dir, f'{cls}_{kind}.png')
        key = f'{cls}_{kind}'
        img = bpy.data.images.get(key)
        if img is None:
            img = bpy.data.images.load(path)
            img.name = key
            img.colorspace_settings.name = cs
        tex = n.new('ShaderNodeTexImage')
        tex.image = img
        return tex

    alb = image('albedo', 'sRGB')
    L.new(alb.outputs['Color'], bsdf.inputs['Base Color'])
    rough = image('roughness', 'Non-Color')
    L.new(rough.outputs['Color'], bsdf.inputs['Roughness'])
    nrm = image('normal', 'Non-Color')
    nm = n.new('ShaderNodeNormalMap')
    nm.inputs['Strength'].default_value = 1.0
    L.new(nrm.outputs['Color'], nm.inputs['Color'])
    L.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Metallic'].default_value = 0.0
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = p['specular']
    if 'Coat Weight' in bsdf.inputs:
        bsdf.inputs['Coat Weight'].default_value = p['clearcoat']
        bsdf.inputs['Coat Roughness'].default_value = p['coat_rough']
    if 'Sheen Weight' in bsdf.inputs:
        bsdf.inputs['Sheen Weight'].default_value = p['sheen']
    mat['tissue'] = cls
    cache[cls] = mat
    return mat


# ----------------------------------------------------------------------------
# geometry stages
# ----------------------------------------------------------------------------
def bake_world_transform(obj):
    m = obj.matrix_world.copy()
    obj.data.transform(m)
    obj.matrix_world = Matrix.Identity(4)
    obj.parent = None


def box_uv(mesh, scale):
    """Box (triplanar-choice) UVs per loop from world-space positions, so tiles repeat every `scale` metres."""
    nv, nl, npoly = len(mesh.vertices), len(mesh.loops), len(mesh.polygons)
    if nl == 0:
        return
    co = np.empty(nv * 3, dtype=np.float32)
    mesh.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    vi = np.empty(nl, dtype=np.int32)
    mesh.loops.foreach_get('vertex_index', vi)
    pn = np.empty(npoly * 3, dtype=np.float32)
    mesh.polygons.foreach_get('normal', pn)
    pn = pn.reshape(-1, 3)
    ltot = np.empty(npoly, dtype=np.int32)
    mesh.polygons.foreach_get('loop_total', ltot)
    lpoly = np.repeat(np.arange(npoly, dtype=np.int32), ltot)
    an = np.abs(pn[lpoly])
    axis = np.argmax(an, axis=1)
    p = co[vi] / scale
    u = np.where(axis == 0, p[:, 1], np.where(axis == 1, p[:, 0], p[:, 0]))
    v = np.where(axis == 0, p[:, 2], np.where(axis == 1, p[:, 2], p[:, 1]))
    uv = np.stack([u, v], axis=1).astype(np.float32).ravel()
    layer = mesh.uv_layers.get('box') or mesh.uv_layers.new(name='box')
    layer.data.foreach_set('uv', uv)
    mesh.uv_layers.active = layer
    for l in mesh.uv_layers:
        l.active_render = (l.name == 'box')


def tri_count(mesh):
    """Triangle count after triangulation (the source has quads and n-gons)."""
    n = len(mesh.polygons)
    if n == 0:
        return 0
    lt = np.empty(n, dtype=np.int32)
    mesh.polygons.foreach_get('loop_total', lt)
    return int((lt - 2).sum())


def plan_decimation(objs, budget, min_tris, floor_ratio):
    """Distribute the system budget over meshes proportionally to their size, with a floor per mesh."""
    counts = {o.name: tri_count(o.data) for o in objs}
    total = sum(counts.values())
    if total <= budget:
        return {}
    ratios = {}
    # small meshes keep everything; the rest share what is left
    small = {k: v for k, v in counts.items() if v <= min_tris}
    remaining = budget - sum(small.values())
    big_total = total - sum(small.values())
    if remaining <= 0 or big_total <= 0:
        return {}
    r = remaining / big_total
    for k, v in counts.items():
        if k in small:
            continue
        target = max(min_tris, v * r)
        ratios[k] = max(floor_ratio, min(1.0, target / v))
    return ratios


def apply_decimation(names, ratios):
    """Works by object name: removing data-blocks invalidates Python handles to other objects."""
    if not ratios:
        return
    for nm in names:
        r = ratios.get(nm)
        if r is None or r >= 0.999:
            continue
        mod = bpy.data.objects[nm].modifiers.new('dec', 'DECIMATE')
        mod.decimate_type = 'COLLAPSE'
        mod.ratio = r
        mod.use_collapse_triangulate = True
        mod.use_symmetry = False
    dg = bpy.context.evaluated_depsgraph_get()
    old_meshes = []
    for nm in names:
        o = bpy.data.objects[nm]
        if not o.modifiers:
            continue
        ev = o.evaluated_get(dg)
        newm = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
        old_meshes.append(o.data.name)
        o.modifiers.clear()
        o.data = newm
    for mn in old_meshes:
        m = bpy.data.meshes.get(mn)
        if m is not None and m.users == 0:
            bpy.data.meshes.remove(m)


def bake_vertex_ao(objs, samples, distance):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    if scene.world is None:
        scene.world = bpy.data.worlds.new('w')
    scene.world.light_settings.distance = distance
    scene.render.bake.target = 'VERTEX_COLORS'
    for o in objs:
        m = o.data
        attr = m.color_attributes.get('AO') or m.color_attributes.new(name='AO', type='BYTE_COLOR', domain='CORNER')
        m.color_attributes.active_color = attr
        m.color_attributes.render_color_index = list(m.color_attributes).index(attr)
    t = time.time()
    with bpy.context.temp_override(object=objs[0], active_object=objs[0], selected_objects=list(objs), selected_editable_objects=list(objs)):
        bpy.ops.object.bake(type='AO', target='VERTEX_COLORS')
    log(f'AO baked for {len(objs)} meshes, {samples} samples, {time.time()-t:.0f}s')


# ----------------------------------------------------------------------------
# main per-system build
# ----------------------------------------------------------------------------
def import_source(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.lower().endswith('.blend'):
        bpy.ops.wm.open_mainfile(filepath=path)
    elif path.lower().endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=path)
    else:
        raise SystemExit('unsupported source: ' + path)


def classify(obj, rules, default):
    matname = obj.data.materials[0].name if obj.data.materials and obj.data.materials[0] else ''
    matname = re.sub(r'\.\d{3}$', '', matname)
    name, _, _ = strip_suffix(obj.name)
    name = display_name(name)
    for r in rules:
        if r.get('material') and re.search(r['material'], matname, re.I):
            return r['class'], matname
    for r in rules:
        if r.get('name') and re.search(r['name'], name, re.I):
            return r['class'], matname
    return default, matname


def build_system(sysname, spec, cfg, args, descriptions, manifest, out_dir, tiles_dir):
    src = os.path.join(cfg['input_dir'], spec['file'])
    if os.path.isdir(cfg.get('blend_dir', '')):
        alt = os.path.join(cfg['blend_dir'], os.path.splitext(spec['file'])[0] + '.blend')
        if os.path.exists(alt):
            src = alt
    t0 = time.time()
    log(f'== {sysname}: importing {os.path.basename(src)}')
    import_source(src)
    scene = bpy.context.scene
    objs = [o for o in scene.objects if o.type == 'MESH']
    roots = spec.get('roots')
    excl_pat = [re.compile(p) for p in cfg.get('exclude_name_patterns', [])]
    excl_lic = [(why, [re.compile(p) for p in pats]) for why, pats in cfg.get('exclude_licensed', {}).items()]
    keep, excluded, landmarks = [], [], []
    for o in objs:
        chain = ancestors(o)
        root = chain[-1] if chain else o.name
        if roots and root not in roots:
            continue                                  # belongs to another system of the same file
        bare, _, role = strip_suffix(o.name)
        if '?' in o.name:
            excluded.append({'name': o.name, 'reason': 'unnamed placeholder'})
            continue
        if role == 'landmark':
            landmarks.append(o)
            continue
        if any(p.search(o.name) for p in excl_pat):
            excluded.append({'name': o.name, 'reason': 'helper object'})
            continue
        why = next((w for w, pats in excl_lic if any(p.search(bare) for p in pats)), None)
        if why:
            excluded.append({'name': o.name, 'reason': why})
            continue
        if tri_count(o.data) == 0:
            excluded.append({'name': o.name, 'reason': 'empty mesh'})
            continue
        keep.append(o)
    if args.limit:
        keep = keep[:args.limit]
    lm_entries = []
    for o in landmarks:
        bare, side, _ = strip_suffix(o.name)
        chain = ancestors(o)
        pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
        c = [round(sum(p[i] for p in pts) / 8.0, 4) for i in range(3)]
        lm_entries.append({'name': display_name(bare), 'side': side, 'system': sysname, 'parents': [display_name(strip_suffix(x)[0]) for x in chain], 'position': c})
    log(f'{sysname}: {len(keep)} meshes kept, {len(landmarks)} landmarks, {len(excluded)} excluded, {sum(tri_count(o.data) for o in keep)} tris')

    # metadata before geometry is touched
    entries = {}
    used_ids = set()
    for o in keep:
        chain = ancestors(o)
        bare, side, role = strip_suffix(o.name)
        disp = display_name(bare)
        cls, matname = classify(o, cfg['tissue_rules'], cfg['default_class'])
        base_id = slug(disp) + (('-' + role) if role != 'organ' else '') + (('-' + side) if side else '')
        oid = base_id
        k = 2
        while oid in used_ids or oid in manifest['organs']:
            oid = f'{base_id}-{k}'
            k += 1
        used_ids.add(oid)
        o['zid'] = oid
        entries[o.name] = {
            'id': oid, 'name': disp, 'source_name': o.name, 'side': side, 'role': role, 'system': sysname,
            'parents': [display_name(strip_suffix(c)[0]) for c in chain],
            'tissue': cls, 'source_material': matname,
            'optional': bare.startswith('('),
            'tris_source': tri_count(o.data),
            'description': descriptions.get(disp.lower()),
        }

    # flatten transforms, drop everything else from the scene
    for o in keep:
        bake_world_transform(o)
    for o in list(scene.objects):
        if o not in keep:
            bpy.data.objects.remove(o, do_unlink=True)
    scale = float(cfg.get('scale', 1.0))
    if scale != 1.0:
        for o in keep:
            o.data.transform(Matrix.Scale(scale, 4))

    # decimation to the budget
    if not args.no_decimate:
        ratios = plan_decimation(keep, int(spec['budget']), int(cfg['min_tris_per_mesh']), float(cfg['decimate_floor_ratio']))
        t = time.time()
        keep_names = [o.name for o in keep]
        apply_decimation(keep_names, ratios)
        keep = [bpy.data.objects[n] for n in keep_names]     # fresh handles: data-block removal invalidates the old ones
        log(f'{sysname}: decimated {len(ratios)} meshes -> {sum(tri_count(o.data) for o in keep)} tris ({time.time()-t:.0f}s)')

    # UVs, materials, per-organ AO
    matcache = {}
    for o in keep:
        box_uv(o.data, float(cfg['tile_scale_m']))
        cls = entries[o.name]['tissue']
        o.data.materials.clear()
        o.data.materials.append(make_export_material(cls, cfg['tissue_classes'][cls], tiles_dir, matcache))
    if not args.no_bake:
        bake_vertex_ao(keep, int(cfg['ao_samples']), float(cfg['ao_distance']))

    # bounds and final stats
    for o in keep:
        e = entries[o.name]
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        lo = [min(v[i] for v in bb) for i in range(3)]
        hi = [max(v[i] for v in bb) for i in range(3)]
        e['bbox'] = {'min': [round(x, 4) for x in lo], 'max': [round(x, 4) for x in hi]}
        e['tris'] = tri_count(o.data)
        o.name = e['id']

    # export
    out_path = os.path.join(out_dir, f'{sysname}.glb')
    kw = dict(filepath=out_path, export_format='GLB', use_selection=True, export_apply=True, export_extras=True,
              export_yup=True, export_texcoords=True, export_normals=True, export_materials='EXPORT',
              export_image_format='AUTO', export_animations=False, export_skins=False, export_morph=False,
              export_lights=False, export_cameras=False, export_vertex_color='ACTIVE',
              export_active_vertex_color_when_no_material=True, export_all_vertex_colors=False,
              export_tangents=False, export_attributes=False, export_jpeg_quality=90)
    with bpy.context.temp_override(selected_objects=list(keep), active_object=keep[0], object=keep[0]):
        bpy.ops.export_scene.gltf(**valid_op_kwargs(bpy.ops.export_scene.gltf, kw))
    size = os.path.getsize(out_path)
    tris = sum(e['tris'] for e in entries.values())
    log(f'{sysname}: wrote {out_path} {size/1e6:.1f} MB, {tris} tris, {time.time()-t0:.0f}s total')

    manifest['systems'][sysname] = {
        'file': f'{sysname}.glb', 'order': spec.get('order', 0), 'budget': spec['budget'],
        'source': os.path.basename(src), 'meshes': len(keep), 'tris': tris, 'bytes': size,
        'excluded': excluded, 'landmarks': lm_entries,
    }
    for e in entries.values():
        manifest['organs'][e['id']] = e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', default=os.path.join(HERE, 'config.json'))
    ap.add_argument('--systems', default='')
    ap.add_argument('--no-bake', action='store_true')
    ap.add_argument('--no-decimate', action='store_true')
    ap.add_argument('--tiles-only', action='store_true')
    ap.add_argument('--rebake-tiles', action='store_true')
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args(sys.argv[1:] if '--' not in sys.argv else sys.argv[sys.argv.index('--') + 1:])
    with open(args.config) as f:
        cfg = json.load(f)
    out_dir = os.path.normpath(os.path.join(HERE, cfg['output_dir']))
    tiles_dir = os.path.join(out_dir, 'tiles')
    os.makedirs(out_dir, exist_ok=True)

    bake_tiles(cfg, tiles_dir, force=args.rebake_tiles)
    if args.tiles_only:
        return

    descriptions = read_descriptions(cfg.get('descriptions_dir'))
    log('descriptions:', len(descriptions))
    manifest_path = os.path.join(out_dir, 'manifest.json')
    manifest = {'systems': {}, 'organs': {}}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
            manifest.setdefault('systems', {})
            manifest.setdefault('organs', {})
    wanted = [s for s in args.systems.split(',') if s] or list(cfg['systems'].keys())
    for s in wanted:
        if s not in cfg['systems']:
            raise SystemExit('unknown system ' + s)
        # drop stale entries for this system
        manifest['organs'] = {k: v for k, v in manifest['organs'].items() if v['system'] != s}
        build_system(s, cfg['systems'][s], cfg, args, descriptions, manifest, out_dir, tiles_dir)
        manifest['generated'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        manifest['peel_order'] = cfg['peel_order']
        manifest['tissue_classes'] = cfg['tissue_classes']
        manifest['attribution'] = [
            'BodyParts3D - The Database Center for Life Science - CC-BY-SA 2.1 Japan',
            'Z-Anatomy - The open source atlas of anatomy - CC-BY-SA 4.0',
            'Cranial Nerves and Foramina - by University of Dundee, CAHID - CC-BY 4.0',
        ]
        manifest['license'] = 'CC-BY-SA 4.0 (derived assets: meshes, baked textures, this manifest)'
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=1, sort_keys=False)
        log('manifest:', manifest_path, len(manifest['organs']), 'organs')


if __name__ == '__main__':
    main()
