# 워크북 3 · AI 요약·키워드와 비교·검증

> 🎯 <b>목표</b> 같은 원문으로 AI 요약·키워드를 받아 **원문 근거 건수 · 빈도 순위 · 원문 대조**로 검증하고, 워드클라우드(빈도)와의 일치·차이·한계를 정리한다.

<b>노트북</b> [실습본](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_텍스트시각화_실습.ipynb) · [완성본](https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/Week07_텍스트시각화_완성.ipynb) — 이 페이지의 <b>▶ 셀 번호</b>와 노트북의 셀 번호·코드가 같습니다. 위에서부터 읽으며 같은 번호 셀을 <code>Shift+Enter</code>로 하나씩 실행하고, <b>실행 결과</b>·<b>✔ 실행 후 확인</b>과 비교합니다.

| 단계 | 셀 | 하는 일 |
| --- | --- | --- |
| 1단계. AI에게 줄 프롬프트 만들기 | 3-1 ~ 3-2 | 원문 전체가 들어간 프롬프트 만들어 저장, 프롬프트 전체 출력 (복사할 때만) |
| 2단계. AI 결과 붙여 넣기 | 3-3 (TODO 1) | AI 요약·키워드 붙여 넣기 |
| 3단계. AI 키워드 검증 — 근거 건수와 빈도 순위 | 3-4 | 키워드마다 근거 건수·빈도 순위·원문 예시 |
| 4단계. 빈도 상위 10 vs AI 키워드 — 일치와 차이 | 3-5 ~ 3-6 (TODO 1) | 교집합·차집합으로 비교, 워드클라우드 위에 AI 키워드 표시 |
| 5단계. AI 요약 문장 확인 — 근거 번호의 원문 읽기 | 3-7 | 근거 번호의 원문 열어 보기 |
| 6단계. 결과 내려받기와 정리 | 3-8 ~ 3-9 | 결과 zip 만들어 내려받기, [선택] Colab 안에서 AI 직접 호출 |

## 1단계. AI에게 줄 프롬프트 만들기

워드클라우드는 **세는 것**, AI 요약·키워드는 **읽고 해석하는 것**입니다. 두 결과를 공정하게 비교하려면 **같은 원문 전체**를 AI에게 줘야 합니다.

좋은 프롬프트의 조건:
- **근거를 원문으로 한정**: "아래 원문만 근거로, 없는 내용은 추측하지 마세요"
- **형식 지정**: 요약 3문장 · 키워드 5개 · 키워드마다 근거 원문 번호 2개 → 나중에 번호로 검증 가능
- **번호 붙인 원문**: `C001 …`, `N001 …` → AI가 근거를 번호로 댈 수 있음

**AI에 붙여 넣는 방법**
1. ChatGPT · Gemini · Claude 중 하나에서 **새 대화**를 엽니다(이전 대화 내용이 섞이지 않게).
2. 셀 3-2의 `# print(prompt_comment)` 앞 `#`을 지우고 실행 → 출력 전체 복사(또는 `results/prompt_comments.txt` 열기) → 붙여 넣기.
3. 답을 받으면 **AI 이름과 날짜**를 기록합니다. 같은 프롬프트로 뉴스(`prompt_news`)도 한 번 더 합니다.
4. AI 답은 매번 달라집니다. 친구와 결과가 다른 것이 정상입니다.

### ▶ 셀 3-1. 원문 전체가 들어간 프롬프트 만들어 저장

```python
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
    body = "\n".join(f"{i} {t}" for i, t in zip(df[id_col], df[text_col]))
    return PROMPT_HEAD.format(label=label, n=len(df)) + body

prompt_comment = make_prompt(comments, "comment_id", "text", "영화 관람객 댓글")
prompt_news = make_prompt(news, "news_id", "title", "뉴스 기사 제목")
open("results/prompt_comments.txt", "w", encoding="utf-8").write(prompt_comment)
open("results/prompt_news.txt", "w", encoding="utf-8").write(prompt_news)
print(f"댓글 프롬프트 {len(prompt_comment):,}자 · 뉴스 프롬프트 {len(prompt_news):,}자 → results/ 폴더에 저장")
print(prompt_comment[:500], "\n...(이하 생략)")
```

