/* Recorded narration with text-version checks and cancellable device-TTS fallback. */
(function (root) {
  'use strict';
  class LessonNarration {
    constructor(lessonId, options = {}) {
      this.lessonId = lessonId;
      this.seq = 0;
      this.audio = null;
      this.timer = null;
      this.manifest = options.manifest || fetch(new URL('audio/manifest.json', document.baseURI), {cache:'no-cache'})
        .then(r => r.ok ? r.json() : {}).catch(() => ({}));
      // Review hold (tools/audio/mkhold.py): {lesson: {sid: issueId}} — a missing file means nothing is held.
      this.hold = options.hold || fetch(new URL('audio/hold.json', document.baseURI), {cache:'no-cache'})
        .then(r => r.ok ? r.json() : {}).catch(() => ({}));
      this.holdDelay = options.holdDelay ?? 3500;
    }
    async heldIssue(sid) { const h = await this.hold; return h?.[this.lessonId]?.[sid] || null; }
    stop() {
      this.seq++;
      clearTimeout(this.timer);
      if (this.audio) { this.audio.onended = this.audio.onerror = null; this.audio.pause(); this.audio.removeAttribute('src'); this.audio.load(); this.audio.remove(); this.audio = null; }
      if (root.speechSynthesis) root.speechSynthesis.cancel();
    }
    setRate(rate) { if (this.audio) this.audio.playbackRate = rate; }
    async play({sid, text, spokenText, rate = 1, auto = false, onend, onblocked, onstatus}) {
      this.stop();
      const token = this.seq;
      const alive = () => token === this.seq;
      const [manifest, held] = await Promise.all([this.manifest, this.heldIssue(sid)]);
      if (!alive()) return;
      // A held stop is never read on its own; stepping to it by hand reads it with the device voice only.
      if (held) {
        if (auto) { onstatus('검수 보류 — 내용 확인 중'); this.timer = setTimeout(() => { if (alive()) onend(); }, this.holdDelay); return; }
        return device('기기 음성 · 검수 보류');
      }
      const entry = manifest.lessons?.[this.lessonId]?.[sid];
      // An edited script must never silently play an old recording.
      if (entry?.status === 'ready' && entry.text === text && entry.src) {
        let url;
        try { url = new URL(entry.src, document.baseURI); if (!['http:', 'https:'].includes(url.protocol)) throw new Error('protocol'); }
        catch (_) { return device(); }
        const audio = new Audio(url.href);
        this.audio = audio; audio.hidden = true; document.body.appendChild(audio); audio.preload = 'auto'; audio.playbackRate = rate;
        let settled = false;
        const fallback = () => { if (!alive() || settled) return; settled = true; audio.pause(); audio.onended = audio.onerror = null; clearTimeout(this.timer); audio.remove(); this.audio = null; device(); };
        audio.onended = () => { if (!alive() || settled) return; settled = true; clearTimeout(this.timer); onend(); };
        audio.onerror = fallback;
        onstatus('Gemini 녹음');
        this.timer = setTimeout(fallback, 12000);
        try { await audio.play(); if (alive()) clearTimeout(this.timer); }
        catch (error) {
          if (!alive() || settled) return;
          if (error.name === 'NotAllowedError') { settled = true; clearTimeout(this.timer); onblocked(); }
          else fallback();
        }
        return;
      }
      return device();
      function device(label = '기기 음성') {
        // Use the owning instance; invoked only after asynchronous manifest resolution.
        if (!alive()) return;
        onstatus(label);
        if (!root.speechSynthesis || !root.SpeechSynthesisUtterance) { onblocked(); return; }
        const u = new root.SpeechSynthesisUtterance(spokenText || text);
        u.lang = 'ko-KR'; u.rate = rate;
        const voice = root.speechSynthesis.getVoices().find(v => /^ko/i.test(v.lang));
        if (voice) u.voice = voice;
        let started = false;
        u.onstart = () => { started = true; };
        u.onend = () => { if (alive() && started) onend(); };
        u.onerror = () => { if (alive()) onblocked(); };
        root.speechSynthesis.speak(u);
        setTimeout(() => { if (alive() && !started) { root.speechSynthesis.cancel(); onblocked(); } }, 3000);
      }
    }
  }
  root.LessonNarration = LessonNarration;
})(window);
