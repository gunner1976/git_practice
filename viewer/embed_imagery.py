#!/usr/bin/env python3
"""Bake images from viewer/imagery/ into viewer/index.html.

Name each file by its slot key: body_front, body_back, body_side, heart_photo,
tissue_micrograph, cell_micrograph, mito_micrograph (.jpg/.jpeg/.png/.webp).
Keep each file under ~1.5 MB; the finished page must stay under 16 MB.
Run:  python3 viewer/embed_imagery.py
"""
import base64, json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
html = os.path.join(here, 'index.html'); imgdir = os.path.join(here, 'imagery')
keys = ['body_front','body_back','body_side','heart_photo','tissue_micrograph','cell_micrograph','mito_micrograph']
mime = {'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}
found = {}
if os.path.isdir(imgdir):
    for f in sorted(os.listdir(imgdir)):
        stem, ext = os.path.splitext(f)
        if stem in keys and ext.lower() in mime:
            with open(os.path.join(imgdir, f), 'rb') as fh: data = fh.read()
            found[stem] = 'data:%s;base64,%s' % (mime[ext.lower()], base64.b64encode(data).decode('ascii'))
            print('embedding %s (%.1f KB)' % (f, len(data)/1024))
src = open(html, encoding='utf-8').read()
a = src.index('/*EMBEDDED_IMAGERY_START*/'); b = src.index('/*EMBEDDED_IMAGERY_END*/')
block = '/*EMBEDDED_IMAGERY_START*/\nconst EMBEDDED_IMAGERY = ' + json.dumps(found) + ';\n'
src = src[:a] + block + src[b:]
open(html, 'w', encoding='utf-8').write(src)
print('wrote %s with %d embedded image(s); page is %.1f MB' % (html, len(found), len(src.encode('utf-8'))/1048576))
if len(src.encode('utf-8')) > 15.5*1048576: print('WARNING: page is close to the 16 MB artifact limit', file=sys.stderr)
