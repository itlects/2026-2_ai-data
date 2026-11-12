# Week10 교통 데이터의 시각화

인공지능과 데이터 활용 · 2026-2학기 · 120분
서울 열린데이터광장의 지하철 승하차 데이터를 시각화하고, 실제 열차 혼잡도·AI 혼잡도 예측과 비교합니다.

## 바로 시작
- [학생 워크북 Colab 열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week10/notebooks/Week10_Student_Workbook.ipynb)
- [완성 예제 Colab 열기 (실행 결과 포함)](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week10/notebooks/Week10_Completed_Example.ipynb)
- [강의 노션](https://app.notion.com/p/40eb2e6bf80780d0a91be75b4a596677) · [Drive 주차 폴더](https://drive.google.com/drive/folders/1QAzK6zvNbnmODChS9MrjmB9AnERzdPgn)

## 폴더
| 경로 | 내용 |
|---|---|
| `data/` | 학생용 CSV 3종(UTF-8). 노트북이 자동으로 읽음 |
| `data/original/` | 열린데이터광장·공공데이터포털에서 받은 원본 그대로 |
| `notebooks/` | 학생 워크북(기록 칸 비어 있음), 완성 예제(실행 결과·예시 답변) |
| `figures/` | 노션용 개념 그림 c1~c4 |
| `results/` | 완성 예제 실행 결과 그림 01~08, `ai_mae.csv` |
| `materials/` | 출처(SOURCES.md), 교수자 가이드(기준 결과·오류 대응) |
| `tools/` | 데이터 준비·노트북 생성·개념 그림 생성 스크립트 |

## 데이터
| 파일 | 행×열 | 내용 |
|---|---|---|
| `subway_hourly_202609.csv` | 621×52 | 2026년 9월 호선·역별 시간대별 승하차 인원(한 달 합계), OA-12252 |
| `subway_congestion_20250331.csv` | 1662×45 | 서울교통공사 1~8호선 열차 혼잡도(%, 30분, 평일/토/일, 방향별) |
| `citydata_places_121.csv` | 121×5 | 서울 실시간 도시데이터 주요 121장소 목록 |

자세한 출처·한계는 [materials/SOURCES.md](materials/SOURCES.md).

## 재현
```bash
cd Week10
python tools/build_week10_data.py      # data/original → data/*.csv
python tools/make_notebooks.py         # notebooks/*.ipynb 생성
python tools/make_concept_figures.py   # figures/c1~c4.png
```
검증: Python 3.13, pandas 3.0.5, matplotlib 3.11, scikit-learn 1.9.1에서 두 노트북을 처음부터 끝까지 실행해 오류 0건.