<b>실행 결과</b>

```text
댓글 프롬프트 12,496자 · 뉴스 프롬프트 11,845자 → results/ 폴더에 저장
다음은 영화 관람객 댓글 300건입니다. 아래 원문만 근거로 답하세요. 원문에 없는 내용은 추측하지 마세요.
1) 전체 내용을 3문장으로 요약
2) 핵심 키워드 5개 (원문에 실제로 나오는 낱말 위주)
3) 각 키워드마다 근거가 되는 원문 번호 2개
형식:
요약: ...
키워드: 단어1, 단어2, 단어3, 단어4, 단어5
근거: 단어1-번호,번호 / 단어2-번호,번호 / ...
---
C001 폴워커의 유작이라 기대됨 근데 개봉관이 왜 없??
C002 내가유일하게싫어하는왕가위영화..국영이형죄송ㅋ
C003 빨간 망토의 현대적 재해석은 커녕 늑대인간 컨셉을 어거지로 끼워 맞춘 하이틴 로맨스, 딱 이 감독의 전작인 트와일라잇 수준의 영화... 백설 속의 빨간 망토 이미지만이 도드라지고 내용은 패륜과 막장 드라마
C004 도통 무슨내용인지..지금 보고있는데 잠만오는듯..
C005 화끈한 액션이 볼만함
C006 스릴이 부실하면 볼거리라도 있어야지
C007 무서운 영화였어. 그리고 두 남매가  
...(이하 생략)
```

✔ <b>실행 후 확인:</b> `댓글 프롬프트 12,496자 · 뉴스 프롬프트 11,845자` + 지시문과 `C001 폴워커의 …` 시작 부분

<b>코드 읽기</b>

- `"""여러 줄 문자열"""` — 따옴표 세 개: 줄바꿈을 그대로 담는 문자열
- `PROMPT_HEAD.format(label=…, n=…)` — 문자열 안의 `{label}`, `{n}` 자리에 값을 채움
- `"\n".join(…)` — 줄바꿈으로 이어 붙이기 → 한 줄에 원문 하나
- `zip(df[id_col], df[text_col])` — 번호와 원문을 짝지어 하나씩

### ▶ 셀 3-2. 프롬프트 전체 출력 (복사할 때만)

```python
# 필요할 때만 # 를 지우고 실행해서 출력 전체를 복사 → AI 새 대화에 붙여 넣기
# print(prompt_comment)
# print(prompt_news)
# 또는 왼쪽 📁 창 results/prompt_comments.txt 를 내려받아 열기
```

✔ <b>실행 후 확인:</b> 출력 없음(주석). 복사할 때 `#`을 지우고 실행

<b>코드 읽기</b>

- `# 코드` — 주석이라 실행되지 않음. `#`을 지우면 실행됨

## 2단계. AI 결과 붙여 넣기

AI 답의 **요약**과 **키워드 5개**를 노트북 변수에 옮겨 적습니다. 완성본에는 **예시 결과**(Claude, 2026-10-15)가 들어 있습니다 —
**여러분이 받은 결과로 바꿔서** 검증하세요.

### ▶ 셀 3-3. AI 요약·키워드 붙여 넣기

