# OPS Dashboard Clone

원본 Streamlit 앱의 UI, UX, 탭, 날짜 필터, 차트, 상세표, 담당자 선택 흐름을 유지한 포트폴리오용 익명화 복제본입니다.

## 실행

```powershell
python -m streamlit run app.py
```

브라우저에서 표시되는 주소를 열면 됩니다.

## 보호 범위

- 기간: 2026년 7월 1일~31일
- 인명: Member A~E
- 브랜드: Brand 01~13
- 원본 서비스 주소와 실제 인명·브랜드명은 포함하지 않음

## Streamlit 휴면 방지

GitHub Actions의 `.github/workflows/keep-streamlit-awake.yml`이 6시간마다 앱 상태를 확인하고 배포 브랜치에 내용 변경 없는 빈 커밋을 추가합니다. 이 커밋이 Streamlit Community Cloud의 무활동 시간을 재설정합니다.

필요할 때는 GitHub의 **Actions → Keep Streamlit app awake → Run workflow**에서 수동 실행할 수 있습니다. 자동 커밋 메시지는 `chore: reset Streamlit inactivity timer [skip ci]`입니다.
