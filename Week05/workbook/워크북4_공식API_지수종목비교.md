# 워크북4: 시장 지수(KOSPI·KOSDAQ)와 개별 종목 수익률 비교

- 노트북: `colab/Week05_Workbook4_지수종목비교_실습.ipynb` (TODO 3곳) / `_완성.ipynb` (실행 검증 완료)
- 데이터(키 불필요): `data/krx_daily_{005930,000660,005380}.csv`, `data/kospi_daily.csv`, `data/kosdaq_daily.csv` — 모두 KRX 실제 일별 자료, 2025-01-02 ~ 2026-10-13
- 공식 API로 직접 수집(심화): `colab/Week05_데이터수집_API가이드.ipynb` 방법 C, `examples/official_financial_api.py`
  - 금융위원회 주식시세: https://www.data.go.kr/data/15094808/openapi.do
  - 금융위원회 지수시세: https://www.data.go.kr/data/15094807/openapi.do
  - KRX Open API: https://openapi.krx.co.kr/contents/OPP/INFO/service/OPPINFO004.cmd

## 학습 순서
1. 종목 3개 + 지수 2개 불러오기 → 날짜·수치형 변환, 오름차순 정렬
2. 공통 거래일 기준 결합(`join="inner"`) → 일간 수익률
3. 비교표: 평균·표준편차·연율화 변동성·누적수익률·상승일 비율·KOSPI 상관계수·베타
4. 시각화: 기준 100 가격지수(로그축), 60일 이동 상관계수
5. 통계표만으로 AI 요약 → 숫자 검증, 표 밖 정보·인과·추천 표현 판정

## 기대값 (완성본)
| 항목 | 삼성전자 | SK하이닉스 | 현대차 | KOSPI | KOSDAQ |
|---|---|---|---|---|---|
| 공통 거래일 / 수익률 일수 | 431 / 430 | | | | |
| 기간 누적수익률% | 334.5 | 742.9 | 48.9 | 151.6 | 21.9 |

나머지 값(상관계수·베타 등)은 완성본 출력과 대조한다.

## 주의
- API 인증키는 노트북·CSV·스크린샷에 남기지 않는다(Colab 보안 비밀 또는 getpass).
- 베타·상관계수는 **과거 관측값**이며 미래 수익을 말해 주지 않는다. 매매 추천 금지.
- 실제 원자료 / 내가 계산한 값 / AI 요약을 구분해 표기한다.
