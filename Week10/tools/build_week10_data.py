"""10주차 실습 데이터 준비 (강의자 1회 실행용).

원본(data/original)은 서울 열린데이터광장·공공데이터포털에서 받은 파일을 그대로 둔다.
학생용 CSV는 Colab에서 바로 읽도록 인코딩만 UTF-8(BOM)로 바꾸고 값·열 이름은 바꾸지 않는다.

실행: python tools/build_week10_data.py   (Week10 폴더에서)
"""
from pathlib import Path
import hashlib
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ORG = ROOT / "data" / "original"
OUT = ROOT / "data"


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


# 1) 시간대별 승하차 (OA-12252, 2026년 9월, 원본 CP949)
hourly = pd.read_csv(ORG / "서울시 지하철 호선별 역별 시간대별 승하차 인원 정보_202609.csv", encoding="cp949")
assert hourly.shape == (621, 52), hourly.shape
assert hourly["사용월"].unique().tolist() == [202609]
assert not hourly.isna().any().any()
assert not hourly.duplicated(["호선명", "지하철역"]).any()
hourly.to_csv(OUT / "subway_hourly_202609.csv", index=False, encoding="utf-8-sig")

# 2) 서울교통공사 지하철 혼잡도 (2025-03-31 기준 파일, 30분 단위, %)
cong = pd.read_excel(ORG / "서울교통공사_지하철혼잡도정보_20250331.xlsx", sheet_name=0)
assert cong.shape == (1662, 45), cong.shape
cong.to_csv(OUT / "subway_congestion_20250331.csv", index=False, encoding="utf-8-sig")

# 3) 서울 실시간 도시데이터 121장소 목록
places = pd.read_excel(ORG / "서울시 주요 121장소 목록.xlsx")
assert places.shape == (121, 5)
places.to_csv(OUT / "citydata_places_121.csv", index=False, encoding="utf-8-sig")

info = {
    "subway_hourly_202609.csv": {"rows": len(hourly), "cols": hourly.shape[1], "md5": md5(OUT / "subway_hourly_202609.csv")},
    "subway_congestion_20250331.csv": {"rows": len(cong), "cols": cong.shape[1], "md5": md5(OUT / "subway_congestion_20250331.csv")},
    "citydata_places_121.csv": {"rows": len(places), "cols": places.shape[1], "md5": md5(OUT / "citydata_places_121.csv")},
}
print(json.dumps(info, ensure_ascii=False, indent=2))
