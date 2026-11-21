// mktts.js <L>... — 잠긴 구간의 낭독 입력 {L_sid:{t,h}} (ttsNorm(say, 사전, 과 차례, 과) — 사전 · 차례를 빼면 영어가 글자 이름으로 읽히고 과 번호가 남는다)
const fs=require('fs'),crypto=require('crypto'),path=require('path');const R=path.join(__dirname,'..','..','..');
const {ttsNorm}=require(R+'/tools/tts_norm.js');const lex=JSON.parse(fs.readFileSync(R+'/tools/tts_lexicon.json','utf8'));const order=require(R+'/tools/tts_order')();
const lk=JSON.parse(fs.readFileSync(R+'/tools/audio/locked.json')).잠김;
const out={};
for(const L of process.argv.slice(2)){const d=JSON.parse(fs.readFileSync(`${R}/lessons/${L}.json`));for(const s of d.stops){if(!lk[L]||!lk[L].구간[s.sid])continue;const t=ttsNorm(s.say,lex,order,L);out[`${L}_${s.sid}`]={t,h:crypto.createHash('sha256').update(t).digest('hex')};}}
fs.writeFileSync(process.env.OUT||'/mnt/user-data/outputs/b2_tts.json',JSON.stringify(out));console.log(Object.keys(out).length);
