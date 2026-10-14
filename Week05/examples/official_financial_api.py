"""공공데이터포털 금융위원회 API로 주식·지수 일별 시세를 받아 지표를 계산한다 (심화·선택).

- 주식: 금융위원회_주식시세정보  https://www.data.go.kr/data/15094808/openapi.do
- 지수: 금융위원회_지수시세정보  https://www.data.go.kr/data/15094807/openapi.do
- 인증키는 실행할 때 한 번만 입력받는다(getpass). 코드·CSV·스크린샷에 키를 남기지 않는다.
- 응답은 문자열·날짜 내림차순 → 숫자 변환·오름차순 정렬 필요.
- 지수 API의 서비스 주소는 활용가이드(docx)와 반드시 대조할 것. 응답 열 이름은 실행 후 출력으로 확인한다.

실행: python official_financial_api.py  (수업 기본 실습은 키 없이 Week05/data CSV 사용)
"""
import getpass

import numpy as np
import pandas as pd
import requests

STOCK_URL = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"
INDEX_URL = "https://apis.data.go.kr/1160100/service/GetMarketIndexInfoService/getStockMarketIndex"
COLS = {"basDt": "Date", "mkp": "Open", "hipr": "High", "lopr": "Low", "clpr": "Close", "trqu": "Volume"}


def _fetch(url, key, extra, start, end, rows=1000):
    """페이지를 넘기며 모든 item을 모은다. start·end는 'YYYYMMDD'."""
    e = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y%m%d")   # 종료일 포함 보장
    items, page = [], 1
    while True:
        params = {"serviceKey": key, "resultType": "json", "numOfRows": rows, "pageNo": page,
                  "beginBasDt": start, "endBasDt": e, **extra}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        try:
            body = r.json()["response"]["body"]
        except ValueError:
            raise RuntimeError("JSON이 아닌 응답(인증키 미등록·오타 가능): " + r.text[:200])
        got = body["items"]["item"] if body.get("items") else []
        items += got if isinstance(got, list) else [got]
        if page * rows >= int(body.get("totalCount", 0)):
            break
        page += 1
    return pd.DataFrame(items)


def fetch_stock(code, start, end, key):
    raw = _fetch(STOCK_URL, key, {"likeSrtnCd": code}, start, end)
    if not raw.empty:
        raw = raw[raw["srtnCd"].astype(str).str.zfill(6) == code]
    return raw


def fetch_index(name, start, end, key):
    """name 예: '코스피', '코스닥'. 비슷한 이름의 지수가 여러 개면 idxNm이 정확히 같은 행만 남긴다."""
    raw = _fetch(INDEX_URL, key, {"idxNm": name}, start, end)
    if not raw.empty and "idxNm" in raw:
        raw = raw[raw["idxNm"] == name]
    return raw


def clean(raw, end):
    d = raw.rename(columns=COLS)[[c for c in COLS.values() if c in raw.rename(columns=COLS)]].copy()
    d["Date"] = pd.to_datetime(d["Date"], format="%Y%m%d", errors="coerce")
    for c in d.columns.drop("Date"):
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", ""), errors="coerce")
    d = d.dropna(subset=["Date", "Close"]).drop_duplicates("Date").sort_values("Date")
    return d[d["Date"] <= pd.Timestamp(end)].reset_index(drop=True)


def compute(d):
    d = d.copy()
    d["ReturnPct"] = d["Close"].pct_change() * 100
    d["SMA5"] = d["Close"].rolling(5, min_periods=5).mean()
    d["SMA20"] = d["Close"].rolling(20, min_periods=20).mean()
    diff = d["Close"].diff()
    gain = diff.clip(lower=0).rolling(14, min_periods=14).mean()
    loss = (-diff.clip(upper=0)).rolling(14, min_periods=14).mean()
    d["RSI14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    d.loc[(loss == 0) & (gain > 0), "RSI14"] = 100
    d.loc[(loss == 0) & (gain == 0), "RSI14"] = 50
    d["Vol20Pct"] = d["ReturnPct"].rolling(20, min_periods=20).std()
    return d


if __name__ == "__main__":
    START, END = "20250101", "20251231"
    key = getpass.getpass("공공데이터포털 인증키(Decoding): ")       # 한 번만 입력
    for code in ["005930", "000660", "005380"]:
        raw = fetch_stock(code, START, END, key)
        if raw.empty:
            print(code, "결과 없음: 인증키 승인 여부·종목코드·기간을 확인")
            continue
        raw.to_csv(f"official_raw_{code}.csv", index=False, encoding="utf-8-sig")
        out = compute(clean(raw, END))
        out.to_csv(f"official_indicators_{code}.csv", index=False, encoding="utf-8-sig")
        print(code, len(out), "행\n", out.tail(1)[["Date", "Close", "SMA5", "SMA20", "RSI14", "Vol20Pct"]])
    for name in ["코스피", "코스닥"]:
        raw = fetch_index(name, START, END, key)
        print(name, "응답 열:", list(raw.columns))
        if not raw.empty:
            raw.to_csv(f"official_index_raw_{name}.csv", index=False, encoding="utf-8-sig")
