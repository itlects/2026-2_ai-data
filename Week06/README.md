# Week06 고객 리뷰 데이터의 가공 및 분석

온라인 쇼핑몰 **실제 상품 후기**(네이버 쇼핑, 공개 말뭉치)로 감성데이터를 직접 수집·정제하고,
사람이 만든 **키워드 규칙**과 **AI(머신러닝) 감성분석** 결과를 비교·검증한다.

- Notion 학습자료: https://app.notion.com/p/3f9b2e6bf807802f871ffe414d026a18
- Google Drive 강의6주: https://drive.google.com/drive/folders/1lPUua3b9LWpFgj5wh5A-Ji_CbDbckgOd
- 데이터 출처: [bab2min/corpus](https://github.com/bab2min/corpus/tree/master/sentiment) `naver_shopping.txt` (2020, Public Domain) — 자세한 내용 [data/DATA_SOURCES.md](data/DATA_SOURCES.md)

## 학습목표
1. 감성데이터를 얻는 경로(공개 말뭉치·포털·설문·API·크롤링)와 확인 사항(출처·라이선스·라벨 방식)을 설명하고, 공개 원자료를 직접 내려받아 재현 가능한 표본을 만든다.
2. 리뷰 텍스트의 결측·중복을 점검하고, 원문을 보존한 채 분석용 텍스트를 정리·탐색한다.
3. 직접 읽고 판단한 근거로 키워드 규칙을 만들고, 실패 사례(부정어·대조·별점 잡음)를 분석해 개선한다.
4. TF-IDF + 로지스틱 회귀로 감성 분류기를 학습해 예측하고, AI가 사용한 단서와 확신도를 해석한다.
5. 교차표·일치율·정확도·재현율로 두 방법을 비교하고, 라벨의 한계를 고려해 사람이 최종 판단한다.

## 파일 구성
| 경로 | 설명 |
|---|---|
| `data/week06_reviews_300.csv` | 수업 데이터: 별점 1·2·4·5 각 75건 (열: review_id, src_line, rating, rating_label, review_text) |
| `data/naver_shopping.txt.gz` | 원자료 20만 건 미러 (원본 그대로 gzip) — 워크북 3 학습용, 원 배포처 장애 시 워크북 0 대체 |
| `data/week06_MANIFEST.csv` | 파일 크기·MD5·행 수 (Drive·업로드 파일이 원본과 같은지 확인, Drive 폴더 자동 탐색 표식) |
| `data/DATA_SOURCES.md` | 출처·라이선스·정제 규칙·한계·다른 수집 경로 |
| `colab/Week06_이론예제_파이썬문법.ipynb` | **이론 시간용 예제** — 노션 본문 순서(공통 파이썬 기초 예제 1–9 → 3.1~3.6 예제 10–26)대로 워크북 코드를 작은 예제로 한 셀씩 실행하며 설명. 외부 데이터 없이 약 20초 |
| `colab/Week06_00_감성데이터수집_실습.ipynb` / `_완성.ipynb` | **워크북 0** 원자료 다운로드 → 품질 점검 → 정제 → 층화추출 → 수집 기록 (실습 TODO 5) |
| `colab/Week06_리뷰감성분석_실습.ipynb` / `_완성.ipynb` | **워크북 1~4** 정제·탐색 → 키워드 규칙 v1/v2/v3 → AI 감성분석 → 비교·평가 (실습 TODO 11) |
| `colab/Week06_00_데이터준비_Drive저장.ipynb` | 강의자용: 수업 전 1회 실행 → Drive `강의6주/01_데이터`에 데이터 저장(MD5 확인, ZIP 포함) |
| `workbook/week06_workbook_checklist.csv` | 단계별 기대값 체크리스트 |
| `workbook/week06_labeling_sheet.csv` | 워크북 2 직접 라벨링 기록지 (R001~R020) |
| `workbook/week06_disagreement_review.csv` | 워크북 4 불일치 사례 판단 기록지 |
| `figures/` | 완성본이 만든 그림 7장 + 이론 예제 시그모이드 그림(`fig_theory_sigmoid.png`) (Notion 본문에 삽입) |
| `examples/` | 완성본 실행 결과 예시 (`week06_results.csv` 등) |
| `tools/` | 강의자용: 데이터 생성(`build_week06_data.py`), 노트북 생성·실행 검증(`build_notebooks.py`, 이론 예제 `make_theory.py` — 노트북과 노션 예제 토글을 같은 원고에서 생성) |

## Colab에서 열기
| 노트북 | 실습본 | 완성본 |
|---|---|---|
| 이론 예제 (파이썬 문법) | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week06/colab/Week06_이론예제_파이썬문법.ipynb) | – |
| 워크북 0 감성데이터 수집 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week06/colab/Week06_00_감성데이터수집_실습.ipynb) | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week06/colab/Week06_00_감성데이터수집_완성.ipynb) |
| 워크북 1~4 리뷰 감성분석 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week06/colab/Week06_리뷰감성분석_실습.ipynb) | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week06/colab/Week06_리뷰감성분석_완성.ipynb) |

열린 뒤 `파일 → Drive에 사본 저장` → `런타임 → 모두 실행`. API 키 불필요. 노트북 0장의 `DATA_SOURCE`로 GitHub / Drive / 업로드 중 데이터 위치를 고른다(기본 `"auto"`: GitHub 실패 시 Drive 자동 탐색).

## 기준 결과 (완성본 실행값)
| 방법 | 판정 비율 | 판정한 것 중 별점 일치 | 300건 전체 기준 |
|---|---|---|---|
| 규칙 v1 (단어 8+8) | 0.337 | 0.842 | 0.283 |
| 규칙 v2 (단어 확장 + 부정어) | 0.700 | 0.881 | 0.617 |
| AI (문자 2~4gram TF-IDF + 로지스틱 회귀, 학습 199,700건) | 1.000 | 0.887 | **0.887** |

워크북 0: 200,000 → 정제 195,423 → 표본 300 (MD5 `826290503dfc1ab898089886d3225ba0`). 규칙 v2 vs AI 일치 0.90(규칙 판정 210건), 정반대 21건, 별점 잡음 후보 8건, AI 애매(0.4~0.6) 16건.
전체 체크리스트: [workbook/week06_workbook_checklist.csv](workbook/week06_workbook_checklist.csv)

검증 환경: Python 3.13 · pandas 2.2.3 · scikit-learn 1.6.1 (Colab과 같은 계열). 표본 MD5는 pandas 3에서도 동일. scikit-learn 버전에 따라 AI 값이 ±0.01 정도 달라질 수 있다.

## 수정·재생성 (강의자)
```bash
python Week06/tools/build_week06_data.py            # 원자료 → 표본·MANIFEST 재생성 (시드 2026)
python Week06/tools/build_notebooks.py --execute python3   # 실습/완성 노트북 생성 + 완성본 실행, figures 갱신
```
노트북 원고는 `tools/make_wb0.py`, `tools/make_main.py` 하나에서 실습본·완성본을 함께 만든다.
