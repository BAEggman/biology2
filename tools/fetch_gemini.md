# Gemini 그림 회수 — 사용자 손을 안 빌리는 절차 (2026-08-20)

전체 설명은 프로젝트 문서 `claude/생물Sketchy_Gemini자동화_해결.md`에 있다.
여기는 명령만 적어 둔다.

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

## ★★★ 탭 하나당 내려받기 **한 번** (2026-08-20 확정)

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
