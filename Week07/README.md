# Week07 텍스트 데이터의 시각화

실제 **온라인 댓글 300건**(네이버 영화 140자평)과 **뉴스 기사 제목 350건**(연합뉴스, 7개 분야)을 단어로 나눠 세고
**빈도표·막대그래프·워드클라우드**로 시각화한 뒤, 같은 원문으로 받은 **AI 요약·키워드**를 원문 근거로 검증·비교한다.

- Notion 학습자료: https://app.notion.com/p/3f9b2e6bf8078016af44e693f897bc8a
- Google Drive 강의7주: https://drive.google.com/drive/folders/1FmWXyUDiwncwGbZ4mTBS7GDuQqJc33Ms
- 데이터 출처: [NSMC](https://github.com/e9t/nsmc) (CC0) · [KLUE-YNAT](https://github.com/KLUE-benchmark/KLUE) (CC BY-SA 4.0) — 자세한 내용 [data/DATA_SOURCES.md](data/DATA_SOURCES.md)

## 학습목표
1. 텍스트(비정형) 데이터를 단어로 나누는 방법(어절·형태소)과 불용어가 결과를 어떻게 바꾸는지 설명한다.
2. 단어 빈도를 세어 빈도표·막대그래프·워드클라우드로 시각화하고, 워드클라우드를 바르게 읽는다(크기만 의미, 문맥 손실).
3. 집단별(긍정/부정, 뉴스 분야별) 워드클라우드와 TF-IDF 특징어로 비교한다.
4. AI 요약·키워드를 근거 건수·빈도 순위·원문 대조로 검증하고, 빈도 기반 시각화와의 일치·차이·한계를 설명한다.

## 수업 흐름 (180분)
| 시간 | 내용 | 자료 |
|---|---|---|
| 0~30분 | 텍스트 데이터·토큰화(어절/형태소)·불용어·워드클라우드 읽는 법, 데이터 출처와 라이선스 | Notion 본문 |
| 30~80분 | 워크북 1 댓글 워드클라우드 (TODO 1~5) | 노트북 워크북 1 |
| 80~120분 | 워크북 2 뉴스 제목 워드클라우드·TF-IDF (TODO 6~7) | 노트북 워크북 2 |
| 120~165분 | 워크북 3 AI 요약·키워드 검증 (TODO 8~9) | 노트북 워크북 3 · 검증 기록지 |
| 165~180분 | 비교표 정리·토론·제출 안내 | 워크북 3 문서 |

## 파일 구성
| 경로 | 설명 |
|---|---|
| `data/week07_comments_300.csv` | 워크북 1 입력: 댓글 300건 (comment_id, src_id, sentiment, text) |
| `data/week07_news_350.csv` | 워크북 2 입력: 뉴스 제목 350건 (news_id, category, title, date, url, guid) |
| `data/nsmc_ratings.txt.gz` · `data/ynat_titles_all.csv.gz` | 원자료 미러 · 뉴스 제목 전체본(확장 과제용) |
| `data/week07_MANIFEST.csv` | 파일 크기·MD5·행 수 (Drive·업로드 파일 확인, Drive 폴더 자동 탐색 표식) |
| `data/DATA_SOURCES.md` | 출처·라이선스·정제 규칙·한계 |
| `colab/Week07_텍스트시각화_실습.ipynb` / `_완성.ipynb` | **워크북 1~3** (실습본 TODO 9곳, 완성본은 전체 실행·출력 포함) |
| `colab/Week07_00_유튜브댓글수집.ipynb` | 확장: YouTube Data API v3로 유튜브 댓글 수집 → 같은 형식 CSV (API 키 필요) |
| `colab/Week07_00_데이터준비_Drive저장.ipynb` | 강의자용: 수업 전 1회 실행 → Drive `강의7주/02_데이터`에 데이터 저장(MD5 확인) |
| `workbook/워크북1~3_*.md` | 워크북 안내 (단계별 기대값, 기록 항목) |
| `workbook/week07_workbook_checklist.csv` | 단계별 기대값 체크리스트 |
| `workbook/week07_ai_verification_template.csv` | 워크북 3 AI 검증 기록지 |
| `figures/` | 완성본이 만든 그림 8장 |
| `examples/` | 완성본 결과 예시 (상위30 CSV, AI 키워드 검증표, 프롬프트) |
| `tools/` | 강의자용: 데이터 생성·노트북 생성/실행 스크립트, 제외 댓글 목록 |

## Colab에서 열기
| 노트북 | 열기 |
|---|---|
| 워크북 1~3 실습본 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_텍스트시각화_실습.ipynb) |
| 워크북 1~3 완성본 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_텍스트시각화_완성.ipynb) |
| 확장: 유튜브 댓글 수집 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_00_유튜브댓글수집.ipynb) |
| 강의자: Drive 데이터 준비 | [열기](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_00_데이터준비_Drive저장.ipynb) |

열린 뒤 `파일 → Drive에 사본 저장` → `런타임 → 모두 실행` (설치 포함 약 1~2분). 워크북 1~3은 API 키가 필요 없다.
노트북 0장의 `DATA_SOURCE`로 GitHub / Drive / 업로드 중 데이터 위치를 고른다(기본 `"auto"`: GitHub 실패 시 Drive 자동 탐색).

## 기준 결과 (완성본 실행값)
| 항목 | 값 |
|---|---|
| 서로 다른 단어 수 (어절 / 형태소) | 1,768 / 659 |
| 댓글 상위 (불용어 제거) | 없다 30 · 좋다 30 · 연기 29 · 재밌다 18 · 재미있다 13 |
| 부정 댓글 '재미없다' (규칙 전 → 후) | 7 → 12 |
| 뉴스 상위 | 대통령 15 · 정부 11 · 개발 9 · 한국 8 · 이란 8 |
| AI 예시 키워드와 빈도 상위10 일치 | 댓글 1(연기) · 뉴스 1(대통령), 근거 0건 키워드 없음 |

전체 기대값: [workbook/week07_workbook_checklist.csv](workbook/week07_workbook_checklist.csv).
검증 환경: Python 3.13 · pandas 2.x · kiwipiepy 0.24.0 · wordcloud 1.9 · scikit-learn 1.9. Kiwi 버전에 따라 개수가 1~2 달라질 수 있다.

## 수정·재생성 (강의자)
```bash
python Week07/tools/build_week07_data.py                                       # 원자료 → 표본·MANIFEST (시드 2026)
python Week07/tools/build_notebooks.py --execute python3 --data-dir Week07/data   # 노트북 생성 + 완성본 실행, figures·examples 갱신
```
- 부적절한 댓글을 발견하면 `tools/week07_comment_exclude.csv`에 `src_id,사유`를 추가하고 두 명령을 다시 실행한다.
- 노트북 원고: `tools/make_main.py`(워크북 1~3), `tools/make_extra.py`(보조 노트북). 기대값 문구: `tools/expect_values.py`.
- AI 예시 답(`tools/ai_example.py`)은 데이터를 바꾸면 근거 번호가 달라지므로 다시 만들어 확인한다.
