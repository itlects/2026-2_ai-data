"""7주차 보조 노트북 원고: 유튜브 댓글 직접 수집(선택 과제), Drive 데이터 준비(강의자용)."""
from nb_common import md, code


def youtube_cells(version_title):
    return [
md(f"""
# 7주차 · [확장] 유튜브 댓글 직접 수집 — {version_title}

**YouTube Data API v3**의 `commentThreads.list`로 공개 영상의 댓글을 모아, 수업 데이터와 **같은 모양의 CSV**로 저장합니다.
저장한 CSV는 본 실습 노트북(워크북 1)에 그대로 넣어 워드클라우드를 그릴 수 있습니다.

| 단계 | 하는 일 |
|---|---|
| 1 | API 키 준비 (Google Cloud 콘솔, 무료 할당량) → Colab **보안 비밀(🔑)** 에 `YOUTUBE_API_KEY` 로 저장 |
| 2 | 영상 주소 입력 → 댓글 받기 (100개씩 페이지 단위) |
| 3 | 정리: 작성자 정보 저장 안 함, 링크·이메일·전화번호 형태 제거, 중복 제거, 길이 제한 |
| 4 | `my_youtube_comments.csv` 저장 → 본 노트북 1-1에서 사용 |

> **꼭 지킬 것**
> - 작성자 이름·채널 ID·프로필은 **저장하지 않습니다**(개인정보 최소 수집). 이 노트북은 댓글 본문·작성일·좋아요 수만 남깁니다.
> - API 키를 코드나 노트북에 직접 적지 않습니다. 공유·제출하는 파일에 키가 들어가면 안 됩니다.
> - 수집한 댓글 원문을 그대로 재배포하지 말고, 과제에는 **집계 결과(빈도표·그림)와 몇 개의 짧은 인용**만 씁니다.
> - [YouTube API 서비스 약관](https://developers.google.com/youtube/terms/api-services-terms-of-service)과 할당량(기본 하루 10,000단위, 이 요청은 1회 1단위)을 확인합니다.

### API 키 만들기 (처음 한 번, 약 5분)
1. [Google Cloud 콘솔](https://console.cloud.google.com/) → 새 프로젝트 만들기
2. `API 및 서비스 → 라이브러리` → **YouTube Data API v3** 검색 → 사용
3. `API 및 서비스 → 사용자 인증 정보 → 사용자 인증 정보 만들기 → API 키` → 키 복사
   (권장: 키 제한 → API 제한 → YouTube Data API v3 만 선택)
4. Colab 왼쪽 **🔑 보안 비밀** → 새 보안 비밀 추가 → 이름 `YOUTUBE_API_KEY`, 값에 키 붙여넣기 → 노트북 액세스 켜기

공식 문서: [commentThreads.list](https://developers.google.com/youtube/v3/docs/commentThreads/list)
"""),
md("## 1. 설정"),
code('''
VIDEO_URL = "https://www.youtube.com/watch?v=..."   # 댓글이 공개된 영상 주소로 바꾸기
MAX_COMMENTS = 300                                   # 최대 몇 개까지 받을지 (100개당 할당량 1단위)
ORDER = "relevance"                                  # "relevance"(인기순) 또는 "time"(최신순)
'''),
md("## 2. 댓글 받기"),
code(r'''
import re, json, time, urllib.parse, urllib.request
import pandas as pd

def video_id_from(url):
    """https://www.youtube.com/watch?v=ID · https://youtu.be/ID · /shorts/ID 모두 지원"""
    m = re.search(r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})", url)
    if not m:
        raise ValueError("영상 주소에서 ID를 찾지 못했습니다: " + url)
    return m.group(1)

def get_api_key():
    try:
        from google.colab import userdata
        return userdata.get("YOUTUBE_API_KEY")
    except Exception as e:
        raise RuntimeError("Colab 보안 비밀 'YOUTUBE_API_KEY'를 읽지 못했습니다. 위 안내 4번을 확인하세요.") from e

def fetch_comments(video_id, api_key, max_comments=300, order="relevance"):
    """commentThreads.list 를 페이지마다 호출. 작성자 정보는 처음부터 꺼내지 않는다."""
    rows, token = [], None
    while len(rows) < max_comments:
        params = {"part": "snippet", "videoId": video_id, "maxResults": 100, "order": order,
                  "textFormat": "plainText", "key": api_key}
        if token:
            params["pageToken"] = token
        url = "https://www.googleapis.com/youtube/v3/commentThreads?" + urllib.parse.urlencode(params)
        try:
            res = json.loads(urllib.request.urlopen(url, timeout=30).read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")
            raise RuntimeError(f"API 오류 {e.code}: 댓글이 꺼진 영상·잘못된 키·할당량 초과인지 확인하세요.\n{msg[:300]}")
        for item in res.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            rows.append({"src_id": item["id"], "video_id": video_id,
                         "published_at": s["publishedAt"][:10], "like_count": s.get("likeCount", 0),
                         "text": s["textDisplay"]})
        token = res.get("nextPageToken")
        if not token:
            break
        time.sleep(0.2)
    return pd.DataFrame(rows[:max_comments])

VIDEO_ID = video_id_from(VIDEO_URL)
raw = fetch_comments(VIDEO_ID, get_api_key(), MAX_COMMENTS, ORDER)
print("영상:", VIDEO_ID, "| 받은 댓글:", len(raw))
raw.head()
'''),
md("""
## 3. 정리 — 수업 데이터와 같은 규칙
수업용 댓글(NSMC)을 만들 때와 같은 규칙입니다: 공백 정리 → 같은 문장 중복 제거 → 링크·이메일·전화번호 형태가 있는 댓글 제외 → 길이 10~300자.
욕설·비하 표현은 목록으로 다 걸러지지 않으므로 **저장 전에 직접 읽어 보고** 과제에 쓰기 부적절한 댓글은 `DROP_IDS`에 넣어 뺍니다.
"""),
code(r'''
PII_PATTERN = r"(?:\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}|@|https?://|www\.|\.com)"

def clean_comments(df):
    c = df.copy()
    c["text"] = c["text"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
    n0 = len(c)
    c = c.drop_duplicates(subset=["text"], keep="first")
    n1 = len(c)
    c = c[~c["text"].str.contains(PII_PATTERN, regex=True)]
    n2 = len(c)
    c = c[c["text"].str.len().between(10, 300)]
    print(f"받은 {n0} → 중복 제거 {n1} → 링크·연락처 제외 {n2} → 길이 10~300자 {len(c)}")
    return c.reset_index(drop=True)

clean = clean_comments(raw)
pd.set_option("display.max_colwidth", 100)
clean[["src_id", "like_count", "text"]].head(30)          # 직접 읽어 보기
'''),
code('''
DROP_IDS = []          # 빼고 싶은 댓글의 src_id 를 넣기 (예: ["Ugx...", "Ugy..."])
final = clean[~clean["src_id"].isin(DROP_IDS)].reset_index(drop=True)
final.insert(0, "comment_id", [f"Y{i:03d}" for i in range(1, len(final) + 1)])
final["sentiment"] = "미분류"          # 감성 라벨이 없음 → 워크북 1-5(긍정/부정 비교)는 직접 라벨을 붙인 경우에만
final = final[["comment_id", "src_id", "sentiment", "text", "video_id", "published_at", "like_count"]]
final.to_csv("my_youtube_comments.csv", index=False, encoding="utf-8-sig")

record = {"video_id": VIDEO_ID, "video_url": VIDEO_URL, "collected_at": time.strftime("%Y-%m-%d %H:%M"),
          "order": ORDER, "received": len(raw), "saved": len(final), "dropped_by_hand": len(DROP_IDS)}
json.dump(record, open("my_youtube_collection_record.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(record)
'''),
md("""
## 4. 본 실습 노트북에서 쓰기
1. 왼쪽 **파일** 창에서 `my_youtube_comments.csv`와 `my_youtube_collection_record.json`을 내려받습니다.
2. `Week07_텍스트시각화` 노트북 **1-1** 셀 아래에서 다음 한 줄로 댓글 데이터를 바꿉니다(파일을 Colab에 업로드한 뒤).
```python
comments = pd.read_csv("my_youtube_comments.csv", encoding="utf-8-sig")
```
3. `STOP_COMMENT`(불용어)를 영상 주제에 맞게 고칩니다. 영화 댓글용 불용어(`영화`, `드라마` …)는 맞지 않을 수 있습니다.
4. 감성 라벨이 `미분류`이므로 **1-5 긍정/부정 비교는 건너뛰거나**, 20~30개를 직접 읽고 `sentiment`를 붙여서 해 봅니다.
5. 과제에는 **영상 주소·수집 날짜·받은 개수·정리 후 개수**(`my_youtube_collection_record.json`)를 함께 적습니다.
"""),
    ]


