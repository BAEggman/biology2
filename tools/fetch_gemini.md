# Gemini 그림 회수 — 사용자 손을 안 빌리는 절차 (2026-08-20)

# ★★★ 2026-08-25 — 좌표 대신 **JS 이벤트 열 개**를 쏘면 다 된다

지난 세션들이 「모드 선택 메뉴가 안 열린다」 「송신 버튼이 안 먹는다」로 막혔던 것이
한 가지 원인이었다. **Angular Material 은 hover 계열 이벤트가 먼저 오지 않으면 클릭을 무시한다.**
`computer left_click` 은 좌표만 보내고, 스크린샷 좌표와 페이지 좌표가 어긋나 있어 더 안 맞았다.

**되는 방법 — 요소를 DOM 에서 찾아 이벤트를 순서대로 쏜다.**

    const b=[...document.querySelectorAll('button')]
      .find(x=>/모드 선택 도구/.test(x.getAttribute('aria-label')||''));   // 또는 /메시지 보내기/
    const r=b.getBoundingClientRect(), cx=r.x+r.width/2, cy=r.y+r.height/2;
    for(const t of ['pointerover','pointerenter','mouseover','pointermove','mousemove',
                    'pointerdown','mousedown','pointerup','mouseup','click'])
      b.dispatchEvent(new MouseEvent(t,{bubbles:true,cancelable:true,composed:true,
                                        clientX:cx,clientY:cy,button:0,
                                        buttons:t.includes('down')?1:0}));

앞의 다섯(hover 계열)이 핵심이다. `click` 만 쏘면 안 먹는다.
이 방법으로 **모드 메뉴 열기 · 메뉴 항목 고르기 · 메시지 보내기**가 전부 됐다.

## 모델 고르기 (2026-08-25 UI)

컴포저 오른쪽의 알약 버튼 `aria-label="모드 선택 도구 열기, 현재 ○○ 모드 사용 중"`.
위 방법으로 열면 메뉴에 네 줄이 뜬다 — `3.5 Flash-Lite` · `3.7 Flash` · `3.1 Pro` · `확장된 사고 모델`.
`[role="menuitem"]` 로 잡아 같은 이벤트 열 개를 쏘면 골라진다.
고른 뒤 알약이 「Pro」로 바뀌는 것으로 확인한다.

⚠ **대화 안에서는 이 알약이 안 보인다.** 새 채팅 화면에서만 뜬다 —
모델은 대화를 시작할 때 정해지고 그 대화 내내 유지된다.

## ★ 내려받기는 **탭 하나에 한 번**이 맞다 (재확정)

2026-08-21 에 「대화가 무거워서였다」로 정정했었는데, 2026-08-25 에 그림 3장짜리 가벼운
대화에서도 똑같이 걸렸다. **같은 탭에서 두 번째 클릭은 조용히 무시된다** — 오류도 안 난다.
대화 URL 로 `navigate` 해서 새로고침해도 **안 풀린다.**

  ★ 규칙 — **그림 하나에 새 탭 하나.** `tabs_create_mcp` → 대화 URL 로 이동 →
    10초 대기 → `computer scroll` 아래로 → 6초 대기 → 다운로드 버튼 클릭.

  ★★ 그런데 새 탭에서도 `b.click()` 이 조용히 무시될 때가 있다.
    **위의 이벤트 열 개를 쏘면 그때 떨어진다.** 즉 다운로드 버튼도 다른 버튼과 같다 —
    hover 계열이 먼저 와야 한다. 새 탭 + 이벤트 열 개, 이 둘을 같이 쓴다.
    (JS `scrollTop` 만으로는 지연 로딩이 안 풀릴 때가 있어 실제로 굴려야 한다.)

## 파일 회수 경로 (2026-08-25 확인)

    device_bash:  ls -t "$HOME/mnt/Downloads"/Gemini_Generated_Image_*.png | head -1
    device_stage_files: paths=["/Users/mac/Downloads/<이름>"]   ← ★ 기기 경로로 준다
      ⚠ device_bash 가 찍어 주는 /sessions/... 경로를 그대로 주면 거부된다
      ("is not inside a folder connected to Cowork"). 연결된 폴더는 /Users/mac/Downloads 다.
    → /mnt/user-data/uploads/Downloads/<이름>  (2048×2048 PNG)



전체 설명은 프로젝트 문서 `claude/생물Sketchy_Gemini자동화_해결.md`에 있다.
여기는 명령만 적어 둔다.

## ⓪ 어느 대화에 보내는가 (2026-08-21 신설)

**지금 쓰는 대화** — `https://gemini.google.com/app/bea759ffdafa7418`
(옛 대화 `45be42d49b3a8149` 는 그림이 12장 쌓여 **렌더러가 얼어붙었다**. 더 쓰지 않는다.)

### ★ 그림 열 장쯤 되면 대화를 새로 판다

대화가 무거워지면 이런 증상이 순서대로 나온다 —
`computer screenshot` 이 `Script injection timed out`,
그다음 `javascript_tool` 이 `CDP Runtime.evaluate timed out`,
끝내 확장 자체가 `did not respond in time`.
탭을 새로 열어도 같은 대화면 똑같이 얼어붙는다. **대화를 바꿔야 풀린다.**

새로 파는 법 — `https://gemini.google.com/app` 으로 이동해 바로 프롬프트를 보낸다.
보내고 나면 URL 이 `/app/<새 id>` 로 바뀐다. 그 id 를 여기 적어 둔다.

⚠ 보낸 직후 화면은 **아직 입력창에 글이 남은 것처럼 보인다.** 속지 말 것 —
`대답 생성 중지` 버튼이 있고 URL 에 id 가 붙었으면 보내진 것이다.

