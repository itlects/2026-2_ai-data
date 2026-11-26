"""13주차 실습 데이터: 11주차 대구 ASOS 시간자료 → 2025년 일자료 365행.

python tools/build_week13_data.py → data/daegu_2025_daily.csv
"""
from pathlib import Path
import hashlib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "Week11" / "data" / "daegu_asos_hourly_2021_2025.csv"
OUT = ROOT / "data" / "daegu_2025_daily.csv"

h = pd.read_csv(SRC, parse_dates=["일시"])
h = h[h["일시"].dt.year == 2025].copy()
h["날짜"] = h["일시"].dt.strftime("%Y-%m-%d")
h["강수량(mm)"] = h["강수량(mm)"].fillna(0)          # 빈칸 = 강수 기록 없음
d = (h.groupby("날짜")
       .agg(평균기온=("기온(°C)", "mean"), 최고기온=("기온(°C)", "max"),
            최저기온=("기온(°C)", "min"), 일강수량=("강수량(mm)", "sum"),
            관측수=("기온(°C)", "count"))
       .round(1).reset_index())
assert len(d) == 365 and (d["관측수"] == 24).all()
d = d.drop(columns="관측수")
OUT.parent.mkdir(exist_ok=True)
d.to_csv(OUT, index=False, encoding="utf-8")
print(OUT.name, d.shape, hashlib.md5(OUT.read_bytes()).hexdigest())
