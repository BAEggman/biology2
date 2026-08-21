/* 복구 화면의 실제 코드(showPicFix)를 index.html 에서 떼어다 그대로 돌린다 */
const fs=require('fs');
const html=fs.readFileSync('/tmp/b2/index.html','utf8');
const g=n=>{const m=html.match(new RegExp('var '+n+'=(\\{[\\s\\S]*?\\}|\\[[\\s\\S]*?\\]);var '));return m?JSON.parse(m[1]):null;};
const blk=html.match(/\/\*BUILD:START[\s\S]*?BUILD:END\*\//)[0];
const env=new Function(blk.replace(/\/\*BUILD:(START|END)[^*]*\*\//g,'')
  +'; return {PMAP,PROW,PTIT,PBR,PFACT,PNOIMG,PSVG};')();
// showPicFix 원본을 떼어 온다
const i=html.indexOf('function showPicFix');
let d=0,j=html.indexOf('{',i);const s0=j;
for(;j<html.length;j++){ if(html[j]==='{')d++; else if(html[j]==='}'){d--; if(!d){j++;break;}} }
const src=html.slice(i,j);
// 최소 환경
const box={innerHTML:'',classList:{remove(){},add(){}},scrollIntoView(){}};
const stub={grades:{classList:{add(){},remove(){}}},picLink:{classList:{add(){},remove(){}}},
            pfNext:{},picFix:box};
const ctx={ $:id=>id==='picFix'?box:(stub[id]||{classList:{add(){},remove(){}}}),
  esc:x=>String(x), rich:x=>String(x), advance(){},
  PMAP:env.PMAP,PROW:env.PROW,PTIT:env.PTIT,PBR:env.PBR,PFACT:env.PFACT,
  PNOIMG:env.PNOIMG,PSVG:env.PSVG,
  pidList:v=>!v?[]:(Array.isArray(v)?v:[v]) };
const fn=new Function('C','with(C){'+src+'; return showPicFix;}')(ctx);
Object.defineProperty(ctx,'picFixOn',{value:false,writable:true});

const NO=new Set(env.PNOIMG); let done=0;
for(const cid of Object.keys(env.PMAP)){
  const ps=ctx.pidList(env.PMAP[cid]);
  if(!ps.every(p=>NO.has(p))) continue;
  box.innerHTML=''; fn(cid);
  const out=box.innerHTML;
  const hasSvg=/<div class="pfsvg"><svg /.test(out);
  const hasImg=/img class="pfimg"/.test(out);
  const nText=(out.match(/<text/g)||[]).length;
  console.log((hasSvg?'✓':'✗')+' '+cid.padEnd(9)+'→ '+ps.join('|').padEnd(9)
    +' SVG '+(hasSvg?'있음':'없음')+' · webp '+(hasImg?'있음(문제)':'없음')
    +' · <text> '+nText+'개'+(/멘델/.test(out)?' · 「멘델」 포함':''));
  if(++done>=6) break;
}
