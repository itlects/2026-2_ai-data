# Week12 — 채용·HR 데이터와 AI 윤리
- 공식 자료: [고용24 채용정보 API](https://www.work24.go.kr/cm/e/a/0110/selectOpenApiSvcInfo.do?fullApiSvcId=000000000000000000000000000000), 인증키 필요.
- data/work24_demo.xml: 공식 필드 구조를 참고해 작성한 가상 공고 6건 (실제 API 응답 아님).
- data/job_requirements.csv: 가상 공고별 실습용 역량 요구사항.
- data/synthetic_audit.csv: 120쌍 240행, 임의 감사 그룹 A/B, 실제 개인정보 없음. historical_ai_score는 인위적 편향을 넣은 모의 과거 AI 출력이며 학습한 모델의 예측은 아님. 실제 채용 금지.
- notebooks: 학생용 및 교수자 시연용. 파일 → Drive에 사본 저장 후 CPU에서 전체 실행.
- 실제 API 호출은 마지막 선택 단계에서 개인 인증키로 진행.
- 자료 생성 및 전체 코드 실행 검증: 2026-11-19. 실시간 API는 키 없음으로 미검증.
