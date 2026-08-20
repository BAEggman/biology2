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
