"""워크북 1~3 (텍스트 데이터 시각화) 노트북 원고. 실습본·완성본을 같은 원고에서 만든다."""
from nb_common import md, code
from nb_loader import LOADER_MD, LOADER_CODE, CHECK_CODE
from ai_example import AI_COMMENT_EXAMPLE, AI_NEWS_EXAMPLE


def cells(version_title):
    return [
md(f"""
# 7주차 · 텍스트 데이터의 시각화 — {version_title}

**인공지능과 데이터 활용** · 실제 **온라인 댓글 300건**과 **뉴스 기사 제목 350건**을
단어 빈도표·막대그래프·**워드클라우드**로 시각화하고, 같은 원문으로 받은 **AI 요약·키워드**를 원문 근거로 검증·비교합니다.

| 워크북 | 하는 일 | 핵심 코드 | 산출물 |
|---|---|---|---|
| 1. 댓글 워드클라우드 | 불러오기·점검 → 어절 vs 형태소 → 불용어 → 빈도·워드클라우드 → 긍정/부정 비교, 문맥 확인 | `re.findall` `Kiwi` `Counter` `WordCloud` | 그림 3장, CSV |
| 2. 뉴스 워드클라우드 | 분야별 건수 → 명사 빈도 → 전체·분야별 워드클라우드 → 빈도 vs 특징어(TF-IDF) | `groupby` `TfidfVectorizer` | 그림 3장, CSV |
| 3. AI 요약·키워드 비교 | 프롬프트 만들기 → AI 결과 붙여넣기 → 원문 근거 건수·빈도 순위로 검증 → 일치/차이 표 | `str.contains` `merge` | 검증표 CSV, 그림 1장 |

**실행:** `런타임 → 모두 실행` (처음 약 1~2분, 설치 포함). 실습본은 `TODO`의 `...`을 채운 뒤 실행하고 **기대값**과 비교합니다.
API 키·유료 서비스는 필요 없습니다. AI 요약은 출력된 프롬프트를 ChatGPT·Gemini·Claude 등에 붙여 넣어 받습니다.

> 데이터: 네이버 영화 140자평(NSMC, CC0) 표본 300건 · 연합뉴스 기사 제목(KLUE-YNAT, CC BY-SA 4.0) 표본 350건.
> 수업 화면용으로 욕설·성적·혐오 표현은 걸러 냈습니다. 그래도 불편한 문장이 보이면 강의자에게 알려 주세요.
"""),
md("## 0. 실행 환경 준비"),
code("""
!pip -q install koreanize-matplotlib wordcloud kiwipiepy   # 한글 그래프·워드클라우드·형태소 분석기 (처음 한 번, 약 30초)
"""),
code("""
import os, re, glob
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")
import koreanize_matplotlib                     # import만 하면 그래프 한글이 깨지지 않음
from wordcloud import WordCloud
from kiwipiepy import Kiwi

plt.rcParams["axes.unicode_minus"] = False
# 워드클라우드는 matplotlib 설정을 쓰지 않으므로 한글 글꼴 파일 경로를 직접 알려 준다
FONT = sorted(glob.glob(os.path.join(os.path.dirname(koreanize_matplotlib.__file__), "fonts", "NanumGothic*.ttf")))[0]
os.makedirs("figures", exist_ok=True)
os.makedirs("results", exist_ok=True)
kiwi = Kiwi()                                   # 한국어 형태소 분석기 (처음 만들 때 몇 초 걸림)
print("글꼴:", os.path.basename(FONT), "| 형태소 분석기 준비 완료")
"""),
md(LOADER_MD),
code(LOADER_CODE),
code(CHECK_CODE + '''
pd.set_option("display.max_colwidth", 70)
pd.set_option("display.width", 160)
'''),
md("""
### 공통 도구 — 시각화 함수
막대그래프와 워드클라우드를 그리는 함수를 미리 만들어 둡니다. **빈도(Counter)만 넣으면** 그림을 그리고 `figures/`에 저장합니다.
"""),
code('''
def bar_top(counter, title, fname, n=20, color="#4C72B0"):
    """상위 n개 단어 가로 막대그래프"""
    words, counts = zip(*counter.most_common(n))
    fig, ax = plt.subplots(figsize=(7, 0.32 * n + 1))
    ax.barh(words[::-1], counts[::-1], color=color)
    for y, v in enumerate(counts[::-1]):
        ax.text(v + 0.3, y, str(v), va="center", fontsize=9)
    ax.set_title(title); ax.set_xlabel("빈도(등장 횟수)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(f"figures/{fname}", dpi=150); plt.show()

def make_wc(counter, colormap="viridis", max_words=80):
    """빈도 → 워드클라우드 객체 (random_state 고정: 실행할 때마다 배치가 같음)"""
    return WordCloud(font_path=FONT, width=900, height=500, background_color="white",
                     colormap=colormap, max_words=max_words, random_state=42,
                     prefer_horizontal=0.9).generate_from_frequencies(counter)

def show_wc(counter, title, fname, colormap="viridis"):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.imshow(make_wc(counter, colormap)); ax.axis("off"); ax.set_title(title)
    fig.tight_layout(); fig.savefig(f"figures/{fname}", dpi=150); plt.show()
'''),
md("""
---
# 워크북 1 · 온라인 댓글 워드클라우드
```
불러오기·점검 → 토큰 나누기(어절 vs 형태소) → 불용어 정리 → 빈도표·막대·워드클라우드 → 긍정/부정 비교 → 문맥 확인
```
댓글 데이터: 네이버 영화 140자평. 한 줄 댓글이라는 점에서 **유튜브 댓글과 형태가 같습니다**
(줄임말·맞춤법 오류·이모티콘·ㅋㅋ). 직접 수집한 유튜브 댓글로 바꾸려면 `Week07_00_유튜브댓글수집` 노트북을 사용합니다.

### 1-1. 불러오기와 점검
"""),
code('''
import io
data = check_file("week07_comments_300.csv")
''' + '''
# TODO 1: 댓글 CSV를 읽어 comments 에 저장하세요.  힌트: pd.read_csv(io.BytesIO(data), encoding="utf-8-sig")
comments = pd.read_csv(io.BytesIO(data), encoding="utf-8-sig")
comments.head()
''', todo='''
import io
data = check_file("week07_comments_300.csv")

# TODO 1: 댓글 CSV를 읽어 comments 에 저장하세요.  힌트: pd.read_csv(io.BytesIO(data), encoding="utf-8-sig")
comments = ...
comments.head()
'''),
code('''
print("행·열:", comments.shape)
print("결측:", comments.isna().sum().to_dict())
print("감성별 건수:", comments["sentiment"].value_counts().to_dict())
comments["length"] = comments["text"].str.len()
comments["length"].describe().round(1)
'''),
md("""
**기대값** 300행 × 4열 · 결측 0 · 긍정 150 / 부정 150 · 길이 평균 약 35자(최소 10, 최대 140).
`sentiment`는 원자료의 평점(1~4점=부정, 9~10점=긍정)으로 붙인 라벨입니다.

> **직접 수집한 유튜브 댓글로 바꾸기(선택):** `Week07_00_유튜브댓글수집` 노트북으로 만든 `my_youtube_comments.csv`를 업로드한 뒤
> 이 셀 아래에 `comments = pd.read_csv("my_youtube_comments.csv", encoding="utf-8-sig")` 한 줄을 넣고 실행합니다.
> 이때 기대값은 달라지고, 감성 라벨이 없으므로 1-5·1-6의 긍정/부정 비교는 건너뜁니다.

### 1-2. 토큰 나누기 — 어절(정규식) vs 형태소(Kiwi)
워드클라우드는 **단어별 개수**로 그립니다. 그러려면 문장을 단어(토큰)로 나눠야 하는데, 한국어는 조사·어미가 붙어서
`영화`, `영화를`, `영화가`가 서로 다른 단어로 세어집니다. 두 방법을 비교해 봅니다.
"""),
code(r'''
def eojeol_tokens(text):
    """정규식: 한글·영문·숫자 2글자 이상 덩어리(어절)를 그대로 단어로 본다"""
    return re.findall(r"[가-힣A-Za-z0-9]{2,}", str(text).lower())

def morph_tokens(text):
    """형태소 분석: 명사(일반·고유)와 형용사만 남긴다. 형용사는 '좋'→'좋다'처럼 기본형으로"""
    out = []
    for t in kiwi.tokenize(str(text)):
        if t.tag in ("NNG", "NNP") and len(t.form) >= 2:
            out.append(t.form)
        elif t.tag == "VA":
            out.append(t.form + "다")
    return out

sample = comments.loc[0, "text"]
print("원문  :", sample)
print("어절  :", eojeol_tokens(sample))
print("형태소:", morph_tokens(sample))
print("품사표:", [(t.form, t.tag) for t in kiwi.tokenize(sample)][:12])
'''),
code('''
# TODO 2: 300건 전체에 두 방법을 적용해 Counter로 세세요.
#   힌트: Counter(w for t in comments["text"] for w in eojeol_tokens(t))
eojeol_cnt = Counter(w for t in comments["text"] for w in eojeol_tokens(t))
morph_cnt = Counter(w for t in comments["text"] for w in morph_tokens(t))

cmp = pd.DataFrame({"어절(정규식)": [f"{w} {c}" for w, c in eojeol_cnt.most_common(12)],
                    "형태소(Kiwi)": [f"{w} {c}" for w, c in morph_cnt.most_common(12)]})
print("서로 다른 단어 수 — 어절:", len(eojeol_cnt), "/ 형태소:", len(morph_cnt))
print("'영화'로 시작하는 어절:", {w: c for w, c in eojeol_cnt.items() if w.startswith("영화")})
cmp
''', todo='''
# TODO 2: 300건 전체에 두 방법을 적용해 Counter로 세세요.
#   힌트: Counter(w for t in comments["text"] for w in eojeol_tokens(t))
eojeol_cnt = ...
morph_cnt = ...

cmp = pd.DataFrame({"어절(정규식)": [f"{w} {c}" for w, c in eojeol_cnt.most_common(12)],
                    "형태소(Kiwi)": [f"{w} {c}" for w, c in morph_cnt.most_common(12)]})
print("서로 다른 단어 수 — 어절:", len(eojeol_cnt), "/ 형태소:", len(morph_cnt))
print("'영화'로 시작하는 어절:", {w: c for w, c in eojeol_cnt.items() if w.startswith("영화")})
cmp
'''),
md("""
**기대값** `EXPECT_EOJEOL`

**생각해 보기** 어절 방식에서는 `영화`가 여러 형태로 흩어져 실제보다 작게 보입니다. 형태소 방식은 `영화`를 한데 모으고,
`너무·진짜·정말` 같은 부사는 빼 줍니다. 대신 `재밌다`처럼 **분석기가 잘못 자르는 신조어·줄임말**도 생깁니다.

### 1-3. 불용어(stopwords) 정리
`영화`는 영화 댓글이면 **당연히** 많이 나오므로 내용을 알려 주지 않습니다. 이런 단어를 불용어로 빼면 다른 단어가 보입니다.
불용어는 정답이 없고 **분석 목적에 따라 사람이 정하는 것**이며, 무엇을 뺐는지 꼭 기록합니다.
"""),
code('''
# TODO 3: 불용어 집합에 단어를 2개 이상 더 넣어 보세요 (예: 상위 단어 중 내용을 알려 주지 않는 것).
STOP_COMMENT = {"영화", "드라마", "작품", "생각", "사람", "평점", "점수", "느낌", "같다", "있다"}

def comment_tokens(text):
    return [w for w in morph_tokens(text) if w not in STOP_COMMENT]

comments["tokens"] = comments["text"].apply(comment_tokens)
comment_cnt = Counter(w for toks in comments["tokens"] for w in toks)
print("불용어:", sorted(STOP_COMMENT))
print("상위 15:", comment_cnt.most_common(15))
''', todo='''
# TODO 3: 불용어 집합에 단어를 2개 이상 더 넣어 보세요 (예: 상위 단어 중 내용을 알려 주지 않는 것).
STOP_COMMENT = {"영화", "드라마", "작품", "생각", ...}

def comment_tokens(text):
    return [w for w in morph_tokens(text) if w not in STOP_COMMENT]

comments["tokens"] = comments["text"].apply(comment_tokens)
comment_cnt = Counter(w for toks in comments["tokens"] for w in toks)
print("불용어:", sorted(STOP_COMMENT))
print("상위 15:", comment_cnt.most_common(15))
'''),
md("""
**기대값 (완성본 불용어 기준)** `EXPECT_COMMENT_TOP`

### 1-4. 빈도표 · 막대그래프 · 워드클라우드
같은 빈도를 두 가지로 그립니다. **막대그래프**는 정확한 순위·개수를, **워드클라우드**는 한눈에 보는 인상을 줍니다.
"""),
code('''
top_comment = pd.DataFrame(comment_cnt.most_common(30), columns=["word", "count"])
top_comment.insert(0, "rank", range(1, len(top_comment) + 1))
top_comment.to_csv("results/week07_comment_top30.csv", index=False, encoding="utf-8-sig")

bar_top(comment_cnt, "댓글 300건 상위 20개 단어 (형태소·불용어 제거)", "fig_w1_comment_bar.png")
show_wc(comment_cnt, "댓글 300건 워드클라우드", "fig_w1_comment_wc.png")
'''),
md("""
**읽는 법** 워드클라우드에서 글자 크기는 빈도에 비례하지만, **글자 길이·색·위치는 의미가 없습니다**.
긴 단어가 커 보이는 착시가 있으므로 정확한 비교는 막대그래프로 합니다.

### 1-5. 긍정 vs 부정 — 나눠서 보기
"""),
code('''
# TODO 4: 긍정·부정 댓글을 나눠 각각 Counter를 만드세요.
#   힌트: comments.loc[comments["sentiment"] == "긍정", "tokens"]
pos_cnt = Counter(w for toks in comments.loc[comments["sentiment"] == "긍정", "tokens"] for w in toks)
neg_cnt = Counter(w for toks in comments.loc[comments["sentiment"] == "부정", "tokens"] for w in toks)

fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, cnt, title, cmap in [(axes[0], pos_cnt, "긍정 댓글 150건", "Blues"), (axes[1], neg_cnt, "부정 댓글 150건", "Reds")]:
    ax.imshow(make_wc(cnt, cmap, 60)); ax.axis("off"); ax.set_title(title, fontsize=14)
fig.tight_layout(); fig.savefig("figures/fig_w1_pos_neg_wc.png", dpi=150); plt.show()

both = pd.DataFrame({"긍정": [f"{w} {c}" for w, c in pos_cnt.most_common(10)],
                     "부정": [f"{w} {c}" for w, c in neg_cnt.most_common(10)]})
both
''', todo='''
# TODO 4: 긍정·부정 댓글을 나눠 각각 Counter를 만드세요.
#   힌트: comments.loc[comments["sentiment"] == "긍정", "tokens"]
pos_cnt = ...
neg_cnt = ...

fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, cnt, title, cmap in [(axes[0], pos_cnt, "긍정 댓글 150건", "Blues"), (axes[1], neg_cnt, "부정 댓글 150건", "Reds")]:
    ax.imshow(make_wc(cnt, cmap, 60)); ax.axis("off"); ax.set_title(title, fontsize=14)
fig.tight_layout(); fig.savefig("figures/fig_w1_pos_neg_wc.png", dpi=150); plt.show()

both = pd.DataFrame({"긍정": [f"{w} {c}" for w, c in pos_cnt.most_common(10)],
                     "부정": [f"{w} {c}" for w, c in neg_cnt.most_common(10)]})
both
'''),
md("""
**기대값** `EXPECT_POSNEG`

### 1-6. 문맥 확인 — 워드클라우드가 놓치는 것
부정 댓글 워드클라우드에도 `재미`·`재밌다`가 보이고, 가장 큰 글자는 `없다`입니다. 무엇이 없다는 걸까요? **단어가 들어간 원문**을 직접 읽어 봅니다.
"""),
code('''
def kwic(word, df=comments, n=8):
    """단어가 들어간 원문 보기 (Key Word In Context)"""
    hit = df[df["text"].str.contains(word, regex=False)]
    print(f"'{word}' 포함 {len(hit)}건 (감성별 {hit['sentiment'].value_counts().to_dict()})")
    return hit[["comment_id", "sentiment", "text"]].head(n)

# TODO 5: 부정 댓글 중 '재미'가 들어간 원문을 확인하세요.  힌트: kwic("재미", comments[comments["sentiment"] == "부정"])
kwic("재미", comments[comments["sentiment"] == "부정"])
''', todo='''
def kwic(word, df=comments, n=8):
    """단어가 들어간 원문 보기 (Key Word In Context)"""
    hit = df[df["text"].str.contains(word, regex=False)]
    print(f"'{word}' 포함 {len(hit)}건 (감성별 {hit['sentiment'].value_counts().to_dict()})")
    return hit[["comment_id", "sentiment", "text"]].head(n)

# TODO 5: 부정 댓글 중 '재미'가 들어간 원문을 확인하세요.  힌트: kwic("재미", comments[comments["sentiment"] == "부정"])
...
'''),
md("""
부정 댓글의 `재미`는 대부분 **`재미없다`** 입니다. 형태소 분석이 `재미` + `없`으로 나눠 버려 부정의 의미가 사라졌습니다.
간단한 규칙으로 **"명사 (+조사) + 없다/있다"를 한 단어로 붙이면** 워드클라우드가 달라집니다.
(`재미없네`처럼 붙여 쓴 말은 분석기가 이미 `재미없다` 한 단어로 보지만, `재미가 없다`·`재미도 없다`는 둘로 나눕니다.)
"""),
code('''
def morph_tokens_v2(text):
    """명사 뒤에 (조사를 건너뛰고) '없/있'이 오면 한 단어로 붙인다: 재미+없다, 재미+가+없다 → '재미없다'"""
    toks = kiwi.tokenize(str(text)); out = []; i = 0
    while i < len(toks):
        t = toks[i]
        j = i + 1
        while j < len(toks) and toks[j].tag.startswith("J"):     # 조사(J로 시작하는 품사) 건너뛰기
            j += 1
        if t.tag == "NNG" and j < len(toks) and toks[j].tag == "VA" and toks[j].form in ("없", "있"):
            out.append(t.form + toks[j].form + "다"); i = j + 1; continue
        if t.tag in ("NNG", "NNP") and len(t.form) >= 2:
            out.append(t.form)
        elif t.tag == "VA":
            out.append(t.form + "다")
        i += 1
    return [w for w in out if w not in STOP_COMMENT]

neg_cnt_v2 = Counter(w for t in comments.loc[comments["sentiment"] == "부정", "text"] for w in morph_tokens_v2(t))
print("부정 상위 10 (규칙 전):", neg_cnt.most_common(10))
print("부정 상위 10 (규칙 후):", neg_cnt_v2.most_common(10))

fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
for ax, cnt, title in [(axes[0], neg_cnt, "부정 — 규칙 전"), (axes[1], neg_cnt_v2, "부정 — '명사+없다' 붙이기 후")]:
    ax.imshow(make_wc(cnt, "Reds", 60)); ax.axis("off"); ax.set_title(title, fontsize=14)
fig.tight_layout(); fig.savefig("figures/fig_w1_negation_fix.png", dpi=150); plt.show()
'''),
md("""
**기대값** `EXPECT_NEGFIX`

**워크북 1 정리 (워크북 문서에 기록)**
1. 어절과 형태소 방식의 상위 단어가 어떻게 달랐는가? 2. 내가 추가한 불용어와 그 이유는?
3. 긍정/부정 워드클라우드의 차이 3가지. 4. `재미` 사례처럼 **빈도만으로는 틀리게 읽히는 단어**를 하나 더 찾아 `kwic()`으로 확인해 보세요 (예: `최고`, `평점`, `시간`).

---
# 워크북 2 · 뉴스 기사 제목 워드클라우드
```
불러오기·분야 확인 → 명사 빈도(뉴스 불용어) → 전체 워드클라우드 → 분야별 워드클라우드 → 빈도 vs 특징어(TF-IDF)
```
### 2-1. 불러오기와 분야별 건수
"""),
code('''
news = pd.read_csv(io.BytesIO(check_file("week07_news_350.csv")), encoding="utf-8-sig")
print("행·열:", news.shape, "| 기간:", news["date"].min(), "~", news["date"].max())

# TODO 6: 분야(category)별 기사 수를 세세요.  힌트: news["category"].value_counts()
news["category"].value_counts()
''', todo='''
news = pd.read_csv(io.BytesIO(check_file("week07_news_350.csv")), encoding="utf-8-sig")
print("행·열:", news.shape, "| 기간:", news["date"].min(), "~", news["date"].max())

# TODO 6: 분야(category)별 기사 수를 세세요.  힌트: news["category"].value_counts()
...
'''),
code('''
news[["news_id", "category", "title", "date"]].head(8)
'''),
md("""
**기대값** 350행 × 6열 · 2016-01-07 ~ 2019-12-31 · 7개 분야(정치·경제·사회·생활문화·세계·IT과학·스포츠) 각 50건.
`url`로 원문 기사를 찾아갈 수 있습니다(일부는 삭제됐을 수 있음). 원자료에서 따옴표 등 기호가 빠져 `…종합`, `1보`처럼 붙은 꼬리표가 있습니다.

### 2-2. 명사 빈도 — 뉴스용 불용어
뉴스 제목에는 `종합`, `속보`, `게시판`처럼 **기사 형식을 나타내는 말**이 붙습니다. 내용이 아니므로 뺍니다.
"""),
code('''
STOP_NEWS = {"종합", "속보", "1보", "2보", "3보", "게시판", "그래픽", "신간", "오늘", "내일", "올해", "작년", "단독", "포토"}

def news_tokens(text):
    return [t.form for t in kiwi.tokenize(str(text))
            if t.tag in ("NNG", "NNP") and len(t.form) >= 2 and t.form not in STOP_NEWS]

news["tokens"] = news["title"].apply(news_tokens)
news_cnt = Counter(w for toks in news["tokens"] for w in toks)

top_news = pd.DataFrame(news_cnt.most_common(30), columns=["word", "count"])
top_news.insert(0, "rank", range(1, len(top_news) + 1))
top_news.to_csv("results/week07_news_top30.csv", index=False, encoding="utf-8-sig")
bar_top(news_cnt, "뉴스 제목 350건 상위 20개 명사", "fig_w2_news_bar.png", color="#55A868")
show_wc(news_cnt, "뉴스 제목 350건 워드클라우드", "fig_w2_news_wc.png", colormap="cividis")
'''),
md("""
**기대값** `EXPECT_NEWS_TOP`

### 2-3. 분야별 워드클라우드
전체 워드클라우드는 여러 분야가 섞여 특징이 흐려집니다. 분야별로 나눠 그리면 각 분야의 주제가 드러납니다.
"""),
code('''
CATS = ["정치", "경제", "사회", "생활문화", "세계", "IT과학", "스포츠"]
# TODO 7: 분야별 Counter를 dict로 만드세요.  힌트: {c: Counter(w for toks in news.loc[news["category"] == c, "tokens"] for w in toks) for c in CATS}
cat_cnt = {c: Counter(w for toks in news.loc[news["category"] == c, "tokens"] for w in toks) for c in CATS}

fig, axes = plt.subplots(2, 4, figsize=(16, 6.5))
for ax, c in zip(axes.flat, CATS):
    ax.imshow(make_wc(cat_cnt[c], "tab10", 40)); ax.axis("off"); ax.set_title(f"{c} (50건)", fontsize=13)
axes.flat[-1].axis("off")
fig.tight_layout(); fig.savefig("figures/fig_w2_category_wc.png", dpi=150); plt.show()
pd.DataFrame({c: [w for w, _ in cat_cnt[c].most_common(5)] for c in CATS})
''', todo='''
CATS = ["정치", "경제", "사회", "생활문화", "세계", "IT과학", "스포츠"]
# TODO 7: 분야별 Counter를 dict로 만드세요.  힌트: {c: Counter(w for toks in news.loc[news["category"] == c, "tokens"] for w in toks) for c in CATS}
cat_cnt = ...

fig, axes = plt.subplots(2, 4, figsize=(16, 6.5))
for ax, c in zip(axes.flat, CATS):
    ax.imshow(make_wc(cat_cnt[c], "tab10", 40)); ax.axis("off"); ax.set_title(f"{c} (50건)", fontsize=13)
axes.flat[-1].axis("off")
fig.tight_layout(); fig.savefig("figures/fig_w2_category_wc.png", dpi=150); plt.show()
pd.DataFrame({c: [w for w, _ in cat_cnt[c].most_common(5)] for c in CATS})
'''),
md("""
**기대값** `EXPECT_CAT`

### 2-4. 빈도 vs 특징어 (TF-IDF)
빈도 1위가 **그 분야만의 특징**이라고는 할 수 없습니다(`대통령`은 정치·세계 모두에 나옴).
**TF-IDF**는 "이 분야에서는 자주 나오지만 **다른 분야에는 잘 안 나오는** 단어"에 높은 점수를 줍니다.
"""),
code('''
from sklearn.feature_extraction.text import TfidfVectorizer

docs = [" ".join(w for toks in news.loc[news["category"] == c, "tokens"] for w in toks) for c in CATS]  # 분야 1개 = 문서 1개
tfidf = TfidfVectorizer(token_pattern=r"\\S+")
X = tfidf.fit_transform(docs).toarray()
vocab = np.array(tfidf.get_feature_names_out())
tfidf_top = pd.DataFrame({c: vocab[X[i].argsort()[::-1][:5]] for i, c in enumerate(CATS)})
freq_top = pd.DataFrame({c: [w for w, _ in cat_cnt[c].most_common(5)] for c in CATS})
print("[빈도 상위 5]"); display(freq_top)
print("[TF-IDF 특징어 상위 5]"); display(tfidf_top)
'''),
md("""
**기대값** `EXPECT_TFIDF`

**워크북 2 정리** 1. 전체 워드클라우드와 분야별 워드클라우드에서 보이는 것이 어떻게 달랐는가?
2. 뉴스 불용어로 뺀 단어와 그 이유. 3. 빈도 상위와 TF-IDF 상위가 다른 분야를 하나 골라 이유를 설명하세요.
4. 이 제목들은 2016~2019년 연합뉴스 표본입니다. **같은 방법을 오늘 뉴스에 쓰면** 무엇이 달라질까요?

---
# 워크북 3 · AI 요약·키워드와 비교·검증
```
프롬프트 만들기 → AI에 붙여 넣기 → 결과 붙여넣기 → 원문 근거 건수·빈도 순위로 검증 → 일치/차이 정리
```
워드클라우드는 **세는 것**, AI 요약·키워드는 **읽고 해석하는 것**입니다. AI 결과가 원문에 근거하는지 **숫자로** 확인합니다.

### 3-1. 프롬프트 만들기
아래 셀은 **원문 전체**를 담은 프롬프트를 출력하고 파일로도 저장합니다. 출력 상단의 지시문 + 원문을 통째로 복사해
ChatGPT·Gemini·Claude 중 하나에 붙여 넣으세요(새 대화에서). 사용한 **AI 이름·날짜**를 기록합니다.
"""),
code('''
PROMPT_HEAD = """다음은 {label} {n}건입니다. 아래 원문만 근거로 답하세요. 원문에 없는 내용은 추측하지 마세요.
1) 전체 내용을 3문장으로 요약
2) 핵심 키워드 5개 (원문에 실제로 나오는 낱말 위주)
3) 각 키워드마다 근거가 되는 원문 번호 2개
형식:
요약: ...
키워드: 단어1, 단어2, 단어3, 단어4, 단어5
근거: 단어1-번호,번호 / 단어2-번호,번호 / ...
---
"""

def make_prompt(df, id_col, text_col, label):
    body = "\\n".join(f"{i} {t}" for i, t in zip(df[id_col], df[text_col]))
    return PROMPT_HEAD.format(label=label, n=len(df)) + body

prompt_comment = make_prompt(comments, "comment_id", "text", "영화 관람객 댓글")
prompt_news = make_prompt(news, "news_id", "title", "뉴스 기사 제목")
open("results/prompt_comments.txt", "w", encoding="utf-8").write(prompt_comment)
open("results/prompt_news.txt", "w", encoding="utf-8").write(prompt_news)
print(f"댓글 프롬프트 {len(prompt_comment):,}자 · 뉴스 프롬프트 {len(prompt_news):,}자 → results/ 폴더에 저장")
print(prompt_comment[:700], "\\n...(이하 생략: 파일 또는 아래 셀로 전체 복사)")
'''),
code('''
# 전체 프롬프트 출력 (필요할 때만 실행해서 복사)  →  print(prompt_comment)  또는  print(prompt_news)
# Colab 왼쪽 '파일' 창에서 results/prompt_comments.txt 를 내려받아 열어도 된다.
'''),
md("""
### 3-2. AI 결과 붙여넣기
AI 답변의 **요약**과 **키워드 5개**를 아래에 붙여 넣습니다. 완성본에는 **예시 결과**가 들어 있습니다
(Claude로 2026-10-15에 생성 — 매번 결과가 달라지므로 **여러분이 받은 결과로 바꿔서** 검증하세요).
"""),
code(f'''
AI_NAME = "Claude (예시, 2026-10-15)"      # 사용한 AI 이름과 날짜로 바꾸기
{AI_COMMENT_EXAMPLE}
{AI_NEWS_EXAMPLE}
print("댓글 AI 키워드:", ai_comment_keywords)
print("뉴스 AI 키워드:", ai_news_keywords)
''', todo='''
AI_NAME = "..."      # 사용한 AI 이름과 날짜 (예: "ChatGPT, 2026-10-16")
# TODO 8: AI 답변을 붙여 넣으세요. 키워드는 따옴표로 감싼 문자열 5개.
ai_comment_summary = """..."""
ai_comment_keywords = ["...", "...", "...", "...", "..."]
ai_news_summary = """..."""
ai_news_keywords = ["...", "...", "...", "...", "..."]
print("댓글 AI 키워드:", ai_comment_keywords)
print("뉴스 AI 키워드:", ai_news_keywords)
'''),
md("""
### 3-3. AI 키워드 검증 — 원문 근거 건수와 빈도 순위
키워드마다 ① 원문 몇 건에 들어 있는지(**근거 건수**) ② 워드클라우드 빈도표에서 몇 위인지 ③ 실제 원문 예시를 확인합니다.
- 근거 0건 → 원문에 없는 말(**AI가 만들어 낸 표현**이거나 다른 말로 바꾼 것)
- 근거는 있는데 `빈도순위`가 `-` → 빈도표에 그 낱말이 없음: **불용어로 뺐거나**(예: `평점`) 형태소 분석이 다르게 잘랐기 때문(예: `지루`는 `지루하다`의 일부라 명사로 세지 않음)
- `str.contains`는 글자가 포함되기만 하면 셉니다. `재미` 30건에는 `재미없다`도 들어 있으므로 **근거 건수가 곧 긍정 근거는 아닙니다** → 원문예시를 읽고 판단
"""),
code('''
def verify_keywords(keywords, df, text_col, id_col, counter, label):
    rank = {w: i + 1 for i, (w, _) in enumerate(counter.most_common())}
    rows = []
    for k in keywords:
        hit = df[df[text_col].str.contains(k, regex=False)]
        r = rank.get(k)
        rows.append({"자료": label, "AI키워드": k, "근거건수": len(hit),
                     "빈도순위": r if r else "-",
                     "판정": ("근거 없음" if len(hit) == 0 else "빈도 상위10" if r and r <= 10
                               else "근거 있음·빈도 하위" if r else "근거 있음·빈도표에 없음"),
                     "원문예시": (hit[id_col].iloc[0] + " " + hit[text_col].iloc[0][:40]) if len(hit) else ""})
    return pd.DataFrame(rows)

check = pd.concat([verify_keywords(ai_comment_keywords, comments, "text", "comment_id", comment_cnt, "댓글"),
                   verify_keywords(ai_news_keywords, news, "title", "news_id", news_cnt, "뉴스")], ignore_index=True)
check.to_csv("results/week07_ai_keyword_check.csv", index=False, encoding="utf-8-sig")
check
'''),
md("""
**기대값 (예시 키워드 기준)** `EXPECT_VERIFY`

### 3-4. 빈도 상위 10 vs AI 키워드 — 일치와 차이
"""),
code('''
# TODO 9: 빈도 상위 10개 단어 집합과 AI 키워드 집합의 교집합·차집합을 구하세요.
#   힌트: set(w for w, _ in comment_cnt.most_common(10)) & set(ai_comment_keywords)
def overlap(counter, keywords, label):
    freq10 = set(w for w, _ in counter.most_common(10))
    ai = set(keywords)
    return {"자료": label, "둘 다": sorted(freq10 & ai), "AI만": sorted(ai - freq10),
            "빈도만": sorted(freq10 - ai), "일치 개수": len(freq10 & ai)}

ov = pd.DataFrame([overlap(comment_cnt, ai_comment_keywords, "댓글"), overlap(news_cnt, ai_news_keywords, "뉴스")])
ov
''', todo='''
# TODO 9: 빈도 상위 10개 단어 집합과 AI 키워드 집합의 교집합·차집합을 구하세요.
#   힌트: set(w for w, _ in comment_cnt.most_common(10)) & set(ai_comment_keywords)
def overlap(counter, keywords, label):
    freq10 = ...
    ai = set(keywords)
    return {"자료": label, "둘 다": sorted(freq10 & ai), "AI만": sorted(ai - freq10),
            "빈도만": sorted(freq10 - ai), "일치 개수": len(freq10 & ai)}

ov = pd.DataFrame([overlap(comment_cnt, ai_comment_keywords, "댓글"), overlap(news_cnt, ai_news_keywords, "뉴스")])
ov
'''),
code('''
# 워드클라우드 위에 AI 키워드만 빨간색으로 표시 → 빈도와 AI 판단이 어디서 겹치는지 한눈에
def highlight(keywords):
    ks = set(keywords)
    return lambda word, **kw: "#D62728" if word in ks else "#B0B0B0"

fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
for ax, cnt, ks, title in [(axes[0], comment_cnt, ai_comment_keywords, "댓글"), (axes[1], news_cnt, ai_news_keywords, "뉴스")]:
    ax.imshow(make_wc(cnt).recolor(color_func=highlight(ks), random_state=42)); ax.axis("off")
    ax.set_title(f"{title}: 빨강 = AI 키워드, 회색 = 그 밖의 빈도 단어", fontsize=12)
fig.tight_layout(); fig.savefig("figures/fig_w3_ai_overlay.png", dpi=150); plt.show()
'''),
md("""
**기대값** `EXPECT_OVERLAP`

### 3-5. AI 요약 문장 확인
요약 문장 속 주장마다 **근거 원문 번호**를 찾아 적습니다. AI가 제시한 근거 번호가 실제로 그 내용인지 아래처럼 확인합니다.
"""),
code('''
def show_ids(ids, df=comments, id_col="comment_id", text_col="text"):
    return df[df[id_col].isin(ids)][[id_col, text_col]]

print(ai_comment_summary)
show_ids(["C115", "C062", "C169", "C205"])        # AI 답변의 '근거' 번호로 바꿔서 확인
'''),
md("""
**최종 비교표 (워크북 3 문서에 작성)**

| 기준 | 워드클라우드(빈도) | AI 요약·키워드 | 내 관찰 |
|---|---|---|---|
| 무엇을 근거로 | 단어 등장 횟수 | 문장의 의미·문맥 | |
| 잘한 점 | 같은 입력이면 항상 같은 결과, 숫자로 확인 가능 | 부정·대조(`재미없다`)를 읽음, 문장으로 요약 | |
| 한계 | 문맥·부정 손실, 토큰화·불용어에 따라 달라짐 | 매번 다름, 원문에 없는 말 가능, 근거 확인 필요 | |
| 일치한 키워드 | | | |

### 결과 내려받기
"""),
code('''
import shutil
shutil.make_archive("week07_results", "zip", ".", "results")
shutil.make_archive("week07_figures", "zip", ".", "figures")
print(sorted(os.listdir("results")), sorted(os.listdir("figures")), sep="\\n")
try:
    from google.colab import files
    files.download("week07_results.zip"); files.download("week07_figures.zip")
except ImportError:
    print("Colab이 아니므로 다운로드 창은 생략 (zip 파일은 현재 폴더에 있음)")
'''),
md("""
---
### [선택] Colab 안에서 AI 직접 호출하기
Colab의 `google.colab.ai`(Gemini 등)를 쓸 수 있는 계정이면 키 없이 바로 결과를 받을 수 있습니다.
사용 가능 여부·한도는 계정마다 다르며, 안 되면 위 3-1처럼 복사·붙여넣기로 진행합니다. 결과는 3-2 셀에 옮겨 적습니다.
"""),
code('''
RUN_COLAB_AI = False        # True로 바꾸고 실행
if RUN_COLAB_AI:
    try:
        from google.colab import ai
        print("사용 가능한 모델:", ai.list_models())
        print(ai.generate_text(prompt_comment))
    except Exception as e:
        print("Colab AI를 사용할 수 없습니다 → 프롬프트 복사 방식으로 진행하세요:", type(e).__name__, e)
else:
    print("건너뜀: RUN_COLAB_AI = True 로 바꾸면 실행")
'''),
    ]
