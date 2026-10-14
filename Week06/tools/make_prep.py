"""강의자용: 수업 전 1회 실행 → Drive 강의6주/01_데이터 에 실습 데이터 저장."""
import os
import nbformat as nbf

HERE = os.path.dirname(os.path.abspath(__file__))

CELLS = [
("md", """
# 6주차 · 데이터 준비 (강의자용, 수업 전 1회 · 약 1분)
GitHub 수업 저장소의 6주차 데이터를 **Google Drive `강의6주/01_데이터`** 에 저장합니다. 수업 중 GitHub 접속이 불안정해도
학생 노트북이 `DATA_SOURCE = "auto"`(또는 `"drive"`)로 Drive의 같은 파일을 찾아 씁니다. MD5를 확인한 뒤 저장하므로 기대값이 그대로 나옵니다.

**학생 안내:** 공유받은 `01_데이터` 폴더 → 오른쪽 클릭 → 정리 → **바로가기 추가 → 내 드라이브**.
"""),
("code", '''
import os, io, hashlib, urllib.request, zipfile
import pandas as pd

TARGET = "auto"      # "auto": 내 Drive에서 '강의6주/01_데이터' 폴더를 자동으로 찾음. 직접 경로를 적어도 됨
GITHUB_BASE = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week06/data/"
FILES = ["week06_MANIFEST.csv", "week06_reviews_300.csv", "naver_shopping.txt.gz", "DATA_SOURCES.md"]

if TARGET == "auto" or TARGET.startswith("/content/drive"):
    from google.colab import drive
    drive.mount("/content/drive")
if TARGET == "auto":
    import glob
    hits = [p for d in range(0, 6) for p in glob.glob("/content/drive/MyDrive/" + "*/" * d + "강의6주/01_데이터")]
    if not hits:
        raise FileNotFoundError("'강의6주/01_데이터' 폴더를 찾지 못했습니다. TARGET에 경로를 직접 적으세요.")
    TARGET = hits[0]
os.makedirs(TARGET, exist_ok=True)
print("저장 위치:", TARGET)
'''),
("code", '''
blobs = {f: urllib.request.urlopen(GITHUB_BASE + f, timeout=120).read() for f in FILES}
manifest = pd.read_csv(io.BytesIO(blobs["week06_MANIFEST.csv"]), encoding="utf-8-sig").set_index("file")
rows = []
for f, data in blobs.items():
    ok = "확인 대상 아님"
    if f in manifest.index:
        ok = "정상(MD5 일치)" if hashlib.md5(data).hexdigest() == manifest.loc[f, "md5"] else "⚠ MD5 불일치 — 저장 중단"
        assert ok.startswith("정상"), f
    open(os.path.join(TARGET, f), "wb").write(data)
    rows.append({"file": f, "bytes": len(data), "check": ok})

with zipfile.ZipFile(os.path.join(TARGET, "week06_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for f, data in blobs.items():
        z.writestr(f, data)
pd.DataFrame(rows)
'''),
("md", """
**확인:** 4개 파일 + `week06_data.zip` 이 저장되면 완료. `week06_data.zip`은 Drive 연결이 어려운 학생이 `DATA_SOURCE = "upload"`로 쓸 파일입니다
(압축을 풀어 4개 파일을 업로드).
"""),
("code", '''
sorted(os.listdir(TARGET))
'''),
]


def main():
    nb = nbf.v4.new_notebook()
    nb.metadata = {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}}
    nb.cells = [nbf.v4.new_markdown_cell(s.strip()) if k == "md" else nbf.v4.new_code_cell(s.strip()) for k, s in CELLS]
    nbf.write(nb, os.path.join(HERE, "..", "colab", "Week06_00_데이터준비_Drive저장.ipynb"))


if __name__ == "__main__":
    main()