```python
AI_NAME = "Claude (예시, 2026-10-15)"      # 사용한 AI 이름과 날짜로 바꾸기
ai_comment_summary = """1) 댓글은 긍정과 부정이 반반으로, 긍정 댓글은 배우의 연기와 감동·눈물, 다시 보고 싶을 만큼의 재미를 칭찬한다(C115, C062).
2) 부정 댓글은 지루함, 뻔하거나 억지스러운 줄거리, 시간·돈이 아깝다는 불만이 중심이다(C169, C205).
3) 연기는 좋지만 내용이 아쉽다는 엇갈린 평가와, 평점이 너무 높거나 낮다는 평점 불신도 자주 보인다(C148, C071)."""
ai_comment_keywords = ["연기", "감동", "재미", "지루", "평점"]
ai_news_summary = """1) 2016~2019년 기사 제목으로 정치·경제·사회·생활문화·세계·IT과학·스포츠 7개 분야가 고르게 섞여 있다.
2) 정치·세계 분야는 대통령과 정상회담, 북한, 미국·이란 등 국제 갈등을, 경제·IT과학 분야는 코스피·금리와 스마트폰 출시를 주로 다룬다(N125, N089, N002).
3) 생활문화는 폭염·한파 등 날씨, 스포츠는 류현진 등 해외 리그 한국 선수와 프로농구 소식이 많다(N072, N040)."""
ai_news_keywords = ["대통령", "북한", "스마트폰", "코스피", "폭염"]
print("댓글 AI 키워드:", ai_comment_keywords)
print("뉴스 AI 키워드:", ai_news_keywords)
```

> ✏️ 실습본에서는 <code># TODO</code> 아래 줄이 <code>...</code>으로 비어 있습니다. 먼저 힌트를 보고 직접 써서 실행한 뒤, 막히면 위 코드와 비교하세요.

<b>실행 결과</b>

```text
댓글 AI 키워드: ['연기', '감동', '재미', '지루', '평점']
뉴스 AI 키워드: ['대통령', '북한', '스마트폰', '코스피', '폭염']
```

✔ <b>실행 후 확인:</b> 키워드 목록 두 줄. 실습본은 `"..."`를 내 AI 결과로 바꾸지 않으면 다음 셀에서 근거 0건으로 나옴

<b>코드 읽기</b>

- `["연기", "감동", …]` — 리스트: 따옴표로 감싼 문자열 5개를 쉼표로
- `"""…"""` — 요약은 여러 줄이라 따옴표 세 개로 감쌈

## 3단계. AI 키워드 검증 — 근거 건수와 빈도 순위

AI 키워드마다 세 가지를 확인합니다.

| 확인 | 방법 | 결과 해석 |
|---|---|---|
| ① 근거 건수 | 키워드가 들어간 원문이 몇 건인가 | **0건** → 원문에 없는 말(AI가 바꿔 말했거나 만들어 냄) |
| ② 빈도 순위 | 워크북 1·2 빈도표에서 몇 위인가 | `-` → 빈도표에 없음: 불용어로 뺐거나(`평점`) 형태소 분석이 다르게 자름(`지루`→`지루하다`) |
| ③ 원문 예시 | 실제로 들어간 문장 읽기 | `재미` 30건에는 `재미없다`도 섞임 → **건수가 많다고 긍정 근거는 아님** |

### ▶ 셀 3-4. 키워드마다 근거 건수·빈도 순위·원문 예시

```python
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
```

<b>실행 결과</b>

```text
   자료 AI키워드  근거건수 빈도순위             판정                                           원문예시
0  댓글    연기    24    3        빈도 상위10  C009 집에서 따뜻해지기 좋은영화. 이연희랑 역할도 잘어울리고 연기도 좋았슴 전
1  댓글    감동     8   15    근거 있음·빈도 하위  C062 진짜 편한 마음으로 봤는데 내 눈물까지 본 영화 ㅜㅜ감동적이고 계속 더 
2  댓글    재미    30   12    근거 있음·빈도 하위          C014 내용 증말 재미없네.긴장감이나 스릴감이 전혀 느켜지지 않아
3  댓글    지루     9    -  근거 있음·빈도표에 없음  C036 특별한건 없지만 그것이 매력인 영화인거 같아요. 소박하면서도 꾸며지지 않
4  댓글    평점    10    -  근거 있음·빈도표에 없음         C026 몸만 어른인 청춘들의 객기만을 보는듯.... 평점이 넘 높네
5  뉴스   대통령    15    1        빈도 상위10                 N078 靑 대통령 겨냥했다 판단…각종 의혹에 단호대응
6  뉴스    북한     4   54    근거 있음·빈도 하위                        N083 북한 건군절 70주년 기념 열병식
7  뉴스  스마트폰     2  326    근거 있음·빈도 하위               N243 삼성·LG 연말 스마트폰 시장 한정판·명품 마케팅
8  뉴스   코스피     3  116    근거 있음·빈도 하위                      N089 코스피 상승 마감…2010선 회복1보
9  뉴스    폭염     5   21    근거 있음·빈도 하위            N025 폭염도시 대구 온열 질환자가 전국에서 가장 적은 이유는
```