def drive_prep_cells(version_title):
    return [
md("""
# 7주차 · 데이터 준비 (강의자용, 수업 전 1회 · 약 1분)
GitHub 수업 저장소의 7주차 데이터를 **Google Drive `강의7주/02_데이터`** 에 저장합니다. 수업 중 GitHub 접속이 불안정해도
학생 노트북이 `DATA_SOURCE = "auto"`(또는 `"drive"`)로 Drive의 같은 파일을 찾아 씁니다. MD5를 확인한 뒤 저장하므로 기대값이 그대로 나옵니다.

**학생 안내:** 공유받은 `02_데이터` 폴더 → 오른쪽 클릭 → 정리 → **바로가기 추가 → 내 드라이브**.
"""),
code('''
import os, io, glob, hashlib, urllib.request, zipfile
import pandas as pd

TARGET = "auto"      # "auto": 내 Drive에서 '강의7주/02_데이터' 폴더를 자동으로 찾음. 직접 경로를 적어도 됨
GITHUB_BASE = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week07/data/"
FILES = ["week07_MANIFEST.csv", "week07_comments_300.csv", "week07_news_350.csv",
         "nsmc_ratings.txt.gz", "ynat_titles_all.csv.gz", "DATA_SOURCES.md"]

if TARGET == "auto" or TARGET.startswith("/content/drive"):
    from google.colab import drive
    drive.mount("/content/drive")
if TARGET == "auto":
    hits = [p for d in range(0, 6) for p in glob.glob("/content/drive/MyDrive/" + "*/" * d + "강의7주/02_데이터")]
    if not hits:
        raise FileNotFoundError("'강의7주/02_데이터' 폴더를 찾지 못했습니다. TARGET에 경로를 직접 적으세요.")
    TARGET = hits[0]
os.makedirs(TARGET, exist_ok=True)
print("저장 위치:", TARGET)
'''),
code('''
blobs = {f: urllib.request.urlopen(GITHUB_BASE + f, timeout=300).read() for f in FILES}
manifest = pd.read_csv(io.BytesIO(blobs["week07_MANIFEST.csv"]), encoding="utf-8-sig").set_index("file")
rows = []
for f, data in blobs.items():
    ok = "확인 대상 아님"
    if f in manifest.index:
        ok = "정상(MD5 일치)" if hashlib.md5(data).hexdigest() == manifest.loc[f, "md5"] else "⚠ MD5 불일치 — 저장 중단"
        assert ok.startswith("정상"), f
    open(os.path.join(TARGET, f), "wb").write(data)
    rows.append({"file": f, "bytes": len(data), "check": ok})

SMALL = ["week07_MANIFEST.csv", "week07_comments_300.csv", "week07_news_350.csv", "DATA_SOURCES.md"]
with zipfile.ZipFile(os.path.join(TARGET, "week07_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for f in SMALL:                       # 수업에 필요한 작은 파일만 (원자료 미러는 제외)
        z.writestr(f, blobs[f])
pd.DataFrame(rows)
'''),
md("""
**확인:** 6개 파일 + `week07_data.zip` 이 저장되면 완료. `week07_data.zip`은 Drive 연결이 어려운 학생이 `DATA_SOURCE = "upload"`로 쓸 파일입니다
(압축을 풀어 `week07_MANIFEST.csv`, 댓글·뉴스 CSV를 업로드).
"""),
code('''
sorted(os.listdir(TARGET))
'''),
    ]