⚠ 새 대화에서도 **모델이 Pro 인지** 확인한다
(`aria-label` 에 「현재 Pro 모드 사용 중」이 있으면 맞다).

## ★ 보낼 때마다 새 탭 (2026-08-21 확정)

한 탭에서 그림이 한 번 나오고 나면 **송신 버튼이 「대답 생성 중지」로 굳는다.**
그 탭에서는 다시 보낼 수 없다 — 중지를 눌러도 안 풀린다. 그림은 멀쩡히 나와 있는데
페이지 상태만 안 풀리는 것이다.

  ★ 그래서 **프롬프트 하나에 새 탭 하나**로 굳힌다. 새 탭에서 대화 URL 로 이동하면
    송신 버튼(`aria-label="메시지 보내기"`)이 정상으로 돌아온다.

  ⚠ 보낸 뒤 확인은 **입력창이 비었는가**로 한다 — `innerText.length` 가 1이면 나간 것이다.
    「대답 생성 중지」 버튼의 유무로 판단하면 안 된다(앞 생성의 잔상일 수 있다).

## ① 다운로드 버튼을 누른다 (Chrome, javascript_tool)

    const im=[...document.querySelectorAll('img')].filter(i=>i.naturalWidth>400).pop();
    const host=im.closest('single-image');
    const b=[...host.querySelectorAll('button')].find(x=>(x.getAttribute('aria-label')||'').includes('다운로드'));
    if(b) b.click(); b?'clicked':'none'

## ② 최신 파일 이름을 얻는다 (device_bash)

    ls -t "$HOME/mnt/Downloads"/Gemini_Generated_Image_*.png | head -1

⚠ device_list_dir 는 쓰지 말 것 — 이 Downloads 는 파일이 수백 개라 한 번에 2만 토큰이 든다.

## ③ 컨테이너로 올린다 (device_stage_files)

    paths: ["/Users/mac/Downloads/<위에서 얻은 이름>"]
    → /mnt/user-data/uploads/Downloads/<이름>

## ④ 설치한다

    python3 - <<'PY'
    from PIL import Image
    SRC='/mnt/user-data/uploads/Downloads/<이름>'
    PID='s00p00'
    im=Image.open(SRC).convert('RGBA')
    bg=Image.new('RGBA',im.size,(247,241,224,255)); bg.alpha_composite(im); im=bg.convert('RGB')
    w=1024; h=round(im.height*w/im.width)
    im.resize((w,h), Image.LANCZOS).save('img/%s.webp'%PID,'WEBP',quality=92,method=6)
    PY

## 권한

세션마다 한 번 `device_request_folder_access(["~/Downloads"])` 를 받아야 한다.
2026-08-20 세션에서 `/Users/mac/Downloads` 로 허용받았다. 기기는 m1-local (macOS arm64).

---

# ★ 기존 그림을 Gemini에 올려 편집하기 (2026-08-20 신설)

재생성은 잘 된 후크를 잃을 위험이 있다. 편집은 나머지를 안 건드린다.
그런데 옛 패널의 그림은 지금 대화에 없으므로 **올려야** 한다.

## ① 컨테이너의 그림을 세션 uploads 폴더로 옮긴다

    python3 -c "
    from PIL import Image
    Image.open('/tmp/b2/img/s19p01.webp').convert('RGB').save('/mnt/user-data/uploads/_edit_s19p01.png')"

⚠ **경로가 `/mnt/user-data/uploads/` 여야 한다.** 기기 경로(`/Users/mac/Downloads/...`)는
크롬 확장이 거부한다 — 「only files this session is allowed to read」.

## ② Gemini 컴포저의 「업로드 및 도구」 버튼을 눌러 file input 을 만든다

    find(query='파일 추가 / 이미지 업로드 플러스 버튼 (컴포저 왼쪽)')  → ref
    computer left_click ref

메뉴(파일 업로드 / Drive에서 파일 추가)가 뜨는데 **메뉴 항목은 누르지 않는다** —
누르면 네이티브 파일 선택창이 열려서 손댈 수 없다. 메뉴가 뜨는 것만으로 DOM 에
`input[type=file]` 셋이 생긴다.

## ③ 이미지용 input 을 골라 잠깐 보이게 만든다 (find 는 숨은 요소를 못 본다)

    const f=[...document.querySelectorAll('input[type=file]')];
    f.forEach((e,i)=>{ if(!e.id) e.id='__fi'+i; });
    f.map((e,i)=>i+'|'+e.id+'|img:'+/png|image/i.test(e.accept||''))
    // accept 가 image/* 인 것을 고른다 (보통 __fi1)

    const e=document.getElementById('__fi1');
    e.removeAttribute('hidden');
    e.style.cssText='position:fixed;left:20px;top:120px;width:320px;height:44px;opacity:1;z-index:99999;display:block;visibility:visible';
    e.setAttribute('aria-label','내가 노출시킨 이미지 업로드 입력');

## ④ file_upload 로 넣는다

    find(query='내가 노출시킨 이미지 업로드 입력') → ref
    mcp__claude-in-chrome__file_upload(ref, paths=['/mnt/user-data/uploads/_edit_s19p01.png'])

성공하면 **컴포저가 비어 있어도 「메시지 보내기」가 enabled** 가 된다. 그것이 붙었다는 신호다.
넣은 뒤 input 을 도로 숨긴다:

    document.getElementById('__fi1').style.cssText='position:absolute;left:-9999px;width:1px;height:1px;opacity:0';

## ⑤ 편집 프롬프트를 쓴다

    Work only from the attached picture — ignore the picture above, that one is finished.
    Redraw the attached picture keeping everything exactly as it is, and change one single thing.
    <바꿀 것 하나>
    Everything else stays identical: <바뀌면 안 되는 것을 하나하나 나열>

