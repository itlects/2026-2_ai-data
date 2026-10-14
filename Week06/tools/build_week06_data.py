"""6주차 실습 데이터 생성 스크립트 (강의자용).

원자료: bab2min/corpus  sentiment/naver_shopping.txt  (네이버 쇼핑 상품 후기 20만 건, Public Domain)
        https://github.com/bab2min/corpus/tree/master/sentiment

만드는 파일 (Week06/data/)
  naver_shopping.txt.gz       원자료 미러 (내용 바이트 동일, gzip 압축만)
  week06_reviews_300.csv      수업용 표본 300건 (별점 1·2·4·5 각 75건, 무작위 층화추출)
  week06_MANIFEST.csv         파일 목록·크기·MD5·행 수

사용법
  python Week06/tools/build_week06_data.py [원자료 경로 또는 URL]

워크북 0(감성데이터 수집) 노트북은 이 스크립트와 **같은 규칙·같은 난수 시드**로 표본을 뽑으므로,
학생이 직접 수집한 결과의 MD5가 week06_reviews_300.csv 와 같게 나온다.
"""
import gzip
import hashlib
import io
import os
import re
import sys
import urllib.request

import pandas as pd

SOURCE_URL = "https://raw.githubusercontent.com/bab2min/corpus/master/sentiment/naver_shopping.txt"
SEED = 2026
N_PER_RATING = 75
# 개인정보·외부 링크로 보이는 문장 제외: 전화번호 형태, 이메일(@), URL
PII_PATTERN = r"(?:\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}|@|https?://|www\.|\.com)"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def load_raw_bytes(src):
    if src.startswith("http"):
        return urllib.request.urlopen(src, timeout=120).read()
    return open(src, "rb").read()


def read_corpus(raw_bytes):
    df = pd.read_csv(io.BytesIO(raw_bytes), sep="\t", header=None, names=["rating", "review_text"],
                     quoting=3, dtype={"rating": "int64", "review_text": "string"})
    df.insert(0, "src_line", range(1, len(df) + 1))      # 원자료 몇 번째 줄인지 (추적용)
    return df


def make_sample(df):
    """워크북 0과 동일한 정제·추출 규칙."""
    c = df.dropna(subset=["review_text"]).copy()
    c["review_text"] = c["review_text"].str.strip().str.replace(r"\s+", " ", regex=True)
    c = c.drop_duplicates(subset=["review_text"], keep=False)      # 같은 문장이 여러 번 → 모두 제외
    c = c[~c["review_text"].str.contains(PII_PATTERN, regex=True)]
    c = c[c["review_text"].str.len().between(10, 150)]
    s = (c.groupby("rating").sample(n=N_PER_RATING, random_state=SEED)
           .sample(frac=1, random_state=SEED).reset_index(drop=True))
    s.insert(0, "review_id", [f"R{i:03d}" for i in range(1, len(s) + 1)])
    s["rating_label"] = s["rating"].map(lambda r: "긍정" if r >= 4 else "부정")
    s["review_text"] = s["review_text"].astype(str)
    return s[["review_id", "src_line", "rating", "rating_label", "review_text"]], len(c)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SOURCE_URL
    raw_bytes = load_raw_bytes(src)
    print("원자료 MD5:", hashlib.md5(raw_bytes).hexdigest(), "크기:", len(raw_bytes))
    gz_path = os.path.join(DATA, "naver_shopping.txt.gz")
    with open(gz_path, "wb") as f:                     # mtime=0 → 다시 만들어도 같은 gz 바이트
        with gzip.GzipFile(filename="naver_shopping.txt", mode="wb", fileobj=f, mtime=0) as g:
            g.write(raw_bytes)

    df = read_corpus(raw_bytes)
    sample, n_cand = make_sample(df)
    out = os.path.join(DATA, "week06_reviews_300.csv")
    sample.to_csv(out, index=False, encoding="utf-8-sig", lineterminator="\n")
    print("원자료", len(df), "행 → 정제 후 후보", n_cand, "행 → 표본", len(sample), "행")

    rows = []
    for name, nrows, note in [("week06_reviews_300.csv", len(sample), "수업용 표본 (워크북 1~4 입력)"),
                              ("naver_shopping.txt.gz", len(df),
                               "원자료 미러, 압축 해제 MD5=" + hashlib.md5(raw_bytes).hexdigest())]:
        p = os.path.join(DATA, name)
        rows.append({"file": name, "bytes": os.path.getsize(p), "md5": md5(p), "rows": nrows, "note": note})
    pd.DataFrame(rows).to_csv(os.path.join(DATA, "week06_MANIFEST.csv"), index=False,
                              encoding="utf-8-sig", lineterminator="\n")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