✔ <b>실행 후 확인:</b> (예시 기준) 근거 0건 없음 · `연기` 24건·3위 · `재미` 30건·12위(원문예시가 `재미없네`) · `지루`·`평점`은 빈도표에 없음 · `대통령` 15건·1위 · `스마트폰` 2건·326위

<b>코드 읽기</b>

- `{w: i + 1 for i, (w, _) in enumerate(…)}` — 단어 → 순위 사전. enumerate는 0부터 번호를 붙임
- `rank.get(k)` — 사전에 없으면 None(오류 아님)
- `A if 조건1 else B if 조건2 else C` — 조건 여러 개를 이어 쓴 조건 표현식
- `hit[id_col].iloc[0]` — 찾은 행 중 첫 번째의 번호
- `pd.concat([표1, 표2], ignore_index=True)` — 두 표를 위아래로 이어 붙이고 행 번호를 새로

## 4단계. 빈도 상위 10 vs AI 키워드 — 일치와 차이

**집합 연산**으로 두 결과를 비교합니다: 둘 다 고른 단어(교집합), AI만 고른 단어, 빈도에만 있는 단어(차집합).
그리고 워드클라우드 위에 AI 키워드만 빨간색으로 칠해 **빈도와 AI 판단이 어디서 겹치는지** 봅니다.

### ▶ 셀 3-5. 교집합·차집합으로 비교

```python
# TODO 9: 빈도 상위 10개 단어 집합과 AI 키워드 집합의 교집합·차집합을 구하세요.
#   힌트: set(w for w, _ in comment_cnt.most_common(10)) & set(ai_comment_keywords)
def overlap(counter, keywords, label):
    freq10 = set(w for w, _ in counter.most_common(10))
    ai = set(keywords)
    return {"자료": label, "둘 다": sorted(freq10 & ai), "AI만": sorted(ai - freq10),
            "빈도만": sorted(freq10 - ai), "일치 개수": len(freq10 & ai)}

pd.DataFrame([overlap(comment_cnt, ai_comment_keywords, "댓글"), overlap(news_cnt, ai_news_keywords, "뉴스")])
```

> ✏️ 실습본에서는 <code># TODO</code> 아래 줄이 <code>...</code>으로 비어 있습니다. 먼저 힌트를 보고 직접 써서 실행한 뒤, 막히면 위 코드와 비교하세요.

<b>실행 결과</b>

```text
   자료    둘 다                  AI만                                       빈도만  일치 개수
0  댓글   [연기]     [감동, 재미, 지루, 평점]  [감독, 기대, 내용, 스토리, 없다, 장면, 재미있다, 재밌다, 좋다]      1
1  뉴스  [대통령]  [북한, 스마트폰, 코스피, 폭염]      [감독, 개발, 삼성, 이란, 정부, 정상, 최고, 추가, 한국]      1
```

✔ <b>실행 후 확인:</b> (예시 기준) 일치 댓글 1개(`연기`), 뉴스 1개(`대통령`). AI만: `감동·재미·지루·평점`, `북한·스마트폰·코스피·폭염`

<b>코드 읽기</b>

- `set(…)` — 집합으로 바꾸기
- `A & B` — 교집합: 둘 다 있는 것
- `A - B` — 차집합: A에만 있는 것
- `sorted(집합)` — 가나다순 목록으로

