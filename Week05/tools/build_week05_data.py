"""Week05 실습 데이터 재생성 스크립트 (강의자용)

KRX 일별 전종목 시세를 매일 GitHub에 공개하는 FinanceData/marcap 저장소에서
수업 대상 종목만 추출해 Week05/data/ 아래 CSV로 저장한다.

사용법 (저장소 루트에서):
    git clone --depth 1 https://github.com/FinanceData/marcap.git /tmp/marcap
    pip install pandas pyarrow finance-datareader
    python Week05/tools/build_week05_data.py /tmp/marcap 2025-01-01 2026-10-13

- 학생은 이 스크립트를 실행할 필요가 없다. 완성된 CSV를 GitHub raw URL로 바로 읽는다.
- 학기 중 최신 데이터로 갱신하고 싶을 때만 강의자가 다시 실행한다.
"""
import sys
from pathlib import Path

import pandas as pd

STOCKS = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차"}
OUT = Path(__file__).resolve().parents[1] / "data"


def load_marcap(marcap_dir: str, start: str, end: str) -> pd.DataFrame:
    years = range(int(start[:4]), int(end[:4]) + 1)
    frames = [pd.read_parquet(Path(marcap_dir) / "data" / f"marcap-{y}.parquet") for y in years]
    df = pd.concat(frames, ignore_index=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df[(df["Date"] >= start) & (df["Date"] <= end) & df["Code"].isin(STOCKS)].copy()


def main(marcap_dir: str, start: str, end: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_marcap(marcap_dir, start, end).sort_values(["Code", "Date"])
    int_cols = ["Open", "High", "Low", "Close", "Volume", "Amount", "Changes", "Marcap", "Stocks"]
    df[int_cols] = df[int_cols].round().astype("int64")

    # 1) 종목별 정제본 (워크북2·3 입력)
    cols = ["Date", "Code", "Name", "Open", "High", "Low", "Close", "Volume",
            "Amount", "Changes", "ChangesRatio", "Marcap", "Stocks", "Market"]
    for code in STOCKS:
        part = df[df["Code"] == code][cols].copy()
        part["Date"] = part["Date"].dt.strftime("%Y-%m-%d")
        part.to_csv(OUT / f"krx_daily_{code}.csv", index=False, encoding="utf-8-sig")

    # 2) 원본 형태 (워크북1 전처리 입력): KRX 정보데이터시스템 '전종목 시세' 다운로드 열 이름,
    #    최신일이 위에 오는 내림차순, 날짜 'YYYY/MM/DD' 문자열 — 실제 값은 그대로
    raw = df.sort_values(["Date", "Code"], ascending=[False, True]).copy()
    raw = pd.DataFrame({
        "일자": raw["Date"].dt.strftime("%Y/%m/%d"),
        "종목코드": raw["Code"], "종목명": raw["Name"], "시장구분": raw["Market"],
        "종가": raw["Close"], "대비": raw["Changes"], "등락률": raw["ChangesRatio"].round(2),
        "시가": raw["Open"], "고가": raw["High"], "저가": raw["Low"],
        "거래량": raw["Volume"], "거래대금": raw["Amount"],
        "시가총액": raw["Marcap"], "상장주식수": raw["Stocks"],
    })
    raw.to_csv(OUT / "krx_daily_3stocks_raw_ko.csv", index=False, encoding="utf-8-sig")

    # 3) KOSPI 지수 (비교 기준선) — FinanceDataReader의 GitHub 캐시
    try:
        import FinanceDataReader as fdr
        k = fdr.DataReader("KS11", start, end).reset_index()
        k = k[["Date", "Open", "High", "Low", "Close", "Volume", "Amount"]]
        k["Date"] = pd.to_datetime(k["Date"]).dt.strftime("%Y-%m-%d")
        k.to_csv(OUT / "kospi_daily.csv", index=False, encoding="utf-8-sig")
    except Exception as e:  # 지수는 선택 자료
        print("KOSPI 다운로드 실패:", e)

    print(df.groupby("Code")["Date"].agg(["min", "max", "count"]))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
