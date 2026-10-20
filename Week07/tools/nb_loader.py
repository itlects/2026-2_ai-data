"""노트북 0장에 들어가는 '데이터 위치 선택' 코드 (7주차 노트북 공통)."""

LOADER_MD = """
### 데이터 위치 선택 (`DATA_SOURCE`)
| 값 | 동작 | 쓰는 상황 |
|---|---|---|
| `"auto"` (기본) | GitHub 수업 저장소에서 읽고, 안 되면 **내 Google Drive**에서 `week07_MANIFEST.csv`가 있는 폴더를 자동으로 찾음 | 평소 |
| `"drive"` | 내 Drive에 미리 저장한 데이터만 사용 (처음 한 번 Drive 접근 허용) | 수업 중 GitHub가 불안정할 때 |
| `"upload"` | 내려받아 둔 파일을 직접 업로드 | Drive 연결이 어려울 때 |

어느 경로든 노트북이 파일마다 **MD5(파일 지문)** 를 확인해 `정상` 여부를 표로 보여 줍니다. 같은 파일이면 기대값도 똑같이 나옵니다.
"""

LOADER_CODE = r'''
# ── 데이터 위치 선택 ─────────────────────────────────────────
DATA_SOURCE = "auto"          # "auto" | "drive" | "upload" | "github"

import os, glob, io, gzip, hashlib, urllib.request
import pandas as pd

GITHUB_BASE = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week07/data/"
MANIFEST = "week07_MANIFEST.csv"

def _find_in_drive():
    from google.colab import drive
    if not os.path.isdir("/content/drive/MyDrive"):
        drive.mount("/content/drive")
    for depth in range(0, 7):                                   # 내 드라이브 아래 6단계까지 탐색
        hits = sorted(glob.glob("/content/drive/MyDrive/" + "*/" * depth + MANIFEST))
        if hits:
            return os.path.dirname(hits[0]) + "/"
    raise FileNotFoundError("내 Drive에서 week07_MANIFEST.csv 를 찾지 못했습니다.\n"
        "· 공유받은 '강의7주/02_데이터' 폴더를 오른쪽 클릭 → 정리 → '바로가기 추가' → '내 드라이브' 후 다시 실행하세요.")

def _upload():
    from google.colab import files
    os.makedirs("week07_data", exist_ok=True)
    print("02_데이터 폴더에서 내려받은 파일(week07_MANIFEST.csv 포함)을 모두 선택하세요.")
    for name, data in files.upload().items():
        open(os.path.join("week07_data", name), "wb").write(data)
    return "week07_data/"

def resolve_base(source=DATA_SOURCE):
    if source in ("auto", "github"):
        try:
            urllib.request.urlopen(GITHUB_BASE + MANIFEST, timeout=15).read()
            return GITHUB_BASE
        except Exception as e:
            if source == "github":
                raise
            print("GitHub 접속 실패 → Google Drive에서 찾습니다:", type(e).__name__)
            source = "drive"
    if source == "drive":
        return _find_in_drive()
    if source == "upload":
        return _upload()
    if os.path.isdir(source):                                   # 폴더 경로를 직접 적은 경우
        return source.rstrip("/") + "/"
    raise ValueError("DATA_SOURCE 값을 확인하세요: " + str(source))

def read_bytes(name):
    if BASE.startswith("http"):
        return urllib.request.urlopen(BASE + name, timeout=120).read()
    return open(BASE + name, "rb").read()

BASE = resolve_base()
manifest = pd.read_csv(io.BytesIO(read_bytes(MANIFEST)), encoding="utf-8-sig")
print("데이터 위치:", BASE)
manifest[["file", "bytes", "rows", "note"]]
'''

CHECK_CODE = r'''
# 파일 지문(MD5) 확인: 수업 저장소 원본과 똑같은 파일인지 검사
def check_file(name):
    data = read_bytes(name)
    expected = manifest.set_index("file").loc[name, "md5"]
    ok = hashlib.md5(data).hexdigest() == expected
    print(f"{name:28s} {len(data):>10,} bytes  →  {'정상(MD5 일치)' if ok else '⚠ 다른 파일! 강의자에게 알리세요'}")
    return data
'''