### ▶ 셀 3-6. 워드클라우드 위에 AI 키워드 표시

```python
def highlight(keywords):
    ks = set(keywords)
    return lambda word, **kw: "#D62728" if word in ks else "#B0B0B0"   # AI 키워드면 빨강, 아니면 회색

fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
for ax, cnt, ks, title in [(axes[0], comment_cnt, ai_comment_keywords, "댓글"), (axes[1], news_cnt, ai_news_keywords, "뉴스")]:
    ax.imshow(make_wc(cnt).recolor(color_func=highlight(ks), random_state=42)); ax.axis("off")
    ax.set_title(f"{title}: 빨강 = AI 키워드, 회색 = 그 밖의 빈도 단어", fontsize=12)
fig.tight_layout(); fig.savefig("figures/fig_w3_ai_overlay.png", dpi=150); plt.show()
```

![셀 3-6 실행 결과 — fig_w3_ai_overlay.png](https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week07/figures/fig_w3_ai_overlay.png)

✔ <b>실행 후 확인:</b> 빨간 글자가 크면 빈도와 AI가 일치, 작거나 없으면 AI가 빈도가 낮은 말을 고른 것

<b>코드 읽기</b>

- `lambda word, **kw: …` — 이름 없는 짧은 함수. 워드클라우드가 단어마다 불러 색을 정함
- `make_wc(cnt).recolor(color_func=…)` — 같은 배치에 색만 다시 칠함

## 5단계. AI 요약 문장 확인 — 근거 번호의 원문 읽기

AI가 댄 근거 번호가 **실제 원문 번호이더라도 내용이 주장과 다를 수 있습니다**.
(이 자료를 만들 때도 예시 답에서 "연기는 좋지만 내용이 아쉽다"의 근거로 댄 번호가 실제로는 연기를 비판하는 댓글이어서 고쳤습니다.)
요약 문장마다 근거 번호를 열어 읽고 **O / X / 일부**로 판정해 검증 기록지에 적습니다.

### ▶ 셀 3-7. 근거 번호의 원문 열어 보기

```python
def show_ids(ids, df=comments, id_col="comment_id", text_col="text"):
    return df[df[id_col].isin(ids)][[id_col, text_col]]

print(ai_comment_summary)
show_ids(["C115", "C062", "C169", "C205"])        # AI 답변의 '근거' 번호로 바꿔서 확인
```

<b>실행 결과</b>

```text
1) 댓글은 긍정과 부정이 반반으로, 긍정 댓글은 배우의 연기와 감동·눈물, 다시 보고 싶을 만큼의 재미를 칭찬한다(C115, C062).
2) 부정 댓글은 지루함, 뻔하거나 억지스러운 줄거리, 시간·돈이 아깝다는 불만이 중심이다(C169, C205).
3) 연기는 좋지만 내용이 아쉽다는 엇갈린 평가와, 평점이 너무 높거나 낮다는 평점 불신도 자주 보인다(C148, C071).
    comment_id                                                         text
61        C062  진짜 편한 마음으로 봤는데 내 눈물까지 본 영화 ㅜㅜ감동적이고 계속 더 봐도 마음 훈훈해질것 같아요....
114       C115                  최민식의 연기가 압권이었다.소재는 뻔하지만 극전개 분위기도 좋고 여운도 남구.
168       C169                                           지루해둑는줄. 과정뻔해 결과뻔해.
204       C205  이거 재밌다는 사람은 스릴러 처음 봤음? 너무 엉성한 시나리오. 맥 빠지는 연출력. 개연성 없는 전후...
```

✔ <b>실행 후 확인:</b> 요약 3문장과 근거 원문 4건. 각 원문이 요약의 주장(연기 칭찬·감동, 지루함·시간 아까움)과 맞는지 읽어 보기

<b>코드 읽기</b>

- `df[id_col].isin(ids)` — 번호가 목록 안에 있으면 True
- `show_ids(…, df=news, id_col="news_id", text_col="title")` — 뉴스 근거를 볼 때

