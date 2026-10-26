import json, re, html
from pathlib import Path
D=json.load(open('tecdeck/project/deck.json')); secs={v['start']:v['description'] for v in D['sections'].values()}
out=[]; cur=''
for sid in D['order']:
    t=Path(f'tecdeck/project/slides/{sid}.html').read_text(); t=re.sub(r'/_blob/([0-9a-f]{32})', r'deck/img/\1.png', t)
    note=''; m=re.search(r'<aside>(.*?)</aside>', t, re.S)
    if m: note=m.group(1).strip(); t=t.replace(m.group(0),'')
    if sid in secs: cur=secs[sid]
    hh=re.search(r'<h2[^>]*>(.*?)</h2>', t, re.S) or re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    out.append(dict(id=sid, section=cur, title=html.unescape(re.sub('<[^>]+>','',hh.group(1))).strip() if hh else sid, html=t, notes=note))
json.dump(dict(title=D['title'], slides=out), open('tecapp/deck/deck.json','w'), ensure_ascii=False); print(len(out))
