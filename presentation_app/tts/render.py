"""Pre-render the presentation narration with a neural voice: one MP3 per slide plus caption timings.
Usage: venv/bin/python -I render.py <voice_id> <engine kokoro|piper> <model voice> <lang> <narration.json> <out_dir>
Writes <out_dir>/<voice_id>/<slideId>__<step>.mp3 (one file per step, so playback never seeks) and <out_dir>/<voice_id>.json =
{slideId: {step: [[t0, t1, caption], ...]}} with times relative to the step file.
Captions are the written text; the engine gets the spoken form (same rules as the app's say()/sayEs()).
"""
import json, re, subprocess, sys, wave, io
from pathlib import Path
import numpy as np, soundfile as sf

vid, engine, model, lang, src, out = sys.argv[1:7]
OUT = Path(out); (OUT / vid).mkdir(parents=True, exist_ok=True)
N = json.load(open(src))
SR = 24000

def sentences(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return [s.strip() for s in re.split(r'(?<=[.!?;])\s+(?=[A-Z0-9“"(‘\'¿¡ÁÉÍÓÚÑ])', t) if s.strip()]
def chunks(t):   # same grouping as Narrator.chunks in engine.js
    out = []
    for s in sentences(t):
        if out and len(out[-1]) + len(s) < 220: out[-1] += ' ' + s
        else: out.append(s)
    return out

ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = {2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty', 6: 'sixty', 7: 'seventy', 8: 'eighty', 9: 'ninety'}
def two(n):
    return ONES[n] if n < 20 else TENS[n // 10] + ('-' + ONES[n % 10] if n % 10 else '')
def year_en(m):   # 1980 -> "nineteen eighty", 1907 -> "nineteen oh seven", 1960s -> "nineteen sixties" (2000s stay as the engine reads them)
    y, plural = int(m.group(1)), m.group(2)
    yy = y % 100; w = 'hundred' if yy == 0 else ('oh ' + ONES[yy] if yy < 10 else two(yy))
    if plural: w = (w[:-1] + 'ies') if w.endswith('y') else w + 's'
    return 'nineteen ' + w
def say_en(t):
    t = re.sub(r'(?<![\d,.])(19\d\d)(s?)(?!\d|,\d)', year_en, t)
    R = [(r'TEC-(\d+)', r'tech \1'), (r'\bmSS\b', 'metres subsea'), (r'\bmMD\b', 'metres measured depth'), (r'(\d)\s?bbl/d', r'\1 barrels a day'),
         (r'\bbbl\b', 'barrels'), (r'\bkbbl\b', 'thousand barrels'), (r'\bMMbbl\b', 'million barrels'), (r'USD\s?([\d.,]+)\s?MM\b', r'\1 million dollars'),
         (r'USD\s?([\d.,]+)\s?k\b', r'\1 thousand dollars'), (r'\bUSD\b', 'US dollars'), (r'kg/cm²', 'kilograms per square centimetre'), (r'\bpsi\b', 'p s i'),
         (r'°API', ' degrees A P I'), (r'(\d)\s?%', r'\1 percent'), (r'\bNPV10\b', 'N P V ten'), (r'\bGOR\b', 'G O R'), (r'\bPVT\b', 'P V T'), (r'\bPSTM\b', 'P S T M'),
         (r'\bPSDM\b', 'P S D M'), (r'\bCNH\b', 'C N H'), (r'\bGLJ\b', 'G L J'), (r'\bAFE\b', 'A F E'), (r'\bWTI\b', 'W T I'), (r'\bOOIP\b', 'original oil in place'),
         (r'\bCAB\b', 'C A B'), (r'\bTM-01\b', 'T M zero one'), (r'\bPEMEX\b', 'Pemex'), (r'\bIRR\b', 'I R R'), ('–', ' to '), ('−', 'minus '), ('×', ' times '), ('≈', 'about ')]
    for a, b in R: t = re.sub(a, b, t)
    return t
def say_es(t):
    R = [(r'TEC-(\d+)', r'Tec \1'), (r'\bmSS\b', 'metros bajo el nivel del mar'), (r'\bmMD\b', 'metros desarrollados'), (r'(\d)\s?bbl/d', r'\1 barriles por día'),
         (r'\bkbbl\b', 'mil barriles'), (r'\bMMbbl\b', 'millones de barriles'), (r'\bbbl\b', 'barriles'), (r'USD\s?([\d.,]+)\s?MM\b', r'\1 millones de dólares'),
         (r'USD\s?([\d.,]+)\s?k\b', r'\1 mil dólares'), (r'\bUSD\b', 'dólares'), (r'kg/cm²', 'kilogramos por centímetro cuadrado'), (r'°API', ' grados API'),
         (r'(\d)\s?%', r'\1 por ciento'), (r'\bCNH\b', 'C N H'), (r'\bGLJ\b', 'G L J'), (r'\bWTI\b', 'W T I'), (r'\bPVT\b', 'P V T'), (r'\bCAB\b', 'C A B'),
         (r'\bTM-01\b', 'T M cero uno'), (r'\bPEMEX\b', 'Pemex'), (r'(\d),(\d{3})', r'\1\2'), ('–', ' a '), ('−', 'menos '), ('×', ' por '), ('≈', 'aproximadamente ')]
    for a, b in R: t = re.sub(a, b, t)
    t = re.sub(r'(\d),(\d{3})', r'\1\2', t)   # thousands separators (a Spanish engine reads the comma as a decimal point)
    return t
spoken = say_es if lang.startswith('es') else say_en

if engine == 'kokoro':
    from kokoro_onnx import Kokoro
    K = Kokoro('kokoro-v1.0.onnx', 'voices-v1.0.bin')
    def synth(t):
        a, sr = K.create(t, voice=model, speed=1.0, lang=lang); assert sr == SR; return a.astype(np.float32)
else:
    from piper import PiperVoice
    PV = PiperVoice.load(model)
    def synth(t):
        b = io.BytesIO()
        with wave.open(b, 'wb') as w: PV.synthesize_wav(t, w)
        b.seek(0); a, sr = sf.read(b, dtype='float32')
        if sr != SR:  # resample to 24 kHz by linear interpolation (Piper voices are 22.05 kHz)
            x = np.arange(len(a)) / sr; a = np.interp(np.arange(int(len(a) * SR / sr)) / SR, x, a).astype(np.float32)
        return a

gap_chunk, gap_step = np.zeros(int(0.30 * SR), np.float32), np.zeros(int(0.10 * SR), np.float32)
import os
REDO = set(filter(None, os.environ.get('REDO', '').split(',')))
timing = json.load(open(OUT / f'{vid}.json')) if (OUT / f'{vid}.json').exists() else {}
by_slide = {}
for k, v in N.items():
    sid, st = k.rsplit('#', 1); by_slide.setdefault(sid, []).append((int(st), v))
for sid, steps in by_slide.items():
    redo = [st for st, _ in steps if f'{sid}#{st}' in REDO]
    if sid in timing and not redo: continue   # resumable; REDO re-renders listed steps only
    T = dict(timing.get(sid, {})) if redo else {}
    for st, text in sorted(steps):
        if redo and st not in redo and str(st) in T: continue
        parts, t, rows = [np.zeros(int(0.05 * SR), np.float32)], 0.05, []
        for c in chunks(text):
            a = synth(spoken(c)); a = a / max(1e-6, np.abs(a).max()) * 0.89
            rows.append([round(t, 3), round(t + len(a) / SR, 3), c]); parts += [a, gap_chunk]; t += (len(a) + len(gap_chunk)) / SR
        wav = OUT / vid / f'{sid}__{st}.wav'; sf.write(wav, np.concatenate(parts), SR)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-ac', '1', '-codec:a', 'libmp3lame', '-b:a', '48k', str(OUT / vid / f'{sid}__{st}.mp3')], check=True); wav.unlink()
        T[str(st)] = rows
    timing[sid] = T; json.dump(timing, open(OUT / f'{vid}.json', 'w'), ensure_ascii=False)
    print(sid, round(sum(r[-1][1] for r in T.values()), 1), 's', flush=True)
print('done', vid)
