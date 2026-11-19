# Week 14 — 프로젝트 발표: AI를 활용한 지하철 혼잡도 분석

- 학생용: [Colab](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/week14/Week14_Student.ipynb)
- 강의자용: [Colab](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/week14/Week14_Instructor.ipynb)
- 데이터: subway_project.csv (UTF-8 BOM, 1,662 rows, 7 columns)
- 출처: 10주차 제공 파일 subway_congestion_20250331.csv, https://drive.google.com/file/d/1jTFSAgocpPDHgfU0tlwdVul4stXIq9gi/view
- 가공: 요일구분, 호선, 역번호, 출발역, 상하구분, 8시00분, 18시00분 열 선택 후 영문 열 이름 부여. 원자료의 집계값을 유지.
- 입력: day, line, direction, morning; 목표: evening; station_id는 그룹 분리용.
- CPU 실행, pandas, matplotlib, scikit-learn. Notion의 순서대로 실행하거나 Colab의 모든 셀을 위에서부터 수행.
- 검증: 로컬 scikit-learn 1.8.0에서 순차 실행. 학습 1,326/평가 336행, 평균 기준선 MAE 20.43%p, 랜덤 포레스트 MAE 13.48%p.
- 한계: 특정 날짜의 실시간 예측 또는 인과관계 분석이 아니라 같은 집계 자료의 미학습 역번호에 대한 추정.

Notion 강의: https://app.notion.com/p/41db2e6bf80780118eb4c3b3dbcec78e
Drive 자료: https://drive.google.com/drive/folders/1IDTg9zDXL3B5IaGtKt_Yvx-8nequ1TOo
