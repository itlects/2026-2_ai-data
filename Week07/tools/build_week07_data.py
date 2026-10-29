"""7주차 실습 데이터 생성 스크립트 (강의자용).

원자료 (둘 다 공개 라이선스, 키 불필요)
  댓글: e9t/nsmc  ratings.txt — 네이버 영화 140자평 20만 건 (CC0 1.0)
        https://github.com/e9t/nsmc
  뉴스: KLUE-benchmark/KLUE  ynat-v1.1_train.json — 연합뉴스 기사 제목 45,678건, 7개 분야 (CC BY-SA 4.0)
        https://github.com/KLUE-benchmark/KLUE/tree/main/klue_benchmark/ynat-v1.1

만드는 파일 (Week07/data/)
  week07_comments_300.csv       워크북 1 입력: 댓글 300건 (긍정 150 · 부정 150)
  week07_news_350.csv           워크북 2 입력: 뉴스 제목 350건 (7개 분야 × 50)
  nsmc_ratings.txt.gz           댓글 원자료 미러 (내용 바이트 동일, gzip 압축만)
  ynat_titles_all.csv.gz        뉴스 원자료에서 제목·분야·날짜·URL만 뽑은 전체본 (확장 과제용)
  week07_MANIFEST.csv           파일 목록·크기·MD5·행 수

사용법
  python Week07/tools/build_week07_data.py
"""
import gzip
import hashlib
import io
import json
import os
import urllib.request

import pandas as pd

NSMC_URL = "https://raw.githubusercontent.com/e9t/nsmc/master/ratings.txt"
YNAT_URL = "https://raw.githubusercontent.com/KLUE-benchmark/KLUE/main/klue_benchmark/ynat-v1.1/ynat-v1.1_train.json"
SEED = 2026
N_PER_SENTIMENT = 150
N_PER_CATEGORY = 50
CATEGORIES = ["정치", "경제", "사회", "생활문화", "세계", "IT과학", "스포츠"]
# 개인정보·외부 링크로 보이는 문장 제외: 전화번호 형태, 이메일(@), URL
PII_PATTERN = r"(?:\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}|@|https?://|www\.|\.com|[A-Za-z]+\d{3,})"
# 수업 화면에 띄우기 부적절한 표현(욕설·성적·혐오·역사 왜곡), 주변 인물 언급(사생활), 원자료의 가림표(OO) 포함 문장 제외
# ※ 목록 방식이라 완벽하지 않다. 수업 중 발견하면 강의자에게 알리고 이 목록에 추가해 다시 만든다.
BLOCK_WORDS = ["새끼", "ㅅㅂ", "ㅆㅂ", "시발", "씨발", "씹", "병신", "ㅂㅅ", "존나", "졸라", "개새", "썅", "좆", "지랄", "닥치",
               "섹스", "섹시", "야동", "야하", "노출", "조개", "에로", "정사", "베드신", "하악",
               "동성애", "게이", "폭동", "홍어", "틀딱", "한남", "김치녀", "된장녀", "쪽바리", "일빠", "짱깨", "짱개", "흑형", "다문화",
               "예수쟁이", "미친년", "존내", "빨고", "빨아", "똥꼬", "엿같", "병맛", "레즈",
               "우리반", "집사", "OO", "ㅗ"]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
CACHE = os.environ.get("W7_RAW_DIR", "")       # 이미 받아 둔 원자료 폴더(선택)


def fetch(url):
    if CACHE:
        p = os.path.join(CACHE, url.rsplit("/", 1)[1])
        if os.path.exists(p):
            return open(p, "rb").read()
    return urllib.request.urlopen(url, timeout=300).read()


def write_gz(path, inner_name, data):
    with open(path, "wb") as f:                     # mtime=0 → 다시 만들어도 같은 gz 바이트
        with gzip.GzipFile(filename=inner_name, mode="wb", fileobj=f, mtime=0) as g:
            g.write(data)


def clean_text(s):
    """앞뒤 공백 제거, 연속 공백 1칸, 유니코드 NFC 정규화(호환용 한자 '女'(U+F981) → '女'(U+5973) 등)"""
    return (s.astype("string").str.normalize("NFC")
             .str.strip().str.replace(r"\s+", " ", regex=True))