★ 같은 대화에 다른 그림이 있으면 **「attached picture 만 보라」를 첫 줄에 못 박는다.**

---

# ★★ 다운로드가 한 번밖에 안 먹는 문제 (2026-08-20 해결)

크롬이 한 페이지에서 **자동 다운로드를 여러 번** 하는 것을 막는다.
버튼은 멀쩡히 보이고 클릭도 먹지만 파일이 안 떨어진다.

**해결: 받기 전에 대화 URL 로 navigate 해서 새로고침한다.**
새로고침한 뒤 **첫 클릭 한 번**은 반드시 먹는다.

    navigate(대화 URL)
    → 15~25초 기다린다 (naturalWidth 가 0 이 아니게 될 때까지)
    → 다운로드 버튼 click  ← 이 한 번만 먹는다
    → device_bash 로 최신 파일 확인

그림 하나마다 새로고침 한 번이라고 생각하면 된다.

## ⚠ file input 이 안 잡힐 때

「업로드 및 도구」를 눌러 메뉴가 떠도 `input[type=file]` 이 **0개**로 나올 때가 있다.
기다려도 안 생긴다. **screenshot 을 한 번 찍으면 그때 잡힌다** — 렌더가 강제되는 듯하다.

    computer left_click (업로드 및 도구 ref)
    computer screenshot          ← 이게 있어야 한다
    javascript: input[type=file] 조회  → 3개

## ★★★ [정정] 「탭 하나당 한 번」이 아니라 **대화가 무거워서**였다 (2026-08-21)

새 대화(`bea759ffdafa7418`)에서는 **같은 탭에서 연달아 두 번** 받았다 — 둘 다 첫 시도에 됐다.
아래 2026-08-20 기록은 **옛 대화가 무거워서 생긴 증상**을 탭 문제로 잘못 읽은 것이다.

  ★ 진짜 규칙 — **대화가 무거우면 안 받아진다. 그림 열 장쯤에서 대화를 새로 판다.**
  탭을 새로 여는 것은 임시방편이었고, 대화를 바꾸면 그럴 필요가 없다.

## (옛 기록 · 2026-08-20) 탭 하나당 내려받기 한 번

여러 번 시도해 본 결과 규칙은 이렇다 — **한 탭에서 파일은 딱 한 번 떨어진다.**
두 번째부터는 버튼을 눌러도 아무 일도 안 일어난다. 오류도 없고 차단 아이콘도 없다.

그래서 절차를 이렇게 굳힌다.

  ① **프롬프트는 아무 탭에서나 보낸다** (이미 받은 탭이어도 보내는 것은 된다)
  ② 그림이 뜨면 **새 탭을 만들고** 대화 URL로 이동한다
  ③ 새 탭에서 맨 아래로 스크롤 → 마지막 single-image 의 img 가 0x0 이면
     `computer scroll` 로 실제로 굴려 준다 (JS scrollTop 만으로는 지연 로딩이 안 풀릴 때가 있다)
  ④ 그 탭에서 한 번 내려받는다 → 다음 그림은 또 새 탭

  ⚠ 탭은 굳이 닫지 않는다. 그룹에 탭이 하나는 남아 있어야 한다.

## (옛 기록) 탭이 다운로드 상태에 갇힌다

한 탭에서 두어 번 받고 나면 그 뒤로는 버튼을 눌러도, 새로고침해도, 실제 마우스로 눌러도
파일이 **영영 안 떨어진다.** 크롬 주소창에는 차단 아이콘도 안 뜨고 저장 위치를 묻는 창도 없다.
사이트 설정에서 자동 다운로드를 허용해도 소용없다.

**해결: 새 탭을 연다.**

    tabs_create_mcp
    navigate(새 탭, 대화 URL)
    → 30초 기다린다 → 스크롤 → 다운로드 버튼 click  ← 바로 먹는다
    → 다 쓴 탭은 tabs_close_mcp

⚠ 탭을 닫으면 탭 그룹이 사라져서 `tabs_context_mcp({createIfEmpty:true})` 로 다시 만들어야 한다.
**그림 두 장마다 새 탭**이라고 생각하면 된다.

## ★★ 송신 버튼은 좌표로 못 누른다 — `find` 로 ref 를 얻어 누른다 (2026-08-21 확정)

스크린샷 좌표와 페이지 좌표가 **안 맞는다.** 실측: 스크린샷 1291px 인데 `innerWidth` 1527,
`devicePixelRatio` 2.2. 송신 버튼이 JS 로는 `(1088,543)` 인데 스크린샷에는 `(1011,505)` 로 보인다.
어느 쪽 좌표로 눌러도 안 먹었고, `Enter` 도 안 먹었다(줄바꿈조차 안 들어갔다).

    mcp__claude-in-chrome__find  query="메시지 보내기 send button"  →  ref_NNN
    computer  action=hover      ref=ref_NNN
    computer  action=left_click ref=ref_NNN

★ 컴포저 클릭은 좌표로도 먹는다(포커스는 잡힌다). **버튼만 ref 가 필요하다.**
⚠ 누른 직후 `입력창.innerText.length` 가 아직 3천대일 수 있다 — DOM 반영이 늦다.
   `document.body.innerText` 에 「말씀하신 내용」이 있으면 보내진 것이다. 다시 누르지 말 것.

## ★ 새 대화를 팔 때 execCommand 가 길이 1을 돌려주면

컴포저가 아직 포커스를 못 받은 것이다. **컴포저를 두 번 클릭하고 JS 로 `c.focus()` 까지** 부른 뒤
다시 넣으면 들어간다.

