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
