"""Week05 금융 데이터의 가공 및 분석 — 공용 함수 모음

Colab에서 사용:
    !wget -q https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week05/examples/finance_week05.py
    import finance_week05 as fw

노트북은 이 파일 없이도 실행되도록 같은 코드를 셀 안에 담고 있다.
이 파일은 (1) 노트북 코드의 정답 기준, (2) 과제에서 재사용할 함수 묶음이다.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

BASE_URL = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week05/data/"
STOCKS = {"005930": "삼성전자", "000660": "SK하이닉스", "005380": "현대차"}

KO2EN = {"일자": "Date", "종목코드": "Code", "종목명": "Name", "시장구분": "Market",
         "종가": "Close", "대비": "Changes", "등락률": "ChangesRatio", "시가": "Open",
         "고가": "High", "저가": "Low", "거래량": "Volume", "거래대금": "Amount",
         "시가총액": "Marcap", "상장주식수": "Stocks"}
PRICE_COLS = ["Open", "High", "Low", "Close", "Volume"]


# ---------------------------------------------------------------- 1. 수집·전처리
def load_stock(code: str, base: str = BASE_URL) -> pd.DataFrame:
    """정제된 종목별 CSV를 읽는다. 종목코드는 문자열로 읽어야 앞자리 0이 보존된다."""
    df = pd.read_csv(f"{base}krx_daily_{code}.csv", dtype={"Code": str}, parse_dates=["Date"])
    return df.sort_values("Date").reset_index(drop=True)


def clean_raw_ko(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """KRX 다운로드 형태(한글 열·내림차순·문자열 날짜)를 분석용 형태로 바꾼다.

    반환: (정제된 DataFrame, 점검 보고 dict)
    """
    report = {"원본_행수": len(raw)}
    df = raw.rename(columns=KO2EN).copy()
    df["Code"] = df["Code"].astype(str).str.zfill(6)          # 5930 → 005930
    df["Date"] = pd.to_datetime(df["Date"], format="%Y/%m/%d", errors="coerce")
    for c in PRICE_COLS + ["Amount", "Changes", "ChangesRatio", "Marcap", "Stocks"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    report["날짜_변환실패"] = int(df["Date"].isna().sum())
    report["가격_결측"] = int(df[PRICE_COLS].isna().any(axis=1).sum())
    report["중복(종목+일자)"] = int(df.duplicated(["Code", "Date"]).sum())
    # OHLC 논리 검사: 고가는 시가·종가·저가 이상, 저가는 시가·종가 이하
    bad = (df["High"] < df[["Open", "Close", "Low"]].max(axis=1)) | \
          (df["Low"] > df[["Open", "Close"]].min(axis=1))
    report["OHLC_논리오류"] = int(bad.sum())
    report["거래량0"] = int((df["Volume"] == 0).sum())
    df = (df.dropna(subset=["Date", "Close"])
            .drop_duplicates(["Code", "Date"])
            .sort_values(["Code", "Date"])           # 시계열 계산 전 반드시 오름차순
            .reset_index(drop=True))
    report["정제후_행수"] = len(df)
    return df, report


# ---------------------------------------------------------------- 2. 기술적 지표
def rsi(close: pd.Series, n: int = 14, method: str = "sma") -> pd.Series:
    """RSI. method='sma' 단순이동평균(수업 기본), 'wilder' 지수평활(HTS 다수 방식)."""
    delta = close.diff()
    gain, loss = delta.clip(lower=0), -delta.clip(upper=0)
    if method == "wilder":
        avg_g = gain.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
        avg_l = loss.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    else:
        avg_g = gain.rolling(n, min_periods=n).mean()
        avg_l = loss.rolling(n, min_periods=n).mean()
    out = 100 - 100 / (1 + avg_g / avg_l.replace(0, np.nan))
    out[(avg_l == 0) & (avg_g > 0)] = 100.0
    out[(avg_l == 0) & (avg_g == 0)] = 50.0
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """단일 종목(날짜 오름차순) DataFrame에 수익률·이동평균·RSI·변동성 등을 추가한다."""
    d = df.sort_values("Date").copy()
    c = d["Close"]
    d["ReturnPct"] = c.pct_change() * 100                      # 일간 수익률(%)
    d["CumReturnPct"] = (c / c.iloc[0] - 1) * 100              # 기간 누적수익률(%)
    for n in (5, 20, 60):
        d[f"SMA{n}"] = c.rolling(n, min_periods=n).mean()
    # 골든/데드 크로스: SMA5가 SMA20을 위/아래로 '뚫는' 날
    above = (d["SMA5"] > d["SMA20"]).astype("float").where(d["SMA20"].notna())
    d["Cross"] = np.select([(above == 1) & (above.shift() == 0), (above == 0) & (above.shift() == 1)],
                           ["golden", "dead"], default="")
    d["RSI14"] = rsi(c, 14, "sma")
    d["RSI14_Wilder"] = rsi(c, 14, "wilder")
    mid, sd = c.rolling(20, min_periods=20).mean(), c.rolling(20, min_periods=20).std()
    d["BB_Upper"], d["BB_Lower"] = mid + 2 * sd, mid - 2 * sd   # 볼린저밴드(20, 2σ)
    d["Vol20Pct"] = d["ReturnPct"].rolling(20, min_periods=20).std()   # 20일 일간 변동성(%p)
    d["Vol20AnnPct"] = d["Vol20Pct"] * np.sqrt(252)                    # 연율화(참고)
    d["DrawdownPct"] = (c / c.cummax() - 1) * 100              # 고점 대비 하락률(%)
    return d


def period_stats(d: pd.DataFrame) -> dict:
    """기간 요약 통계 (지표가 추가된 단일 종목 DataFrame)."""
    r = d["ReturnPct"].dropna()
    return {
        "시작일": d["Date"].iloc[0].date(), "종료일": d["Date"].iloc[-1].date(),
        "거래일수": len(d), "시작종가": int(d["Close"].iloc[0]), "종료종가": int(d["Close"].iloc[-1]),
        "누적수익률%": round(float(d["CumReturnPct"].iloc[-1]), 2),
        "일간수익률_평균%": round(float(r.mean()), 3), "일간수익률_표준편차%": round(float(r.std()), 3),
        "연율화변동성%": round(float(r.std() * np.sqrt(252)), 1),
        "최대낙폭MDD%": round(float(d["DrawdownPct"].min()), 2),
        "상승일비율%": round(float((r > 0).mean() * 100), 1),
        "골든크로스": int((d["Cross"] == "golden").sum()), "데드크로스": int((d["Cross"] == "dead").sum()),
    }


# ---------------------------------------------------------------- 3. 규칙 기반 해석 & AI 검증
def rule_facts(row: pd.Series) -> dict:
    """기준일 한 행으로 '데이터로 확인 가능한 사실'만 문장으로 만든다(전통적 기술적 분석)."""
    f = {}
    f["이동평균"] = ("SMA5가 SMA20보다 높다(단기 평균 > 중기 평균)" if row["SMA5"] > row["SMA20"]
                 else "SMA5가 SMA20보다 낮다(단기 평균 < 중기 평균)")
    f["종가위치"] = ("종가가 SMA20 위에 있다" if row["Close"] > row["SMA20"] else "종가가 SMA20 아래에 있다")
    r = row["RSI14"]
    f["RSI"] = (f"RSI14={r:.1f}, 70 이상(상대적 과열 구간)" if r >= 70 else
               f"RSI14={r:.1f}, 30 이하(상대적 침체 구간)" if r <= 30 else
               f"RSI14={r:.1f}, 30~70 중립 구간")
    f["볼린저"] = ("종가가 상단 밴드 위" if row["Close"] > row["BB_Upper"] else
                "종가가 하단 밴드 아래" if row["Close"] < row["BB_Lower"] else "종가가 밴드 안")
    f["변동성"] = f"20일 일간 변동성 {row['Vol20Pct']:.2f}%p"
    return f


def latest_table(frames: dict[str, pd.DataFrame], date: str | None = None) -> pd.DataFrame:
    """종목별 기준일 지표표. AI에게 줄 '근거 표'이자 워크북2 결과표."""
    rows = []
    for name, d in frames.items():
        x = d[d["Date"] <= pd.Timestamp(date)] if date else d
        last = x.iloc[-1]
        rows.append({"종목": name, "기준일": last["Date"].strftime("%Y-%m-%d"),
                     "종가": int(last["Close"]), "일간수익률%": round(float(last["ReturnPct"]), 2),
                     "SMA5": int(round(last["SMA5"])), "SMA20": int(round(last["SMA20"])),
                     "RSI14": round(float(last["RSI14"]), 1), "Vol20Pct": round(float(last["Vol20Pct"]), 2),
                     "BB_Upper": int(round(last["BB_Upper"])), "BB_Lower": int(round(last["BB_Lower"]))})
    t = pd.DataFrame(rows)
    t["변동성순위"] = t["Vol20Pct"].rank(ascending=False).astype(int)
    return t


PROMPT_TEMPLATE = """아래는 {date} 기준 국내 주식 3종목의 기술적 지표 표입니다(출처: 한국거래소 일별 시세로 직접 계산).
규칙:
1) 표에 있는 숫자만 사용하세요. 실적, 뉴스, 수급(외국인·기관), 전망, 목표주가는 쓰지 마세요.
2) 종목별로 (1) SMA5와 SMA20 비교, (2) RSI14 위치(30 이하/30~70/70 이상), (3) 3종목 중 변동성 순위, (4) 이 표만으로는 알 수 없는 점 을 각각 한 문장으로 쓰세요.
3) 각 문장 끝에 근거가 된 열 이름을 [열이름] 형태로 붙이세요.
4) 표로 확인할 수 없는 내용은 '확인 불가'라고 쓰세요. 매수·매도 추천은 하지 마세요.