## ⑦ 생성이 5~7분 걸릴 수 있다 (Pro + 확장된 사고)

`Creating your image` 가 6분 넘게 떠 있어도 정상이다. `img[src^="blob:"]` 가 **하나 생겼는데
`naturalWidth` 가 0**이면 디코드 중이다 — **대화 URL 로 새로고침**하면 1024 로 잡힌다.
없다고 판단하고 다시 보내면 판을 하나 낭비한다.

## ⑧ 대화 id (2026-08-21 갱신)

지금 쓰는 대화 — `https://gemini.google.com/app/6fa255aa0a3dd6a9` (s20p01c 부터)
앞 대화 `bea759ffdafa7418` 는 그림 6장에서 목록 렌더가 느려졌다.

## ★★★ 2026-08-25(2) — 송신은 「JS 로 캐럿을 끝에 놓고 Enter」가 제일 잘 먹는다

이 세션에서 송신 버튼이 세 가지 방법을 다 튕겨 냈다 — `fire()` 이벤트 열 개도,
스크린샷 좌표 클릭도, 사이드바 접기도. `editorLen` 이 계속 4,116 그대로였다.

먹은 방법은 이것이다:

```js
const box=document.querySelector('div.ql-editor[contenteditable="true"]');
box.focus();
const sel=window.getSelection(), rng=document.createRange();
rng.selectNodeContents(box); rng.collapse(false);   /* ★ 캐럿을 글 끝으로 */
sel.removeAllRanges(); sel.addRange(rng);
```
그 다음 **computer action=key text="Return"**.

→ `editorLen` 이 1 로 떨어지고 `busy` 가 true 가 된다. 그것이 보내진 표시다.

★ 왜 Enter 가 먹고 클릭이 안 먹나 — 컴포저가 포커스를 쥐고 있으면 Enter 는
Quill 의 키 핸들러로 직행한다. 클릭은 Angular Material 의 히트 테스트를 통과해야 하는데
스크린샷 좌표(1374×734)와 페이지 좌표가 어긋나 있어 빗나간다.
**앞으로는 송신을 이 순서로 한다 — 넣기(execCommand) → 캐럿 끝 → Enter.**
버튼 클릭은 그 다음 수단이다.

## ⑨ 이미지가 0×0 으로 안 뜰 때 — src 를 손으로 다시 물린다

새로고침해도 `naturalWidth` 가 0 이면 (2026-08-25 에 겪었다) 이렇게 다시 물린다.

```js
const L=[...document.querySelectorAll('img.image')].pop();
L.removeAttribute('srcset');
const s=L.src; L.src=''; await new Promise(r=>setTimeout(r,300)); L.src=s;
await new Promise(r=>setTimeout(r,9000));  /* → 1024×1024 */
```

⚠ 그리고 **내려받기 버튼은 그림이 0×0 이어도 먹는다** — 파일은 따로 받아 온다.
내려받기가 실패한 줄 알고 다시 누르지 말고 `ls -lt ~/mnt/Downloads` 로 시각을 확인할 것
(2026-08-25 에 성공한 내려받기를 실패로 오판했다).

## ★★★★ 2026-08-25(4) — 결론: 송신은 **ref 로 누른다**. 좌표는 쓰지 마라.

세 가지를 다 겪고 나서 확정한다. **좌표는 어떤 계산으로도 못 맞춘다.**
같은 세션 안에서도 스크린샷과 뷰포트의 비가 1.365 였다가 1.078 이었다.
`getBoundingClientRect()` × (스크린샷/뷰포트) 도 안 맞는다.

**항상 이 넷을 이 순서로 한다.**

```
1) execCommand('insertText') 로 글을 넣는다
2) mcp__claude-in-chrome__find  query="메시지 보내기 send button"  → ref_NNN
3) computer  action=left_click  ref=ref_NNN      ← ★ 곧바로 누른다
4) editorLen 이 1 로 떨어지고 busy 가 true 면 보내진 것이다
```

⚠ **hover 를 먼저 하지 마라.** hover 한 뒤 같은 ref 로 클릭하면 안 먹는다(2026-08-25 에 겪었다).
   `find` 바로 다음에 `left_click` 을 해야 한다. 안 먹었으면 **다시 `find` 하고 다시 누른다.**
⚠ 앞 응답이 아직 돌고 있으면 `find` 가 「대답 생성 중지」 단추를 돌려준다 — 그때는 보낼 수 없다.
   `busy` 가 false 가 될 때까지 기다리고, **몇 분이 지나도 busy 가 안 풀리면 대화 URL 로 새로고침**한다
   (그림은 이미 다 나왔는데 busy 만 남아 있는 일이 잦다).

`find` 는 접근성 트리에서 찾으므로 창 크기·확대율과 무관하다.
Enter 키도, `fire()` 이벤트 열 개도, 스크린샷 좌표 클릭도 **믿지 마라** —
이 세션에서 셋 다 몇 번씩 조용히 실패했다. 실패해도 오류가 안 나서 더 나쁘다.
★ 모드 알약·메뉴 항목처럼 **DOM 으로 잡히는 것**은 `fire()` 가 잘 먹는다.
   `fire()` 가 안 먹는 것은 **송신 단추 하나**다.

## 2026-08-25(3) — (참고) 호버 → 확대로 확인 → 클릭

2026-08-25(2)에 적은 「캐럿 끝 + Enter」가 그 뒤로 안 먹었다. 그리고 `fire()` 도,
좌표 클릭도, 새 대화도, 새 탭도 전부 안 먹었다. 원인은 **좌표계가 어긋난 것**이었다.

