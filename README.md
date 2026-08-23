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

GitHub Actions의 `.github/workflows/keep-streamlit-awake.yml`이 6시간마다 공개 앱 URL을 방문합니다. 필요할 때는 GitHub의 **Actions → Keep Streamlit app awake → Run workflow**에서 수동 실행할 수 있습니다.

Streamlit Community Cloud는 트래픽이 12시간 없으면 앱을 휴면 처리합니다. 또한 GitHub는 공개 저장소에 60일간 활동이 없으면 예약 워크플로를 자동 중지할 수 있으므로, 장기간 저장소를 수정하지 않았다면 Actions 화면에서 워크플로 활성 상태를 확인해야 합니다.
