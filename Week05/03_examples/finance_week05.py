import pandas as pd
def indicators(df):
    """Date/Close 열이 있는 OHLCV DataFrame을 받아 기술지표를 계산한다."""
    d=df.copy()
    d["Date"]=pd.to_datetime(d["Date"],errors="coerce")
    d["Close"]=pd.to_numeric(d["Close"],errors="coerce")
    d=d.dropna(subset=["Date","Close"]).drop_duplicates("Date").sort_values("Date")
    d["ReturnPct"]=d["Close"].pct_change()*100
    d["SMA5"]=d["Close"].rolling(5).mean()
    d["SMA20"]=d["Close"].rolling(20).mean()
    diff=d["Close"].diff()
    gain=diff.clip(lower=0).rolling(14).mean()
    loss=(-diff.clip(upper=0)).rolling(14).mean()
    rs=gain/loss.replace(0,float("nan"))
    d["RSI14"]=100-100/(1+rs)
    d.loc[(loss==0)&(gain>0),"RSI14"]=100
    d.loc[(loss==0)&(gain==0),"RSI14"]=50
    d["Vol20Pct"]=d["ReturnPct"].rolling(20).std()
    return d

if __name__=="__main__":
    import FinanceDataReader as fdr
    for code in ("005930","000660","005380"):
        df=fdr.DataReader("NAVER:"+code,"2025-01-01","2025-12-31").reset_index()
        output=indicators(df)
        output.to_csv(code+"_2025_indicators.csv",index=False,encoding="utf-8-sig")
        print(code,output.tail(1)[["Date","Close","SMA5","SMA20","RSI14","Vol20Pct"]])