`window.innerWidth/Height` 와 스크린샷 크기가 **서로 다르고, 비율도 x·y 가 다르다.**
예: 뷰포트 1066×569 인데 스크린샷은 1455×725 (x 1.365배 · y 1.274배).
그래서 `getBoundingClientRect()` 로 잰 자리로 클릭하면 빗나간다.
★ **`computer` 도구의 좌표는 스크린샷 좌표계다.** 페이지 좌표가 아니다.

먹는 순서는 이것이다.

1. `computer action=screenshot` — 파란 송신 단추가 **스크린샷에서** 어디 있는지 눈으로 읽는다.
2. `computer action=hover coordinate=[그 자리]`
3. `computer action=zoom region=[그 언저리]` — 커서 끝이 단추 위에 있고
   **「제출」 툴팁이 떴는지** 확인한다. 안 떴으면 자리를 고쳐 2로 돌아간다.
4. `computer action=left_click coordinate=[같은 자리]`
5. `editorLen` 이 1 로 떨어지고 `busy` 가 true 면 보내진 것이다. URL 도 /app/<id> 로 바뀐다.

★ 3번(확대로 툴팁 확인)을 건너뛰지 마라. 이것 하나로 「눌렀는데 왜 안 되지」를 안 겪는다.
★ Enter 키도 같은 이유로 못 믿는다 — 창 크기가 바뀌면 포커스가 어디 있는지 알 수 없다.

## ★★★★★ 2026-08-25(5) — 원인을 찾았다: **친 글만 보내진다**

몇 시간을 헤맨 끝에 갈랐다. 문제는 클릭이 아니라 **글을 넣는 방법**이었다.

| 넣는 방법 | 글이 보이나 | 보내지나 |
|---|---|---|
| `document.execCommand('insertText')` | ✅ 보인다 | ❌ **안 보내진다** |
| `quill.setText(TXT,'user')` | ✅ 보인다 | ❌ **안 보내진다** |
| `computer action=type` (진짜 키보드) | ✅ | ✅ **보내진다** |

DOM 에는 글이 있고 송신 단추도 「메시지 보내기」로 바뀌지만, Gemini 의 송신 처리기는
**진짜 입력 이벤트로 들어온 글만** 자기 모델로 인정한다. 그래서 눌러도 조용히 아무 일도 안 난다.
오류도 안 나고 네트워크 요청도 안 나간다 — 그래서 「클릭이 안 먹는다」로 오진하기 쉽다.

### 그래서 이렇게 한다

```
1) 프롬프트를 **한 줄로** 만든다 — computer action=type 은 줄바꿈을 그냥 버린다.
   문단은 " / " 로 잇고 소제목은 대문자로 쓴다 (THE LEFT LIMB: …).
   ⚠ 줄바꿈이 버려지는 것은 다행이다 — Enter 로 새 나가지 않는다.
2) 컴포저를 비운다 — quill.setText('','user') 로 지워도 된다(지우는 것은 먹는다).
   const q = window.Quill.find(document.querySelector('div.ql-editor').parentElement)
3) computer action=type 으로 통째로 친다. 4,200자도 한 번에 들어간다.
   ⚠ CDP 가 30초에 시간 초과를 뱉을 수 있는데 **글은 다 들어가 있다.** 길이를 확인하고 넘어간다.
4) computer action=screenshot 을 **새로 찍고**, 파란 화살표가 스크린샷의 어디 있는지 눈으로 읽는다.
5) 그 좌표로 computer action=left_click.
6) URL 이 /app/<id> 로 바뀌면 보내진 것이다.
```

★ **ref 클릭은 못 믿는다** — 될 때도 있고 안 될 때도 있다. 스크린샷 좌표가 더 낫다.
★ 컴포저가 여러 줄이 되면 단추가 아래로 내려간다. **매번 새로 찍어서** 좌표를 읽을 것.
★ `navigator.userActivation.hasBeenActive` 가 false 면 진짜 입력이 한 번도 안 닿은 것이다 —
  그때는 확장 프로그램 문제이니 사용자에게 말한다. true 인데 안 보내지면 위의 「친 글」 문제다.
★ 모드 알약과 메뉴 항목은 여전히 `fire()`(이벤트 열 개)로 고른다 — 그쪽은 잘 먹는다.

### ⚠ type 은 **한 번에** 다 쳐야 한다

길다고 두 번으로 쪼개 치면 **첫 토막만 저 혼자 보내진다**(2026-08-25 에 s20p07 에서 겪었다 —
1,277자짜리 반쪽이 그림으로 만들어졌다). 4,200자도 한 call 로 들어가니 쪼개지 마라.
CDP 가 30초 시간 초과를 뱉어도 글은 다 들어가 있다.

### ⚠ 좌표는 **매번 계산한다** — 공식은 이것 하나다

```
스크린샷좌표 = 페이지좌표 × (스크린샷너비 / window.innerWidth)
```
창 크기가 자주 바뀌므로 **누른 자리를 기억해 재활용하지 마라.** 매번
`getBoundingClientRect()` 로 재고 위 식으로 환산한다.

확인하는 법 — 누르기 전에 리스너를 걸어 두면 어디 닿았는지 알 수 있다.
```js
window.__p=null;
window.addEventListener('mousedown', e=>{window.__p={x:e.clientX,y:e.clientY}}, {capture:true});
```
누른 뒤 `window.__p` 가 null 이면 **입력이 아예 페이지에 안 닿은 것**이다 —
그때는 사용자에게 「크롬 창을 앞으로 꺼내 달라」고 부탁한다. 오늘 세 번 다 그것으로 살아났다.

## ★★★★★★ 2026-08-25(6) — 보내려면 그 탭이 **보이는 탭**이어야 한다

오늘 마지막으로 찾은 조건. `document.visibilityState` 가 답을 준다.

