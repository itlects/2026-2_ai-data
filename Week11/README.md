# Week11 환경·기후 데이터의 가공 및 분석

인공지능과 데이터 활용 · 2026-2학기 · 120분
기상청 ASOS 시간자료(대구 143, 2021~2025)를 일자료로 가공하고, 단순 추세 예측 3가지와 AI 예측 2가지의 하루 뒤 평균기온 예측 성능을 비교합니다.

## 바로 시작
실습 데이터는 Google Drive `강의11주_환경·기후 데이터의 가공 및 분석/01_실습데이터`에 있습니다. 노트북 1단계에서 Drive 파일 ID로 이 데이터를 내려받아 읽습니다(gdown). 이 저장소의 `data/`는 Drive에 접속하지 못할 때 쓰는 백업입니다.

- [학생 워크북 Colab 열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week11/notebooks/Week11_Student_Workbook.ipynb)
- [강의자 시연 완성본 Colab 열기 (실행 결과 포함)](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week11/notebooks/Week11_Instructor_Demo.ipynb)
- [강의 노션](https://app.notion.com/p/41cb2e6bf80780599600fbbb9501e8c4) · [Drive 주차 폴더](https://drive.google.com/drive/folders/1THcJdADR-JKKNZHZOJUW9fr2JpeNcmFp)

## 폴더
| 경로 | 내용 |
|---|---|
| `data/daegu_asos_hourly_2021_2025.csv` | 학생용 시간자료 43,823행 × 8열(UTF-8). Drive 원본과 같은 파일(백업용) |
| `data/original/` | 기상자료개방포털 ASOS 시간자료 연도별 원본 5개(CP949) |
| `notebooks/` | 학생 워크북(기록 칸 비어 있음), 강의자 시연 완성본(실행 결과와 예시 답변 포함) |
| `figures/` | 노션·노트북에 쓰는 개념 그림 c1~c6 |
| `results/` | 완성본 실행 결과 그림 01~07, `week11_metrics.csv` |
| `materials/` | 출처(SOURCES.md), 교수자 가이드(기준 결과, 오류 대응) |
| `tools/` | 데이터 결합, 노트북 생성, 개념 그림 생성 스크립트 |

## 기준 결과 (2025년 365일, 하루 뒤 평균기온)
| 방법 | MAE(°C) | RMSE(°C) |
|---|---:|---:|
| AI 선형회귀 | 1.566 | 2.049 |
| AI 랜덤포레스트 | 1.620 | 2.131 |
| 어제 그대로(지속 예측) | 1.633 | 2.184 |
| 최근 7일 직선추세 | 2.389 | 3.127 |
| 최근 7일 평균 | 2.500 | 3.177 |

## 재현
```bash
cd Week11
python tools/build_week11_data.py       # data/original → data/daegu_asos_hourly_2021_2025.csv
python tools/make_notebooks.py          # notebooks/*.ipynb 생성
python tools/make_concept_figures.py    # figures/c1~c6.png
jupyter nbconvert --to notebook --execute --inplace notebooks/Week11_Instructor_Demo.ipynb
```
검증 환경은 Python 3.13, pandas 3.0.5, matplotlib 3.11, scikit-learn 1.9.1입니다. 두 노트북을 처음부터 끝까지 실행했을 때 오류는 0건이었습니다.
