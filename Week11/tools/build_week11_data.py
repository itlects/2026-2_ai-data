"""11주차 실습 데이터 만들기.

기상청 기상자료개방포털 ASOS 시간자료(대구 143, 2021~2025, CP949) 5개 파일을
한 파일로 이어 붙이고 UTF-8로 저장한다. 값은 바꾸지 않는다(인코딩·결합만).

python tools/build_week11_data.py → data/daegu_asos_hourly_2021_2025.csv
"""
from pathlib import Path
import hashlib

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "data" / "original"
OUT = ROOT / "data" / "daegu_asos_hourly_2021_2025.csv"

frames = [pd.read_csv(f, encoding="cp949", dtype=str) for f in sorted(ORIG.glob("OBS_ASOS_TIM_*.csv"))]
df = pd.concat(frames, ignore_index=True)
assert df["지점"].eq("143").all()
assert df["일시"].is_unique
df = df.sort_values("일시")
df.to_csv(OUT, index=False, encoding="utf-8")
print(OUT.name, df.shape, hashlib.md5(OUT.read_bytes()).hexdigest())