| | 결과 |
|---|---|
| `visibilityState === 'visible'` | 클릭이 닿고 **보내진다** |
| `visibilityState === 'hidden'` | 컴포저에 포커스는 가고 글도 쳐지는데 **송신만 조용히 실패** |

같은 탭에서 프롬프트 ①은 보이는 상태에서 한 번에 보내졌고,
탭이 뒤로 간 뒤 친 ②는 송신 단추에 정확히 닿는데도(mousedown 리스너로 확인)
아무 일도 안 났다.

★ **그래서 창을 여럿 띄워 병렬로 보내는 것은 안 된다.** 탭은 하나만 보일 수 있고,
  MCP 에는 탭을 활성화하는 도구가 없다(`navigate` 도, `cmd+alt+→` 도 안 먹는다).
  ⚠ 게다가 **보이던 탭을 닫으면** 초점이 다른 창으로 가 버려 남은 탭이 hidden 이 된다.

### 그러면 어떻게 여러 장을 돌리나

**한 탭에서 차례로 보내고, 대화 URL 만 적어 둔다.** 생성은 서버에서 도니까
보낸 뒤 곧바로 `/app` 으로 옮겨 다음 것을 보내도 된다. 나중에 각 대화 URL 로
돌아가 내려받으면 된다. 이것이 사실상의 병렬이다.

보내기 전에 항상 확인할 것:
```js
document.visibilityState        // 'visible' 이어야 한다
```
'hidden' 이면 사용자에게 「그 크롬 탭을 눌러 앞으로 꺼내 달라」고 부탁한다.

## ★★★★★★★ 2026-08-25(7) — 컴포저 좌표는 **매번** 재측정하고 **글자 수를 검증**한다

오늘 프롬프트 넷을 통째로 날렸다. 원인은 어이없다 — **입력칸을 안 눌렀다.**

창 크기가 바뀌면 컴포저의 y 좌표가 움직인다(오늘 363 ↔ 391 로 오갔다).
어긋난 좌표로 클릭하면 포커스가 `BODY` 에 남고, `computer action=type` 의 글자는
**어디에도 안 들어간다.** 그런데 그 다음 송신 클릭은 정상으로 보이고
**URL 도 `/app/<id>` 로 바뀐다.** 그래서 성공한 줄 알았다.

내용이 없으니 서버가 그 대화를 버린다 — 나중에 그 URL 로 가면 `/app` 으로 튕기고,
사이드바에도 없고, 「채팅 검색」에도 안 나온다. **흔적이 통째로 사라진다.**

### 반드시 이 순서로 한다

```js
// 1. 재측정 — 상수로 박아 두지 마라
const el = document.querySelector('div.ql-editor[contenteditable="true"]');
const r  = el.getBoundingClientRect();
// cx = r.x + r.width/2, cy = r.y + r.height/2   ← 이 좌표로 클릭
```
```
2. computer action=left_click  (cx, cy)
3. computer action=type        (프롬프트 한 줄)
4. ★ 검증 — el.innerText.length 가 프롬프트 길이와 같은가?
   activeElement.className 에 'ql-editor' 가 있는가?
5. 같을 때만 computer action=key "Return"
6. URL 이 /app/<id> 로 바뀌었는지, 화면에 내 프롬프트가 보이는지 확인
```

★ **Enter 가 송신 단추보다 안전하다.** 단추도 창 크기에 따라 움직이는데
  Enter 는 포커스만 맞으면 늘 듣는다. 4·5단계를 한 batch 로 묶으면 왕복도 준다.

## ★★★★★★★ 2026-08-25(8) — 그림 모델은 **넷은 세지만 여덟은 못 센다**

s13p03 v1 이 요구한 수를 거의 다 놓쳤다. 하나같이 **하나씩 모자랐다.**

| 요구 | 나온 것 |
|---|---|
| 조끼 단추 여덟 | **여섯** ✗ |
| 조끼 단추 넷 | **넷** ✓ |
| 따로 선 사람 넷 | 셋 ✗ |
| 큰 판 든 사람 셋 | 둘 ✗ |
| 도랑 셋 | 넷 ✗ |

★ 그런데 **넷 한 줄은 정확했다.** 그래서 규칙은 이것이다 —
**세는 단위를 넷 이하로 낮추고, 큰 수는 「넷씩 몇 줄」로 쪼갠다.**

v2 에서 CD8 을 「**더블브레스티드 조끼 — 넷씩 두 줄**」로, CD4 를
「싱글브레스티드 — 한 줄 넷」으로 바꿨다. 학생은 「두 줄이면 여덟」로 읽고,
모델은 늘 「넷 한 줄」만 그리면 된다.

그리고 **「N 중 M」을 한 문장에 넣지 마라.** 「넷 중 셋만 판을 들었다」는
넷도 셋도 틀렸다. 「판 든 사람 셋 + 빈손 하나」로 **둘로 쪼개** 각각 못 박는다.
개수를 말할 때는 자리도 같이 준다 — 「왼쪽에서 하나 · 왼쪽 아래에서 하나 · 오른쪽 아래에서 하나」.

## ★★★★★★★ 2026-08-25(9) — 내려받기는 5초로는 모자라다

`fire(다운로드)` 뒤 5초에 `ls` 하면 아직 없다. **10초 이상** 기다린 뒤 확인한다.
오늘 5초에 없길래 실패로 보고 새 탭에서 다시 눌렀더니 `(1)` 붙은 중복이 생겼다.
「탭 하나에 한 번만」은 여전히 맞지만, **판정은 시각으로 한다** —
`ls -lt --time-style=+%H:%M:%S` 로 방금 시각의 파일이 있는지 본다.

