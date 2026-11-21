const fs=require('fs'),crypto=require('crypto');const {ttsNorm}=require('/tmp/b2/tools/tts_norm.js');
const lk=JSON.parse(fs.readFileSync('/tmp/b2/tools/audio/locked.json')).잠김;
const Ls=process.argv.slice(2);const out={};
for(const L of Ls){const d=JSON.parse(fs.readFileSync(`/tmp/b2/lessons/${L}.json`));for(const s of d.stops){if(!lk[L]||!lk[L].구간[s.sid])continue;const t=ttsNorm(s.say);out[`${L}_${s.sid}`]={t,h:crypto.createHash('sha256').update(t).digest('hex')};}}
fs.writeFileSync(process.env.OUT||'/mnt/user-data/outputs/b2_tts.json',JSON.stringify(out));console.log(Object.keys(out).length);
