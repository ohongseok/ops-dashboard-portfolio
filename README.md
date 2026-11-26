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

## Streamlit 휴면 완화 및 가용성 확인

[대시보드 열기](https://ops-dashboard-portfolio.streamlit.app/)

GitHub Actions의 `.github/workflows/keep-streamlit-awake.yml`이 3시간마다 Chromium 브라우저로 앱을 방문합니다. 휴면 해제 버튼이 표시되면 클릭하고, 실제 대시보드의 지표가 표시되는지 확인하며 최대 3회 재시도합니다. HTTP 200이나 상태 주소 응답만으로 성공 처리하지 않습니다.

- 한국 시간 기준 예정 시각: 매일 00:23, 03:23, 06:23, 09:23, 12:23, 15:23, 18:23, 21:23. GitHub 사정에 따라 지연되거나 누락될 수 있습니다.
- 실행 결과와 화면 캡처: **Actions → Keep Streamlit app awake**. 캡처는 7일간 보관합니다.
- 수동 실행: 같은 화면의 **Run workflow**.
- 저장소에 7일 이상 커밋이 없으면 빈 heartbeat 커밋을 추가합니다. 이는 저장소 활동 유지 목적이며, Streamlit 방문 시간을 초기화한다고 보장하지 않습니다.
- Community Cloud는 12시간 무접속 시 앱을 휴면시킵니다. 이 작업은 휴면 가능성을 줄이는 보조 수단이며 24시간 가동을 보장하지 않습니다.
- 공개 저장소의 예약 작업은 저장소 활동이 60일간 없으면 GitHub에서 중지할 수 있습니다. 자동 작업이 중지되면 Actions에서 재활성화해야 합니다.

공식 문서: [Streamlit 앱 관리](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app), [GitHub 예약 작업 제한](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
