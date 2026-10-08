# Week04 헬스케어 데이터관리

Kaggle **FitBit Fitness Tracker Data** 원자료(걸음수·수면)의 품질을 점검하고, **규칙 기반 알림**과 **AI 이상탐지(Isolation Forest)** 결과의 차이를 비교한다.

> 본 실습은 교육 목적이며 의료 진단을 위한 것이 아니다.

## 학습목표
- 웨어러블 걸음수·수면 원자료를 불러오고 구조를 확인한다.
- 결측치·중복·범위 오류·‘숨은 결측’(기기 미착용)을 식별한다.
- 사용자 Id + 날짜 기준으로 두 데이터를 결합한다.
- 규칙 기반 알림과 Isolation Forest 이상탐지를 구현하고 결과 차이를 해석한다.

## 파일 구성
| 경로 | 설명 |
|---|---|
| `data/dailyActivity_merged.csv` | Kaggle 원자료 · 940행 × 15열 · 33명 · 2016-04-12 ~ 05-12 |
| `data/sleepDay_merged.csv` | Kaggle 원자료 · 413행 × 5열 · 24명 · 완전 중복 3행 포함 |
| `colab/Week04_Healthcare_Data_Management_실습.ipynb` | 학생용(TODO 채우기) |
| `colab/Week04_Healthcare_Data_Management_완성.ipynb` | 완성본(실행 검증 완료) |
| `examples/week04_toy_steps_sleep.csv` | 개념 설명용 소형 가상 데이터(42일, 오류 의도적 삽입) |
| `examples/week04_example_rule_vs_ai_toy.py` | 소형 데이터 예제 코드 |
| `workbook/week04_workbook_checklist.csv` | 단계별 체크리스트(기대값 포함) |
| `workbook/week04_result_table_template.csv` | 규칙 vs AI 결과표 양식 |
| `figures/` | 강의자료 그림(PNG·SVG) |

## 데이터 받기
- **방법 A** — [Kaggle](https://www.kaggle.com/datasets/arashnic/fitbit)에서 ZIP 다운로드 → `mturkfitbit_export_4.12.16-5.12.16/Fitabase Data 4.12.16-5.12.16/` 폴더의 두 CSV 사용  
  (ZIP 안의 `3.12.16-4.11.16` 폴더에는 sleepDay 파일이 없으므로 사용하지 않는다)
- **방법 B** — 수업 Google Drive `강의4주/02_데이터` 제공본
- **방법 C** — Colab에서 바로 읽기
  ```python
  BASE = 'https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week04/data/'
  daily = pd.read_csv(BASE + 'dailyActivity_merged.csv')
  sleep = pd.read_csv(BASE + 'sleepDay_merged.csv')
  ```

## 기준 결과(완성 노트북, scikit-learn 1.x)
| 항목 | 값 |
|---|---|
| sleep 중복 제거 | 413 → 410 |
| 미착용 의심일(걸음 0 & 비활동 1440분) | 72 |
| merge 결과 | 410행 × 19열 |
| 규칙 이상 / AI 이상(contamination=0.05) | 42 / 21 |
| 교차표 (규칙O·AIO / O·X / X·O / X·X) | 12 / 30 / 9 / 359 |

## 출처
Möbius (2020). *FitBit Fitness Tracker Data*. Kaggle. License: CC0 Public Domain.  
원 데이터: Furberg, R., Brinton, J., Keating, M., & Ortiz, A. (2016). Crowd-sourced Fitbit datasets 03.12.2016-05.12.2016. Zenodo.
