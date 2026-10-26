// ---------------------------------------------------------------- presentation engine: stage, steps, narration, player
export const $ = (s, el = document) => el.querySelector(s);
export const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
export const sleep = ms => new Promise(r => setTimeout(r, ms));
export function h(tag, attrs = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (k === 'class') e.className = v; else if (k === 'style' && typeof v === 'object') Object.assign(e.style, v);
    else if (k === 'html') e.innerHTML = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else if (v != null && v !== false) e.setAttribute(k, v);
  }
  for (const k of kids.flat()) if (k != null && k !== false) e.append(k.nodeType ? k : document.createTextNode(k));
  return e;
}

// ---------------------------------------------------------------- narrator (Web Speech API, with a timed fallback)
export class Narrator {
  constructor() {
    this.synth = window.speechSynthesis || null; this.voice = null; this.rate = 1.0; this.muted = false; this.voices = [];
    this.onSentence = () => {}; this._gen = 0;
    const load = () => {
      if (!this.synth) return; const all = this.synth.getVoices(); if (!all.length) return;
      const en = all.filter(v => /^en/i.test(v.lang));
      const score = v => (/natural|neural|premium|enhanced/i.test(v.name) ? 40 : 0) + (/google|microsoft|samantha|daniel|serena|ava|allison|aria|guy|jenny|libby|ryan/i.test(v.name) ? 15 : 0) + (/en-(GB|US|CA|AU)/i.test(v.lang) ? 5 : 0) - (v.localService ? 0 : 2);
      this.voices = (en.length ? en : all).sort((a, b) => score(b) - score(a));
      if (!this.voice) { let saved = null; try { saved = localStorage.getItem('tec-voice'); } catch (e) {} this.voice = this.voices.find(v => v.name === saved) || this.voices[0]; }
      this.onVoices && this.onVoices(this.voices);
    };
    if (this.synth) { load(); this.synth.addEventListener?.('voiceschanged', load); setTimeout(load, 600); setTimeout(load, 2000); }
  }
  setVoice(name) { this.voice = this.voices.find(v => v.name === name) || this.voice; try { localStorage.setItem('tec-voice', name); } catch (e) {} }
  estimate(text) { const w = text.split(/\s+/).filter(Boolean).length; return (w / 2.55 / this.rate) * 1000 + 350; }
  sentences(text) { return text.replace(/\s+/g, ' ').trim().split(/(?<=[.!?;])\s+(?=[A-Z0-9“"(‘'])/).map(s => s.trim()).filter(Boolean); }
  cancel() { this._gen++; if (this.synth) this.synth.cancel(); }
  // speak a block; resolves when finished or cancelled; signal.cancelled says which
  async speak(text) {
    const gen = ++this._gen; const parts = this.sentences(this.say(text));
    for (const s of parts) {
      if (gen !== this._gen) return false;
      this.onSentence(s);
      if (this.muted || !this.synth || !this.voice) { await this._wait(this.estimate(s), gen); continue; }
      const ok = await new Promise(res => {
        const u = new SpeechSynthesisUtterance(s); u.voice = this.voice; u.lang = this.voice.lang; u.rate = this.rate; u.pitch = 1;
        let done = false; const fin = v => { if (!done) { done = true; clearTimeout(guard); res(v); } };
        u.onend = () => fin(true); u.onerror = () => fin(true);
        const guard = setTimeout(() => fin(true), this.estimate(s) * 2.2 + 4000);   // never hang on a lost 'end' event
        this.synth.speak(u);
      });
      if (!ok || gen !== this._gen) return false;
    }
    this.onSentence('');
    return gen === this._gen;
  }
  _wait(ms, gen) { return new Promise(r => { const t0 = performance.now(); const tick = () => { if (gen !== this._gen) return r(); if (performance.now() - t0 >= ms) return r(); setTimeout(tick, 60); }; tick(); }); }
  // pronunciation fixes for the speech engine only (captions keep the written form)
  say(t) {
    return t.replace(/TEC-(\d+)/g, 'tech $1').replace(/\bmSS\b/g, 'metres subsea').replace(/\bmMD\b/g, 'metres measured depth')
      .replace(/(\d)\s?bbl\/d/g, '$1 barrels a day').replace(/\bbbl\b/g, 'barrels').replace(/\bkbbl\b/g, 'thousand barrels').replace(/\bMMbbl\b/g, 'million barrels')
      .replace(/USD\s?([\d.,]+)\s?MM\b/g, '$1 million dollars').replace(/USD\s?([\d.,]+)\s?k\b/g, '$1 thousand dollars').replace(/\bUSD\b/g, 'US dollars')
      .replace(/kg\/cm²/g, 'kilograms per square centimetre').replace(/\bpsi\b/g, 'p s i').replace(/°API/g, ' degrees A P I').replace(/(\d)\s?%/g, '$1 percent')
      .replace(/\bNPV10\b/g, 'N P V ten').replace(/\bGOR\b/g, 'G O R').replace(/\bPVT\b/g, 'P V T').replace(/\bPSTM\b/g, 'P S T M').replace(/\bPSDM\b/g, 'P S D M')
      .replace(/\bCNH\b/g, 'C N H').replace(/\bGLJ\b/g, 'G L J').replace(/\bAFE\b/g, 'A F E').replace(/\bWTI\b/g, 'W T I').replace(/\bOOIP\b/g, 'original oil in place')
      .replace(/\bPEMEX\b/g, 'Pemex').replace(/\bIRR\b/g, 'I R R').replace(/–/g, ' to ').replace(/−/g, 'minus ').replace(/×/g, ' times ').replace(/≈/g, 'about ');
  }
}

// ---------------------------------------------------------------- player
// slide = { id, section, title, kind: 'html'|'3d', build(el, ctx) -> steps[] }, step = { say, run(fast) }
export class Player {
  constructor({ stage, slideLayer, glLayer, slides, ctx, ui }) {
    Object.assign(this, { stage, slideLayer, glLayer, slides, ctx, ui });
    this.si = 0; this.step = -1; this.playing = false; this.steps = []; this.runGen = 0; this.autoAdvance = true;
  }
  async go(si, step = 0, { play = this.playing } = {}) {
    const gen = ++this.runGen; this.ctx.narrator.cancel();
    si = Math.max(0, Math.min(this.slides.length - 1, si)); this.si = si;
    const slide = this.slides[si];
    this.slideLayer.innerHTML = ''; this.slideLayer.className = 'slide-layer kind-' + (slide.kind || 'html') + ' ' + (slide.theme || '');
    const el = h('section', { class: 'slide ' + (slide.cls || ''), 'data-id': slide.id }); this.slideLayer.append(el);
    this.ctx.field.paused = slide.kind !== '3d';   // the 3-D canvas stays mounted; plain slides cover it and rendering pauses
    this.ctx.slide = slide; this.ctx.fast = false;
    this.steps = (await slide.build(el, this.ctx)) || [{ say: '' }];
    if (gen !== this.runGen) return;
    $$('.pg', el).forEach(p => p.textContent = si + 1);
    this.ui.onSlide(si, slide);
    step = Math.max(0, Math.min(this.steps.length - 1, step));
    for (let k = 0; k < step; k++) await this._apply(k, true);       // fast-forward earlier steps without narration
    this.step = step - 1;
    if (play) this.play(); else { await this._apply(step, false); this.step = step; this.ui.onStep(this); }
  }
  async _apply(k, fast) {
    const st = this.steps[k]; if (!st) return; this.ctx.fast = fast;
    $$(`[data-step]`, this.slideLayer).forEach(e => { const n = +e.dataset.step; if (n <= k) e.classList.add('on'); if (fast && n <= k) e.classList.add('instant'); });
    if (st.run) await st.run(fast);
  }
  async play() {
    if (this.playing && this._loop) return; this.playing = true; this.ui.onPlay(true);
    const gen = this.runGen;
    this._loop = (async () => {
      while (this.playing && gen === this.runGen) {
        const k = this.step + 1;
        if (k >= this.steps.length) {
          if (!this.autoAdvance || this.si >= this.slides.length - 1) { this.pause(); break; }
          await sleep(500); if (!this.playing || gen !== this.runGen) break;
          this._loop = null; this.go(this.si + 1, 0, { play: true }); return;
        }
        this.step = k; this.ui.onStep(this);
        const st = this.steps[k]; const say = st.say || '';
        const dur = say ? this.ctx.narrator.estimate(say) : (st.hold || 1200);
        this.ctx.stepDuration = dur;
        const runP = this._apply(k, false);
        const ok = say ? await this.ctx.narrator.speak(say) : (await sleep(st.hold || 1200), true);
        await runP;
        if (!ok || gen !== this.runGen || !this.playing) break;
        await sleep(st.pause ?? 380);
      }
      this._loop = null;
    })();
  }
  pause() { this.playing = false; this.ctx.narrator.cancel(); this.ui.onPlay(false); }
  toggle() { this.playing ? this.pause() : (this.step >= this.steps.length - 1 && this.si < this.slides.length - 1 ? this.go(this.si + 1, 0, { play: true }) : this.play()); }
  async next() {
    const was = this.playing; this.pause();
    if (this.step < this.steps.length - 1) { this.step++; await this._apply(this.step, false); this.ui.onStep(this); if (was) this.play(); }
    else if (this.si < this.slides.length - 1) this.go(this.si + 1, 0, { play: was });
  }
  async prev() {
    const was = this.playing; this.pause();
    if (this.step > 0) this.go(this.si, this.step - 1, { play: was }); else if (this.si > 0) { this.go(this.si - 1, 999, { play: false }); }
  }
}

// count-up numbers: <span data-count="1936255" data-fmt="0,0">
export function countUp(el, fast) {
  $$('[data-count]', el).forEach(n => {
    const to = +n.dataset.count, dec = +(n.dataset.dec || 0), pre = n.dataset.pre || '', suf = n.dataset.suf || '';
    const f = v => pre + v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf;
    if (fast) { n.textContent = f(to); return; }
    const t0 = performance.now(), D = 1400; const tick = () => { const p = Math.min(1, (performance.now() - t0) / D), e = 1 - Math.pow(1 - p, 3); n.textContent = f(to * e); if (p < 1) requestAnimationFrame(tick); }; tick();
  });
}