표:
{table}
"""


def build_prompt(table: pd.DataFrame) -> str:
    cols = ["종목", "기준일", "종가", "일간수익률%", "SMA5", "SMA20", "RSI14", "Vol20Pct", "BB_Upper", "BB_Lower"]
    try:
        body = table[cols].to_markdown(index=False)      # tabulate 필요(Colab 기본 설치)
    except ImportError:
        body = table[cols].to_csv(index=False)
    return PROMPT_TEMPLATE.format(date=table["기준일"].iloc[0], table=body)


def check_numbers(ai_text: str, table: pd.DataFrame, tol: float = 0.01) -> pd.DataFrame:
    """AI 응답에 등장한 숫자가 근거 표의 값과 일치하는지 자동 점검한다(환각 1차 탐지).

    - 쉼표 제거 후 모든 숫자를 추출, 표의 모든 수치와 상대오차 tol 이내면 '표에 있음'
    - 30, 70 같은 기준값과 1~3 순위, 14·20·5 같은 기간 숫자는 '기준/기간 숫자'로 분류
    """
    vals = pd.to_numeric(table.select_dtypes("number").stack(), errors="coerce").dropna().values
    allowed = {5, 14, 20, 30, 60, 70, 1, 2, 3, 4}
    out = []
    for tok in re.findall(r"(?<![A-Za-z\d.])-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?", ai_text):
        v = float(tok.replace(",", ""))
        if v in allowed:
            status = "기준/기간 숫자"
        elif np.any(np.isclose(vals, v, rtol=tol, atol=0.051)):
            status = "표에 있음"
        else:
            status = "표에 없음 → 직접 확인"
        out.append({"AI가 쓴 숫자": tok, "판정": status})
    return pd.DataFrame(out).drop_duplicates()


if __name__ == "__main__":
    frames = {n: add_indicators(load_stock(c)) for c, n in STOCKS.items()}
    t = latest_table(frames)
    print(t.to_string(index=False))
    for n, d in frames.items():
        print(n, period_stats(d))