def make_comments(raw):
    df = pd.read_csv(io.BytesIO(raw), sep="\t", quoting=3, dtype={"id": "string", "document": "string"})
    n_raw = len(df)
    c = df.dropna(subset=["document"]).copy()
    c["document"] = clean_text(c["document"])
    c = c.drop_duplicates(subset=["document"], keep=False)          # 같은 문장이 여러 번 → 모두 제외
    c = c[~c["document"].str.contains(PII_PATTERN, regex=True)]
    c = c[~c["document"].str.contains("|".join(BLOCK_WORDS), regex=True)]
    c = c[c["document"].str.len().between(10, 140)]
    # 강의자가 표본을 읽고 제외한 문장 (사유는 week07_comment_exclude.csv)
    excl = set(pd.read_csv(os.path.join(HERE, "week07_comment_exclude.csv"), dtype=str)["src_id"])
    n_cand = len(c)
    # 후보 전체를 섞은 순서를 고정한 뒤 제외 목록을 빼고 감성별 앞에서 150건
    # → 한 건을 빼면 같은 감성의 다음 후보 한 건만 바뀐다
    order = c.sample(frac=1, random_state=SEED)
    order = order[~order["id"].astype(str).isin(excl)]
    s = (order.groupby("label", group_keys=False).head(N_PER_SENTIMENT)
              .sample(frac=1, random_state=SEED).reset_index(drop=True))
    out = pd.DataFrame({
        "comment_id": [f"C{i:03d}" for i in range(1, len(s) + 1)],
        "src_id": s["id"].astype(str),
        "sentiment": s["label"].map({1: "긍정", 0: "부정"}),
        "text": s["document"].astype(str),
    })
    return out, n_raw, n_cand


def norm_date(d):
    # '2016.06.30. 오전 10:36' / '2019.03.19 21:32' → '2016-06-30'
    y, m, dd = d.replace(" ", "").split(".")[:3]
    return f"{y}-{m}-{dd[:2]}"


def make_news(raw):
    rows = json.loads(raw.decode("utf-8"))
    full = pd.DataFrame({
        "guid": [r["guid"] for r in rows],
        "category": [r["label"] for r in rows],
        "title": [r["title"] for r in rows],
        "date": [norm_date(r["date"]) for r in rows],
        "url": [r["url"] for r in rows],
    })
    c = full.copy()
    c["title"] = clean_text(c["title"])
    c = c.drop_duplicates(subset=["title"], keep=False)
    c = c[c["title"].str.len() >= 10]
    s = (c.groupby("category").sample(n=N_PER_CATEGORY, random_state=SEED)
           .sample(frac=1, random_state=SEED).reset_index(drop=True))
    s.insert(0, "news_id", [f"N{i:03d}" for i in range(1, len(s) + 1)])
    s["title"] = s["title"].astype(str)
    return s[["news_id", "category", "title", "date", "url", "guid"]], full, len(c)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def main():
    os.makedirs(DATA, exist_ok=True)
    nsmc = fetch(NSMC_URL)
    ynat = fetch(YNAT_URL)
    print("NSMC 원자료 MD5", hashlib.md5(nsmc).hexdigest(), "| YNAT 원자료 MD5", hashlib.md5(ynat).hexdigest())

    comments, n_raw_c, n_cand_c = make_comments(nsmc)
    news, ynat_full, n_cand_n = make_news(ynat)
    print(f"댓글: 원자료 {n_raw_c} → 정제 후보 {n_cand_c} → 표본 {len(comments)}")
    print(f"뉴스: 원자료 {len(ynat_full)} → 정제 후보 {n_cand_n} → 표본 {len(news)}")

    kw = dict(index=False, encoding="utf-8-sig", lineterminator="\n")
    comments.to_csv(os.path.join(DATA, "week07_comments_300.csv"), **kw)
    news.to_csv(os.path.join(DATA, "week07_news_350.csv"), **kw)
    write_gz(os.path.join(DATA, "nsmc_ratings.txt.gz"), "ratings.txt", nsmc)
    buf = ynat_full.to_csv(index=False, lineterminator="\n").encode("utf-8")
    write_gz(os.path.join(DATA, "ynat_titles_all.csv.gz"), "ynat_titles_all.csv", buf)

    rows = []
    for name, nrows, note in [
        ("week07_comments_300.csv", len(comments), "워크북 1 입력: 네이버 영화 140자평(NSMC) 긍정 150·부정 150"),
        ("week07_news_350.csv", len(news), "워크북 2 입력: 연합뉴스 제목(KLUE-YNAT) 7개 분야 × 50"),
        ("nsmc_ratings.txt.gz", n_raw_c, "댓글 원자료 미러, 압축 해제 MD5=" + hashlib.md5(nsmc).hexdigest()),
        ("ynat_titles_all.csv.gz", len(ynat_full), "뉴스 제목 전체본(guid·category·title·date·url), 확장 과제용"),
    ]:
        p = os.path.join(DATA, name)
        rows.append({"file": name, "bytes": os.path.getsize(p), "md5": md5(p), "rows": nrows, "note": note})
    man = pd.DataFrame(rows)
    man.to_csv(os.path.join(DATA, "week07_MANIFEST.csv"), **kw)
    print(man.to_string(index=False))


if __name__ == "__main__":
    main()