## ★★★★★★★ 2026-08-25(10) — 새 대화를 열면 모델이 **Flash 로 되돌아가 있다**

`/app` 으로 옮길 때마다 모드가 초기화되는데, **가끔 `Flash Extended` 로 돌아온다.**
그런데 「Extended 가 켜져 있으면 건너뛴다」는 검사는 그것을 통과시킨다.

```js
// ✗ 틀림 — Flash Extended 도 통과한다
if(!/Extended/.test(pill.innerText)) { ...켠다... }

// ✓ 맞음 — Pro 와 Extended 를 따로 본다
const need = !/Pro/.test(pill.innerText) || !/Extended/.test(pill.innerText);
```

되돌리는 절차는 **두 번 연다** — ① 알약 열고 「3.1 Pro」를 누르고,
② 다시 알약을 열어 「확장된 사고 모델」을 누른다. 한 번에는 안 된다.
끝나면 `aria-label` 이 「현재 **Pro Extended** 모드 사용 중」인지 반드시 읽어 확인한다.

## ★★★★★★★ 2026-08-25(11) — 키보드는 **보이는 탭에만** 닿는다 (타이핑도 그렇다)

전에는 「hidden 이면 **송신만** 실패한다」고 적었는데, 더 정확히는 이렇다.

| | hidden |
|---|---|
| `javascript_tool` (JS 실행·`fire()`·`el.focus()`) | ✅ 된다 |
| `computer action=left_click` | ✅ 좌표는 닿는다 |
| **`computer action=type` (실제 키 입력)** | ❌ **아무 데도 안 들어간다** |
| **`computer action=key "Return"` (송신)** | ❌ 조용히 실패 |

★ `el.focus()` 가 `activeElement` 를 컴포저로 바꿔 놓아도 소용없다 —
**키 이벤트 자체가 안 배달된다.** 그래서 타이핑 전에도 `visibilityState` 를 봐야 한다.

⚠ 한 번 **보이는 상태에서 치기 시작하면** 도중에 창이 뒤로 가도 글은 끝까지 들어간다
(s17p01 3,802자가 그랬다. CDP 30초 시간 초과가 나도 마찬가지다).
그러니 순서는 **① visible 확인 → ② 클릭 → ③ 타이핑 → ④ 길이 검증 → ⑤ 다시 visible 확인 → ⑥ Enter**.

## ★★★★★★★★ 2026-08-26(1) — [정정] **execCommand 로 넣은 글도 보내진다.** `type` 은 이제 안 써도 된다

2026-08-25(5) 에 「친 글만 보내진다」고 적었는데 **절반만 맞았다.** 오늘 s04p04 v2·v3 를
둘 다 `document.execCommand('insertText')` 로 넣고 **`computer action=key "Return"`** 으로
보냈고 **둘 다 정상으로 접수됐다**(대화 `b72b319122ca478f`, 3,031자와 1,864자).

| 넣는 방법 | 보내는 방법 | 결과 |
|---|---|---|
| `execCommand('insertText')` | **송신 단추 클릭** | ❌ 조용히 실패 (옛 기록) |
| `execCommand('insertText')` | **`key "Return"`** | ✅ **보내진다** (오늘 두 번 확인) |
| `computer type` | 단추 클릭 / Return | ✅ 보내진다 (느리다) |

갈리는 것은 **글을 넣는 방법이 아니라 보내는 방법**이었다. Quill 은 `beforeinput`/`input` 을
듣고 있어서 execCommand 로 넣은 글이 **제 모델에 정상으로 들어간다**. 그 모델을 읽는 것은
**키보드 처리기**이고, 송신 단추는 다른(앵귤러 쪽) 상태를 읽는 듯하다.

### ★ 그래서 새 절차는 이렇다 — 훨씬 빠르고 안전하다

```js
// ① 프롬프트를 base64 로 실어 보낸다 (따옴표·유니코드 이스케이프 걱정이 없다)
const bin=atob(B64); const b=new Uint8Array(bin.length);
for(let i=0;i<bin.length;i++)b[i]=bin.charCodeAt(i);
const TXT=new TextDecoder('utf-8').decode(b).trim();
// ② 캐럿을 컴포저 전체에 걸고 통째로 갈아 끼운다
const ed=document.querySelector('.ql-editor'); ed.focus();
const sel=getSelection(), r=document.createRange();
r.selectNodeContents(ed); sel.removeAllRanges(); sel.addRange(r);
document.execCommand('insertText',false,TXT);
// ③ 길이를 **문자 단위로 정확히** 맞춰 본다
return JSON.stringify({want:TXT.length, got:ed.innerText.trim().length,
                       match:ed.innerText.trim()===TXT});
```
그 다음 `computer action=key "Return"` 한 번.

### ★ 이것이 없애 주는 골칫거리 셋

1. **좌표를 안 쓴다** — 컴포저가 363↔388↔391 로 움직여도 상관없다.
   2026-08-25 에 프롬프트 넷을 통째로 날린 사고가 이 좌표 어긋남 때문이었다.
2. **CDP 30초 시간 초과가 없다** — 3,000자가 한 호출에 즉시 들어간다.
3. **쪼개 치다 반쪽이 보내지는 사고가 없다** — 통째로 갈아 끼우니 반쪽이 있을 수 없다.

### ⚠ 그래도 남는 것

- 길이 검증은 **여전히 반드시 한다.** `match:false` 면 절대 Enter 를 치지 마라.
- **`hidden` 이어도 `key "Return"` 은 오늘 두 번 다 먹었다**(2026-08-25(11) 의 표에서
  Return 칸은 정정한다). 다만 `computer type` 은 여전히 보이는 탭에서만 먹으니,
  execCommand 로 넣는 이 절차를 쓰면 **가시성 자체를 신경 쓸 일이 없다**.
