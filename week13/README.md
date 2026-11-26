# Week13 생성형 AI 콘텐츠 제작

인공지능과 데이터 활용 · 2026-2학기 · 120분

기상청 ASOS 대구(143) 2025년 관측자료로 **인스타그램 카드뉴스 4장**을 만듭니다. 순서는 다음과 같습니다.

1. 데이터에서 사실표를 계산합니다.
2. 사람이 먼저 카드 문구를 씁니다.
3. 프롬프트를 v1에서 v4까지 고쳐 가며 AI 문구를 받습니다.
4. 사람이 검증하고 편집합니다.
5. PNG 카드를 만듭니다.
6. 사람이 쓴 버전과 AI 버전을 블라인드로 비교합니다.

AI는 Colab에 들어 있는 `google.colab.ai`(Gemini)를 씁니다. API 키는 필요 없습니다. Colab AI를 쓸 수 없으면 오프라인 예비 응답으로 자동 전환되므로 실습이 끊기지 않습니다.

## 바로 시작
- [학생 워크북 Colab](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/week13/notebooks/Week13_Student_Workbook.ipynb)
- [강의자 시연 완성본 Colab (실행 결과 포함)](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/week13/notebooks/Week13_Instructor_Demo.ipynb)
- [강의 노션](https://app.notion.com/p/41db2e6bf80780b5bb0bc96a118d3ba5)
- [Drive 주차 폴더](https://drive.google.com/drive/folders/1SoASL8YdTQ4B1iCso4-C6cMDqJ-tjBZw)

## 폴더
| 경로 | 내용 |
|---|---|
| `data/daegu_2025_daily.csv` | 2025년 일자료 365행 × 5열. Drive `01_실습데이터`에 있는 파일과 같으며, 여기 있는 것은 백업입니다. |
| `notebooks/` | 학생 워크북, 강의자 시연 완성본 |
| `figures/` | 개념 그림 c1~c4 |
| `results/` | 완성본 실행 결과: 카드 4장, 월별 그림, 비교 그래프, 사실표·비교표 CSV |
| `materials/` | 출처(SOURCES.md), 교수자 가이드, 오프라인 예비 응답(JSON) |
| `tools/` | 데이터·노트북·그림 생성 스크립트 |
| `rag/` | (별도) PDF RAG 워크북. 이번 개정에서는 손대지 않았습니다. |
| `_previous_draft/` | 이전 ChatGPT 초안(가상 행사 홍보문). 사용하지 않습니다. |

## 재현
```bash
cd week13
python tools/build_week13_data.py      # ../Week11/data → data/daegu_2025_daily.csv
python tools/make_notebooks.py         # notebooks/*.ipynb
python tools/make_concept_figures.py   # figures/c1~c4
```
강의자 완성본은 생성한 뒤 실행해서 결과를 저장합니다. 2026-11-26에 두 노트북을 처음부터 끝까지 실행했고 오류는 0건이었습니다. 이때는 오프라인 예비 응답 경로로 실행했습니다.
