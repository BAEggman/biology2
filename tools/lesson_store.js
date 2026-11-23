/* lesson_store.js — 과 목록 · 과 화면이 함께 쓰는 저장 도우미(보기 화면 명세 §1.1).
   빌드(build_lesson.js)가 두 화면에 그대로 끼워 넣는다(__STORE__) — 열쇠 이름 · 꼴이 한 군데서만 정해진다.
   열쇠: lesson_stars {ID: 찍은 때(ms)} · lesson_prefs {onlyStar, autoNext, rep, scope} · lesson_ab_<ID> {a: sid, b: sid}
   읽기 · 쓰기는 모두 try/catch — 저장이 막힌 브라우저에서는 그 쪽을 떠날 때까지만 기억하고 오류를 내지 않는다.
   (lesson_<ID> · lesson_shuffle · lesson_srs_inbox · lesson_auto_start 는 여기서 건드리지 않는다) */
const LStore = (() => {
  const mem = {};
  const rd = (k, d) => {
    let ok = false;
    try { const v = localStorage.getItem(k); ok = true; if (v !== null && v !== undefined) { const o = JSON.parse(v); mem[k] = o; return o; } } catch (e) {}
    if (ok) { delete mem[k]; return d; }   // 저장소는 멀쩡한데 값이 없다 = 다른 탭에서 지웠다 — 메모리 값도 버린다
    return k in mem ? mem[k] : d;
  };
  const wr = (k, o) => { mem[k] = o; try { localStorage.setItem(k, JSON.stringify(o)); } catch (e) {} };
  const del = k => { delete mem[k]; try { localStorage.removeItem(k); } catch (e) {} };
  const isObj = o => o && typeof o === 'object' && !Array.isArray(o);
  const REP = ['off', 'ab', 'one', 'list'];
  return {
    stars() { const s = rd('lesson_stars', {}); return isObj(s) ? s : {}; },
    isStar(id) { return id in LStore.stars(); },
    setStar(id, on) {
      const s = { ...LStore.stars() };
      if (on) s[id] = Date.now(); else delete s[id];
      if (Object.keys(s).length) wr('lesson_stars', s); else del('lesson_stars');
      return on;
    },
    prefs() {
      const p = rd('lesson_prefs', {}); const o = isObj(p) ? p : {};
      return { onlyStar: !!o.onlyStar, autoNext: !!o.autoNext, rep: REP.includes(o.rep) ? o.rep : 'off', scope: o.scope === 'star' ? 'star' : 'all' };
    },
    setPrefs(patch) { const p = { ...LStore.prefs(), ...patch }; wr('lesson_prefs', p); return p; },
    ab(id) { const v = rd('lesson_ab_' + id, null); return isObj(v) ? { a: typeof v.a === 'string' ? v.a : null, b: typeof v.b === 'string' ? v.b : null } : { a: null, b: null }; },
    setAb(id, v) { const k = 'lesson_ab_' + id; if (v && (v.a || v.b)) wr(k, { a: v.a || null, b: v.b || null }); else del(k); },
    REP,
  };
})();
