import getpass
import requests
import pandas as pd
import numpy as np

BASE="https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService/getStockPriceInfo"

def fetch_stock(code, start="20250101", end="20251231"):
    key=getpass.getpass("공공데이터포털 API 키: ")
    rows=[]
    for page in range(1,101):
        params={"serviceKey":key,"resultType":"json","pageNo":page,"numOfRows":1000,
                "likeSrtnCd":code,"beginBasDt":start,"endBasDt":end}
        response=requests.get(BASE,params=params,timeout=30)
        response.raise_for_status()
        payload=response.json()["response"]["body"]
        items=payload.get("items",{}).get("item",[])
        if isinstance(items,dict):items=[items]
        rows += [v for v in items if str(v.get("srtnCd"))==code]
        if len(items)<1000:break
    return pd.DataFrame(rows)

def compute(df):
    d=df.rename(columns={"basDt":"Date","clpr":"Close","mkp":"Open",
                          "hipr":"High","lopr":"Low","trqu":"Volume"}).copy()
    d["Date"]=pd.to_datetime(d["Date"],format="%Y%m%d",errors="coerce")
    for col in ["Open","High","Low","Close","Volume"]:
        d[col]=pd.to_numeric(d[col],errors="coerce")
    d=d.dropna(subset=["Date","Close"]).drop_duplicates("Date").sort_values("Date")
    d["ReturnPct"]=d["Close"].pct_change()*100
    d["SMA5"]=d["Close"].rolling(5).mean()
    d["SMA20"]=d["Close"].rolling(20).mean()
    diff=d["Close"].diff()
    gain=diff.clip(lower=0).rolling(14).mean()
    loss=(-diff.clip(upper=0)).rolling(14).mean()
    ratio=gain/loss.replace(0,np.nan)
    d["RSI14"]=100-100/(1+ratio)
    d.loc[(loss==0)&(gain>0),"RSI14"]=100
    d.loc[(loss==0)&(gain==0),"RSI14"]=50
    d["Vol20Pct"]=d["ReturnPct"].rolling(20).std()
    return d

if __name__=="__main__":
    for ticker in ["005930","000660","005380"]:
        raw=fetch_stock(ticker)
        if raw.empty:
            print(ticker,"No records. Check key, parameter names and date range.")
            continue
        raw.to_csv("official_raw_"+ticker+".csv",index=False,encoding="utf-8-sig")
        computed=compute(raw)
        computed.to_csv("official_indicators_"+ticker+".csv",index=False,encoding="utf-8-sig")
        print(ticker,computed.tail(1)[["Date","Close","SMA5","SMA20","RSI14","Vol20Pct"]])