- 모델 알약(Pro + 확장된 사고) 확인은 그대로 필요하다.

## ★★★★★★★★ 2026-08-26(2) — [재정정] Enter 는 **역시 보이는 탭에만** 닿는다

같은 날 앞 절에서 「hidden 이어도 Return 이 두 번 다 먹었다」고 적었는데 **틀렸다.**
s08p02 를 보내려 할 때 hidden 상태에서 **Enter 가 네 번 다 배달되지 않았다** —
`edLen` 도 `blocks`(31)도 그대로였다. 즉 키 이벤트가 아예 안 온 것이다.

앞 절의 두 번은 그 순간 창이 실제로 앞에 있었던 것으로 본다
(`javascript_tool` 로 읽은 `visibilityState` 는 조회 시점의 값이라 그 사이에 바뀔 수 있다).

| 상황 | `computer key "Return"` |
|---|---|
| `visibilityState === 'visible'` | ✅ 먹는다 |
| `hidden` (`hasFocus:true` 여도) | ❌ **안 먹는다** |

★ `resize_window` 를 부르면 `document.hasFocus()` 는 true 가 되지만
`visibilityState` 는 **여전히 hidden 이고 키는 안 온다.** 창을 앞으로 꺼내는 방법이 아니다.

★ 송신 단추 `fire()` 는 **역시 안 먹는다** — 2026-08-25(5) 의 기록이 맞다.
`execCommand` 로 넣은 글에는 단추가 「메시지 보내기」로 멀쩡히 바뀌고 클릭도 받지만
아무 일도 일어나지 않는다. **그래서 Enter 말고는 길이 없고, Enter 는 보이는 탭에만 닿는다.**

### 그러니 순서는 이렇다

```
① execCommand 로 글을 넣는다 (좌표도 가시성도 필요 없다 — 여기까진 hidden 에서 다 된다)
② 정규화 대조로 검증한다 (아래)
③ visibilityState 를 읽어 'visible' 인지 본다
   → hidden 이면 **사용자에게 창을 앞으로 꺼내 달라고 말한다.** 글은 컴포저에 안전하게 남는다
④ visible 이면 캐럿을 끝에 놓고 computer key "Return"
⑤ URL 이 /app/<id> 로 바뀌었는지 확인
```

## ★★★ 2026-08-26(3) — 줄바꿈이 있는 프롬프트의 검증은 **정규화 해시**로 한다

`execCommand` 는 줄바꿈을 살려 넣는데, Quill 이 각 줄을 `<p>` 로 만들면서
`innerText` 에 빈 줄이 더 생긴다. 그래서 **글자 수가 안 맞는다** (3,383 → 3,425).
이때 「match:false 니까 보내지 마라」로 멈추면 멀쩡한 프롬프트를 버리게 된다.

**공백을 뭉개고 견주면 정확히 맞는지 알 수 있다.** 양쪽에서 같은 셈을 한다.

브라우저에서:
```js
const norm=s=>s.replace(/ /g,' ').replace(/\s+/g,' ').trim();
const n=norm(document.querySelector('.ql-editor').innerText);
let h=5381; for(let i=0;i<n.length;i++){h=((h*33)^n.charCodeAt(i))>>>0;}
JSON.stringify({len:n.length,hash:h})
```
컨테이너에서:
```python
n=re.sub(r'\s+',' ', t.replace(' ',' ')).strip()
h=5381
for ch in n: h=((h*33) ^ ord(ch)) & 0xFFFFFFFF
print(len(n), h)
```
둘의 **길이와 해시가 같으면** 잘림도 섞임도 없다 (s08p02 v2: 3371 / 997652139 로 일치).
⚠ 한 줄짜리 프롬프트라면 예전대로 `got===TXT` 로 그냥 대조하면 된다.

## ★★★★★★★★ 2026-08-26(4) — **같은 물건을 네 군데에 서로 다른 개수로 그리게 하지 마라**

s02p04(CD4:CD8 저울)에서 두 번 연달아 실패했다. 요구는 이랬다.

> 저울 **넷**의 접시마다 꼬리표를 달고 — **왼쪽 접시**의 표는 「한 줄에 넷」,
> **오른쪽 접시**의 표는 「넷씩 두 줄」

| 시도 | 결과 |
|---|---|
| v1 | 네 표가 전부 **셋**. 왼쪽·오른쪽 구분도 없음 |
| v2 (「셋은 잘못이다」를 지목하고 자리를 못 박음) | 넷·셋·「셋씩 두 줄」·「넷씩 두 줄」이 **뒤섞임** |

★ **왜 s13p03 은 됐는데 여기는 안 되나.** s13p03 은 **조끼 둘**이었다 —
「한 줄에 넷」인 사람 하나, 「넷씩 두 줄」인 사람 하나. **두 자리에 두 무늬**다.
s02p04 는 **네 자리에 두 무늬**를 번갈아 놓으라는 것이었고, 모델이 그 대응을 못 지킨다.

### 규칙

```
같은 종류의 물건을 세 군데 이상에 놓고 자리마다 개수를 달리하게 하지 마라.
「두 자리에 두 무늬」까지가 한계다. 그 위는 개수도 대응도 무너진다.
```

★ 「모델이 그린 잘못을 지목해 고치게 하기」(s04p04 v3 에서 통했던 것)도
**여기서는 안 통했다.** 그 기법은 **한 군데를 고칠 때** 통하고,
**네 군데의 대응을 고칠 때는 안 통한다.**

⚠ 설치하지 않았으므로 잃은 것은 없다. s02p04 는 보류로 남긴다 —
1장을 얻으려고 7장이 걸린 판을 거는 일이기도 하다.