🔁 <b>직접 바꿔 보기:</b> 뉴스 요약의 근거도 `show_ids(["N125", "N089"], df=news, id_col="news_id", text_col="title")`로 확인하세요.

## 6단계. 결과 내려받기와 정리

`results/`(CSV 3개·프롬프트 2개)와 `figures/`(그림 8장)를 zip으로 묶어 내려받아 제출합니다.

| 기준 | 워드클라우드(빈도) | AI 요약·키워드 | 내 관찰 |
|---|---|---|---|
| 무엇을 근거로 | 단어 등장 횟수 | 문장의 의미·문맥 | |
| 재현성 | 같은 입력이면 항상 같음 | 매번 다름, AI·날짜마다 다름 | |
| 잘한 점 | 숫자로 확인 가능 | 부정·대조를 읽고 문장으로 요약 | |
| 한계 | 문맥·부정 손실, 토큰화·불용어 영향 | 원문에 없는 말, 근거 번호 오류 가능 | |
| 일치한 키워드 | | | |

### ▶ 셀 3-8. 결과 zip 만들어 내려받기

```python
import shutil
shutil.make_archive("week07_results", "zip", ".", "results")
shutil.make_archive("week07_figures", "zip", ".", "figures")
print(sorted(os.listdir("results")), sorted(os.listdir("figures")), sep="\n")
try:
    from google.colab import files
    files.download("week07_results.zip"); files.download("week07_figures.zip")
except ImportError:
    print("Colab이 아니므로 다운로드 창은 생략 (zip 파일은 현재 폴더에 있음)")
```

<b>실행 결과</b>

```text
['prompt_comments.txt', 'prompt_news.txt', 'week07_ai_keyword_check.csv', 'week07_comment_top30.csv', 'week07_news_top30.csv']
['fig_w1_comment_bar.png', 'fig_w1_comment_wc.png', 'fig_w1_negation_fix.png', 'fig_w1_pos_neg_wc.png', 'fig_w2_category_wc.png', 'fig_w2_news_bar.png', 'fig_w2_news_wc.png', 'fig_w3_ai_overlay.png', 'test_bar.png']
(Colab에서는 여기서 week07_results.zip, week07_figures.zip 두 파일이 내려받아짐)
```

✔ <b>실행 후 확인:</b> results 5개(CSV 3·프롬프트 2), figures 9개(그림 8 + 시험 막대그래프) 목록, 브라우저에서 zip 2개 다운로드

<b>코드 읽기</b>

- `shutil.make_archive(이름, "zip", 기준폴더, 묶을폴더)` — 폴더를 zip 파일로 묶기
- `files.download(파일)` — Colab에서 내 컴퓨터로 내려받기

### ▶ 셀 3-9. [선택] Colab 안에서 AI 직접 호출

```python
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
```

<b>실행 결과</b>

```text
건너뜀: RUN_COLAB_AI = True 로 바꾸면 실행
```

✔ <b>실행 후 확인:</b> `건너뜀`. 계정에 따라 Colab AI(Gemini 등)를 키 없이 쓸 수 있으며, 안 되면 3-1의 복사 방식으로 진행

<b>코드 읽기</b>

- `from google.colab import ai` — Colab이 제공하는 AI 도구(계정·시기에 따라 사용 가능 여부 다름)

## 정리

**제출 체크리스트**
- [ ] 데이터 출처(NSMC CC0, KLUE-YNAT CC BY-SA 4.0)와 표본 크기 기록
- [ ] 토큰화 방법·불용어 목록 기록
- [ ] `week07_figures.zip`, `week07_results.zip`
- [ ] AI 이름·날짜, 요약 3문장·키워드 5개 × 2 자료
- [ ] 검증 기록지: 근거 번호를 열어 확인한 결과(O/X/일부)
- [ ] 결론: 두 방법을 언제 각각 쓰면 좋은가 (3문장)
