(async()=>{const {PRE,KS,EXCL,EXTRA,v,zip,TITLE}=window.G;
const J=JSON.parse(localStorage.b2tts2);const D=JSON.parse(localStorage.b2dict2||'{}');
const ks=Object.keys(J).filter(k=>(PRE.some(p=>k.startsWith(p+'_')))||(KS||[]).includes(k)).filter(k=>!(EXCL||[]).includes(k));const N=ks.length;
const dict=[...new Set(ks.flatMap(k=>D[k.split('_')[0]]||[]))].concat(EXTRA||[]);
let p=`Gemini TTS를 사용해 아래 한국어 그림 해설 ${N}개를 실제 낭독 음성 파일로 생성해 줘.\n\n텍스트 답변, API 코드, 만드는 방법 설명이 아니라 재생·다운로드 가능한 WAV 파일이 필요해.\n\n문단 하나에 파일 하나씩, 모두 ${N}개 파일을 만들고 ZIP 하나로 묶어 줘. ZIP 파일명은 ${zip}.zip 으로 해 줘. 파일명은 각 문단 머리의 이름을 그대로 써.\n\n한 명의 자연스럽고 또렷한 한국어 목소리(Kore)로, ${N}개 모두 같은 목소리와 같은 속도로 읽어 줘.\n\n차분하지만 생동감 있게, 그림 속 물건과 사건을 함께 살펴보는 말투로 읽어 줘.\n\n속도는 보통으로 하고, 전문용어는 한 음절씩 또렷하게 읽어 줘.\n\n배경음악, 효과음, 인사, 제목 낭독, 파일명 낭독, 마무리 멘트는 넣지 마.\n\n아래 대본은 검증하고 확정한 반말 서술체야.\n\n존댓말로 바꾸거나 요약·첨삭·보충·생략·문장 순서 변경을 하지 마.\n\n각 파일에는 해당 <대본> 안의 문장만 처음부터 끝까지 읽어 줘.\n\n알파벳 약어는 대본에 이미 한글 소리로 풀어 적었으니 적힌 소리 그대로 읽어 줘.\n\n`+(dict.length?`전문용어의 지정 발음은 아래 사전을 따르되, 사전 자체는 읽지 마.\n\n<발음 사전>\n\n${dict.join('\n\n')}\n\n</발음 사전>\n\n`:'')+`파일을 만들 수 없다면 만들었다고 말하지 말고 실제 제한을 알려 줘.\n\n`;
for(const k of ks) p+=`[biology_${k}_${v}.wav]\n\n<대본>\n\n${J[k].t}\n\n</대본>\n\n`; p=p.trim();
const ed=document.querySelector("rich-textarea .ql-editor");ed.focus();document.execCommand("selectAll");document.execCommand("insertText",false,p);
await new Promise(r=>setTimeout(r,1000));
const sha=async s=>[...new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s)))].map(b=>b.toString(16).padStart(2,"0")).join("");
const txt=ed.innerText;const re=/\[biology_(L\w+?_s\d+)_v\d+\.wav\]\s*<대본>\s*([\s\S]*?)\s*<\/대본>/g;let m,out=[];while((m=re.exec(txt))){out.push(m[1]+((await sha(m[2].trim()))===J[m[1]].h?" ok":" BAD"));}
const mode=document.querySelector('[aria-pressed=true], .selected')?.innerText;const b=document.querySelector('button[aria-label="메시지 보내기"]');
if(out.length===N&&out.every(x=>x.endsWith(' ok'))&&mode==='태스크'&&b){b.click();setInterval(()=>{if(document.title.length>20)document.title=TITLE},500);return 'sent '+N}else return ['NOT SENT',N,out,mode,!!b]
})()