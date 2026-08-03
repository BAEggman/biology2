/* ═══════════════════════════════════════════════════════════════════
   _terms.js — 한국어 용어 매칭 공용부 (rank.js · orphan.js 공유)

   왜 따로 뺐나: rank.js는 「카드 → 그림」, orphan.js는 「그림 → 카드」로
   방향이 반대인데 매칭 규칙은 같아야 한다. 복사해 두면 반드시 갈라진다.
   ═══════════════════════════════════════════════════════════════════ */

/* 한국어라 토큰 비교가 안 된다 — 「전자전달계의」는 「전자전달계」와 다른 말로 잡힌다.
   그래서 사실표에서 용어 사전을 만들고 카드 본문에 그 용어가 있는지를 본다(부분일치).
   방향이 사실표 → 카드라 조사·어미가 붙어도 걸린다. */
const STRIP=/(으로써|으로서|에게서|이라는|라는|에서|에게|한테|처럼|같이|부터|까지|보다|으로|이나|이란|과의|와의|의|은|는|이|가|을|를|와|과|도|만|로|에|랑|나)$/;

function terms(t){
  const out=new Set();
  for(const w of String(t).match(/[가-힣]{2,}/g)||[]){
    out.add(w); const b=w.replace(STRIP,''); if(b.length>=2) out.add(b);
  }
  for(const w of String(t).match(/[A-Za-z][A-Za-z0-9₀-₉\-]{1,}/g)||[]) out.add(w);
  return out;
}

/* 사실표에 흔한 빈 말 — 소품 서술이 위치·수량·모양으로 되어 있어 이런 말이 많다.
   DF만으로는 안 걸러진다. 106패널 중 2~3곳에만 나오면 오히려 높은 가중을 받는다. */
const STOP=new Set(('마지막 처음 하나 둘 셋 넷 다섯 여섯 사람 사람이 인부 작업 오른쪽 왼쪽 가운데 '
 +'아래 위쪽 아래쪽 바깥 안쪽 모양 같은 다른 전부 각각 여럿 자리 방향 크기 색깔 그대로 '
 +'되는 하는 하고 있는 없는 만든 들고 나가는 들어 이것 저것 경우 상태 부분 전체 통째로 '
 +'개씩 개가 개를 번째 쪽으로 위에 밑에 옆에 안에 밖에 그림 표시 이름 서로 함께 다시 '
 +'무엇 에서 에게 으로 이나 하나씩 무슨 어떤 어느 얼마 언제 그것').split(' '));

const chNum = s => (String(s||'').match(/^[\d·]+/)||[''])[0].split('·').filter(Boolean);

const strip = t => String(t||'').replace(/<[^>]*>/g,' ');

/* sketchy.html의 DATA를 괄호 균형으로 잘라 평가한다.
   `const DATA` 를 그대로 eval하면 재선언 에러가 난다. */
function parseDATA(sk){
  const st=sk.indexOf('[', sk.indexOf('const DATA'));
  let d=0,q=null,esc=false;
  for(let k=st;k<sk.length;k++){ const ch=sk[k];
    if(q){ if(esc){esc=false;continue} if(ch==='\\'){esc=true;continue} if(ch===q)q=null; continue }
    if(ch==='"'||ch==="'"||ch==='`'){ q=ch; continue }
    if(ch==='[')d++; else if(ch===']'){ d--; if(!d) return eval('('+sk.slice(st,k+1)+')'); } }
  throw new Error('DATA 괄호가 안 맞는다');
}

module.exports={STRIP, terms, STOP, chNum, strip, parseDATA};
