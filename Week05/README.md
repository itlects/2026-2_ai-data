# Week05 금융 데이터의 가공 및 분석

국내 주요 종목(삼성전자·SK하이닉스·현대차)의 **실제 한국거래소(KRX) 일별 시세**로 수익률·이동평균·RSI·볼린저밴드·변동성을 직접 계산하고(전통적 기술적 분석), 같은 지표표로 만든 **AI 보조 요약**의 숫자·표현을 검증한다.

> 교육용 데이터 분석이며 매매 추천이 아니다. 데이터 출처: 한국거래소(KRX).

- Notion 학습자료: https://app.notion.com/p/3f9b2e6bf807800c89ffc7306a229398
- Google Drive 강의5주: https://drive.google.com/drive/folders/1VDunJ-H3To8gkKTsf_gFDICUbECQuEZj

## 학습목표
1. 금융 시세 데이터의 출처·기준일·가격 유형(수정주가 여부)을 기록하고 여러 경로로 확보할 수 있다.
2. KRX 다운로드 형식 원본을 정렬·형 변환·품질 점검해 분석용 데이터로 만든다.
3. 일간·누적 수익률, SMA5/20/60, RSI14(단순/Wilder), 볼린저밴드, 20일 변동성, MDD를 계산·시각화한다.
4. 같은 지표표로 받은 AI 요약에서 숫자 오류, 표 밖 정보(환각), 예측·추천 표현을 찾아낸다.

## 파일 구성
| 경로 | 설명 |
|---|---|
| `data/krx_daily_3stocks_raw_ko.csv` | 워크북1 입력 · KRX 다운로드 형식(한글 열, 내림차순) · 1,293행 |
| `data/krx_daily_{005930,000660,005380}.csv` | 종목별 정제본 · 각 431거래일 (2025-01-02 ~ 2026-10-13) |
| `data/kospi_daily.csv`, `data/kosdaq_daily.csv` | KOSPI·KOSDAQ 지수 일별 (시장 비교 기준선, 워크북4) |
| `data/week05_MANIFEST.csv` | 파일 목록·크기·MD5·행 수 (Drive·업로드 데이터가 원본과 같은지 확인, Drive 폴더 자동 탐색 표식) |
| `data/DATA_SOURCES.md` | 출처·점검 결과·사용 조건·직접 수집 방법 비교 |
| `colab/Week05_00_데이터준비_Drive저장.ipynb` | 강의자용: 수업 전 1회 실행 → Drive `강의5주/02_데이터`에 실습 데이터 저장(MD5 확인, ZIP 포함) |
| `colab/Week05_Finance_Data_Analysis_실습.ipynb` | 학생용 (TODO 8곳 채우기, 단계별 기대값 제공) |
| `colab/Week05_Finance_Data_Analysis_완성.ipynb` | 완성본 (전체 실행 검증 완료, 출력 포함) |
| `colab/Week05_Workbook4_지수종목비교_실습.ipynb` / `_완성.ipynb` | 워크북4: KOSPI·KOSDAQ 지수와 종목 수익률·상관계수·베타 비교 |
| `colab/Week05_데이터수집_API가이드.ipynb` | 심화: FinanceDataReader · 공공데이터포털(주식·지수) · KRX Open API 수집 |
| `examples/finance_week05.py` | 노트북 함수 모음 (전처리·지표·AI 숫자 검증) |
| `examples/official_financial_api.py` | 공공데이터포털 주식·지수 API 수집 스크립트 (인증키 필요) |
| `workbook/워크북4_공식API_지수종목비교.md` | 워크북4 안내·기대값 |
| `workbook/week05_workbook_checklist.csv` | 단계별 체크리스트 (기대값 포함) |
| `workbook/week05_result_table_template.csv` | 워크북2 결과표 양식 |
| `workbook/week05_ai_verification_template.csv` | 워크북3 AI 검증표 양식 |
| `workbook/week05_ai_prompt.txt` | AI 프롬프트(강한/약한) |
| `figures/` | 완성본이 생성한 그림 (종목별 지표, 누적수익률, 위험) |
| `tools/build_week05_data.py` | 강의자용: 최신 데이터로 CSV 재생성 |

## Colab에서 열기
- 실습본: https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week05/colab/Week05_Finance_Data_Analysis_실습.ipynb
- 완성본: https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week05/colab/Week05_Finance_Data_Analysis_완성.ipynb
- 워크북4 실습본: https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week05/colab/Week05_Workbook4_지수종목비교_실습.ipynb
- API 가이드: https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week05/colab/Week05_데이터수집_API가이드.ipynb

열린 뒤 `파일 → Drive에 사본 저장` 후 `런타임 → 모두 실행`.

## 수업 중 데이터 위치 선택 (GitHub / Google Drive / 업로드)
모든 실습 노트북 0장의 `DATA_SOURCE` 한 줄로 고른다. 어느 경로든 MD5가 같은 파일이므로 기대값이 똑같다.

| 값 | 동작 | 쓰는 상황 |
|---|---|---|
| `"auto"` (기본) | GitHub에서 읽고, 실패하면 내 Drive에서 `week05_MANIFEST.csv`가 있는 폴더를 자동으로 찾음 | 평소 |
| `"drive"` | 내 Drive에 미리 저장한 데이터만 사용 | 수업 중 GitHub 불안정 / 사전 다운로드 데이터로만 진행 |
| `"upload"` | 내려받아 둔 CSV를 직접 업로드 | Drive 연결이 어려운 학생 |
| `"github"` | GitHub만 사용 | 원본 확인 |

**준비 (강의자, 수업 전 1회):** `colab/Week05_00_데이터준비_Drive저장.ipynb` 실행 → Drive `강의5주/02_데이터`에 CSV 6개 + `week05_MANIFEST.csv` + `DATA_SOURCES.md` + `week05_data.zip` 저장.
**학생:** 공유받은 `02_데이터` 폴더를 오른쪽 클릭 → 정리 → **바로가기 추가 → 내 드라이브** → 노트북에서 `DATA_SOURCE = "drive"`.

## 데이터 받기
- **방법 A (기본, 키 불필요)** — 노트북이 GitHub에서 바로 읽음
  ```python
  BASE = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week05/data/"
  raw = pd.read_csv(BASE + "krx_daily_3stocks_raw_ko.csv", dtype={"종목코드": str})
  ```
- **방법 B** — `fdr.DataReader("005930", "2025-01-01")` (네이버 경유, 접속 제한 시 실패 가능)
- **방법 C** — 공공데이터포털 [금융위원회_주식시세정보](https://www.data.go.kr/data/15094808/openapi.do) (서비스키, 전 영업일까지)
- **방법 D** — [KRX Open API](http://openapi.krx.co.kr) `sto/stk_bydd_trd` (AUTH_KEY, 서비스별 이용신청)
- **방법 E** — [네이버 금융 일별 시세](https://finance.naver.com/item/sise_day.naver?code=005930) 화면으로 몇 개 값 교차검증 (스크래핑 금지)
- 방법 C·D는 `colab/Week05_데이터수집_API가이드.ipynb`에 키 발급 절차와 코드가 있다.

## 기준 결과 (완성 노트북, 기준일 2026-10-13)
| 종목 | 종가 | SMA5 | SMA20 | RSI14(단순) | RSI14(Wilder) | Vol20Pct | 기간 누적수익률 | MDD |
|---|---|---|---|---|---|---|---|---|
| 삼성전자 | 232,000 | 257,000 | 263,850 | 40.4 | 34.4 | 3.20 | 334.5% | −42.9% |
| SK하이닉스 | 1,443,000 | 1,645,000 | 1,759,550 | 29.7 | 31.4 | 3.74 | 742.9% | −54.7% |
| 현대차 | 315,000 | 328,700 | 353,075 | 14.7 | 21.9 | 1.34 | 48.9% | −58.0% |
| KOSPI 지수 | 6,035.35 | – | – | – | – | – | 151.6% | −38.6% |
| KOSDAQ 지수 | 837.03 | – | – | – | – | – | 21.9% | – |

워크북4 (공통 430일 수익률): KOSPI 대비 베타 삼성전자 1.29 · SK하이닉스 1.58 · 현대차 0.80, 상관계수 0.91 · 0.89 · 0.62.

원본 1,293행 → 정제 1,293행 (결측·중복·OHLC 논리오류·거래량0 모두 0건, 원본은 내림차순이라 정렬 필요).

## 데이터 갱신 (강의자)
```bash
git clone --depth 1 https://github.com/FinanceData/marcap.git /tmp/marcap
pip install pandas pyarrow finance-datareader
python Week05/tools/build_week05_data.py /tmp/marcap 2025-01-01 <종료일>
```
갱신하면 기준일과 기대값이 바뀌므로 완성본을 다시 실행하고 체크리스트 기대값을 고친다.

## 출처
- 한국거래소 정보데이터시스템 전종목 시세 (http://data.krx.co.kr), 정리본: [FinanceData/marcap](https://github.com/FinanceData/marcap)
- KOSPI 지수: [FinanceDataReader](https://github.com/FinanceData/FinanceDataReader) `KS11`
