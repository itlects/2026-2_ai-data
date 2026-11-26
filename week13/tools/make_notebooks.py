"""13주차 노트북 생성기: 학생 워크북과 강의자 시연 완성본을 같은 코드로 만든다.

python tools/make_notebooks.py → notebooks/ 아래 두 ipynb 생성
(완성본의 실행 결과는 jupyter nbconvert --execute 로 채운다)
"""
from pathlib import Path
import json

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
IDS = json.loads((ROOT / "tools" / "drive_ids.json").read_text(encoding="utf-8"))
OFFLINE = json.loads((ROOT / "materials" / "offline_examples.json").read_text(encoding="utf-8"))
DATA_NAME = "daegu_2025_daily.csv"
RAW = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/week13"

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell


def fill(s: str) -> str:
    return (s.replace("@@DRIVE_ID@@", IDS[DATA_NAME])
             .replace("@@DRIVE_FOLDER@@", IDS["folder_01"])
             .replace("@@RAW@@", RAW)
             .replace("@@DATA@@", DATA_NAME))


def pystr(s: str) -> str:
    """문자열을 노트북 코드 안의 삼중따옴표 문자열로."""
    return '"""' + s.replace('\\', '\\\\').replace('"""', '\\"\\"\\"') + '"""'


# ---------------------------------------------------------------- 기록 칸 예시 답
EX = {
    "student_id": "강의자예시",
    "human": OFFLINE["human_example"],
    "final": OFFLINE["final_example"],
    "guess": "B",
    "scores": {"A": {"정확성": 4, "읽고 싶음": 5, "행동 유도": 4},
               "B": {"정확성": 5, "읽고 싶음": 3, "행동 유도": 3}},
    "answers": {
        "Q1_v1에서_사실표에_없는_숫자와_그_출처":
            "8개(16.1, 39.8, 41, 30, 520, 1,180, 12.3, 2026). '8월 2일'처럼 사실표에 있는 숫자(8, 2)로 이루어진 틀린 날짜는 걸러지지 않았다. 데이터를 주지 않았는데도 AI가 '대구는 덥다'는 일반적인 패턴으로 그럴듯한 숫자를 지어냈다.",
        "Q2_가장_효과가_컸던_프롬프트_요소와_이유":
            "v2의 '근거 데이터'. 사실표를 넣자 사실표에 없는 숫자가 8개에서 0개로 줄었다. 형식은 v3의 출력 형식 지정, 문체는 v4의 예시가 가장 크게 바꿨다.",
        "Q3_숫자_검사를_통과했는데도_사람이_고친_부분":
            "v4가 '가장 추운 달은 1월'이라고 썼는데 사실표는 2월(평균 1.2°C)이다. 숫자가 없는 문장이라 자동 검사로는 잡히지 않았다. '39일'은 사실표에 없다고 표시됐지만 18+21=39로 맞는 계산이라 그대로 두었다.",
        "Q4_블라인드_비교에서_알게_된_점":
            "짝은 사람 글(B)을 AI로 골라 맞히지 못했다. AI 글이 '읽고 싶음' 점수는 더 높았지만 정확성은 사람 글이 높았다. 문장력은 AI가, 사실 확인은 사람이 강했다.",
        "Q5_AI_사용_기록":
            "Colab 내장 Gemini(google.colab.ai, 기본 모델), 2026-12-03. v1~v4 카드뉴스 초안 생성에 사용. 최종 문구는 사람이 사실표와 대조해 수정했다.",
    },
}
EMPTY_ANS = {k: "" for k in EX["answers"]}


def build(completed: bool):
    c = []
    add_md = lambda s: c.append(md(fill(s)))
    add_code = lambda s: c.append(code(fill(s)))
    title = "강의자 시연 완성본" if completed else "학생 워크북"

    add_md(f"""# 13주차 {title} — 생성형 AI 콘텐츠 제작
인공지능과 데이터 활용 · 2026-2학기 · 120분

**오늘의 질문:** AI에게 "2025년 대구 날씨 카드뉴스 만들어 줘"라고 하면, 그 숫자를 믿고 SNS에 올려도 될까? 그리고 사람이 쓴 카드뉴스와 AI가 쓴 카드뉴스, 친구는 구별할 수 있을까?

**오늘 만드는 것:** 2025년 대구 날씨를 정리한 **인스타그램 카드뉴스 4장(PNG)** — 실제 기상청 관측자료로 만들고, 바로 게시할 수 있는 수준까지 다듬습니다.

| 단계 | 내용 | 결과물 |
|---|---|---|
| 0~1 | 준비, 2025년 대구 일자료 불러오기 | 365행 × 5열 |
| 2 | **데이터에서 사실 뽑기** (pandas) | 사실표 13줄, 그림 1장 |
| 3 | ✍️ **사람 버전 먼저** — AI 없이 카드 4장 문구 쓰기 | 사람 문구 |
| 4~7 | **프롬프트 v1 → v4** — 실패를 보고 한 줄씩 고치기 | AI 문구 4개 |
| 8 | 버전별 비교표·그래프 | 표 1개, 그림 1장 |
| 9 | ✍️ **사람이 검증·편집** | 최종 문구 |
| 10 | 카드뉴스 PNG 4장 만들기 | PNG 4장 |
| 11 | **블라인드 비교** — 짝이 사람/AI 맞히기 | 평가 기록 |
| 12 | ✍️ 기록, 제출 ZIP | ZIP |

**사용 방법:** `파일 → Drive에 사본 저장` 후 **위에서부터 한 셀씩 ▶ 실행**합니다. 런타임을 다시 시작했다면 0단계부터 다시 실행합니다. GPU는 필요 없습니다.
""" + ("\n> 🧑‍🏫 이 노트북은 모든 셀을 실행해 둔 **강의자 시연 완성본**입니다. ✍️ 셀에 예시 답이 들어 있습니다. 학생 워크북과 다른 파일이므로 여기서 실행해도 학생 노트북에는 영향이 없습니다.\n>\n> ⚠️ 저장된 AI 응답은 **오프라인 예비 응답**(실제 AI 출력이 아니라 수업 흐름을 보여 주려고 미리 작성한 예시)입니다. 수업 중 Colab에서 다시 실행하면 실제 Gemini 응답으로 바뀝니다.\n" if completed else "\n> ✍️ 표시 셀에 본인의 결과를 작성합니다. 코드 셀은 고치지 않아도 끝까지 실행됩니다. 🔧 표시 셀은 선택 활동입니다.\n"))

    # ---------- 0 ----------
    add_md("""## 0단계. 실습 준비 (3분)
그래프·카드에 한글이 보이도록 한글 폰트를 설치하고, **AI 연결**을 확인합니다.

| 도구 | 하는 일 |
|---|---|
| `pandas` | 표(DataFrame) 데이터 읽기·계산 |
| `matplotlib` + `koreanize_matplotlib` | 그래프·카드 이미지 그리기 + 한글 폰트 |
| `google.colab.ai` | Colab에 들어 있는 생성형 AI(Gemini). **API 키 없이** `ai.generate_text(프롬프트)` 한 줄로 글을 생성 |
| `re` | 글 속에서 숫자를 찾아내는 정규표현식 |

`ask_ai(버전, 프롬프트)` 함수는 다음 순서로 응답을 가져옵니다.
1. 🔧 붙여넣기 칸(`PASTE`)에 직접 붙여 넣은 응답이 있으면 그것을 씁니다(Gemini 웹 등에서 받은 결과).
2. 없으면 Colab AI에 요청합니다.
3. Colab AI를 쓸 수 없으면(사용량 한도 등) **오프라인 예비 응답**을 쓰고 ⚠️로 알려 줍니다. 실습은 끊기지 않습니다.

✅ **확인:** `준비 완료`와 함께 `✔ Colab AI 연결됨` 또는 `⚠️ 오프라인 예비 응답 모드`가 출력됩니다.""")
    add_code("""import subprocess, sys
try:
    import koreanize_matplotlib            # 그래프 한글 폰트
except ImportError:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'koreanize-matplotlib'], check=False)
    try:
        import koreanize_matplotlib
    except ImportError:
        print('⚠️ 한글 폰트 설치 실패: 그림의 한글이 네모로 보일 수 있지만 실습은 계속할 수 있습니다.')

import re, json, textwrap, random, shutil, datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
try:
    from IPython.display import display, Image
except ImportError:
    display = print

plt.rcParams['axes.unicode_minus'] = False
OUT = Path('week13_outputs')
OUT.mkdir(exist_ok=True)

# ── AI 연결 ─────────────────────────────────────────────
try:
    from google.colab import ai
    AI_OK = True
except Exception:
    ai, AI_OK = None, False
print('준비 완료 · pandas', pd.__version__)
print('✔ Colab AI 연결됨' if AI_OK else '⚠️ 오프라인 예비 응답 모드 (Colab이 아니거나 AI를 쓸 수 없음)')""")

    add_md("""### 0-1. 응답 가져오기 함수와 예비 응답 (실행만 하세요)
이 셀은 `ask_ai()` 함수와 오프라인 예비 응답을 준비합니다. 내용을 읽지 않아도 됩니다.

✅ **확인:** `ask_ai 준비 완료` 출력""")
    add_code("OFFLINE = " + json.dumps({k: OFFLINE[k] for k in ["v1", "v2", "v3", "v4"]}, ensure_ascii=False, indent=1) + """

PASTE = {'v1': '', 'v2': '', 'v3': '', 'v4': ''}   # 🔧 다른 AI 결과를 붙여 넣을 때만 사용(4-1 참고)
prompts, responses, sources = {}, {}, {}

def ask_ai(version, prompt):
    \"\"\"프롬프트를 AI에 보내고 응답 글을 돌려준다(붙여넣기 → Colab AI → 예비 응답 순).\"\"\"
    prompts[version] = prompt
    if PASTE.get(version, '').strip():
        text, src = PASTE[version].strip(), '붙여넣기'
    else:
        text, src = None, None
        if AI_OK:
            try:
                text, src = str(ai.generate_text(prompt)).strip(), 'Colab AI(Gemini)'
            except Exception as e:
                print('⚠️ Colab AI 요청 실패:', type(e).__name__, '→ 예비 응답 사용')
        if not text:
            text, src = OFFLINE[version], '오프라인 예비 응답'
    responses[version], sources[version] = text, src
    print(f'── {version} 응답 [{src}] ──')
    print(text)
    return text

print('ask_ai 준비 완료')""")

    add_md("""### 0-2. 내 정보 ✍️
제출 파일 이름과 블라인드 비교 순서에 쓰입니다.""")
    add_code(f"STUDENT_ID = '{EX['student_id'] if completed else ''}'   # ✍️ 학번 또는 이름 (예: '2025123')\n"
             "STUDENT_ID = STUDENT_ID.strip() or 'student'\nprint('제출자:', STUDENT_ID)")

    # ---------- 1 ----------
    add_md("""## 1단계. 2025년 대구 날씨 데이터 불러오기 (3분)
11주차에 쓴 **기상청 ASOS 대구(143) 시간자료**에서 2025년 1년치를 **하루 단위로 묶은** 파일입니다(11주차 3단계와 같은 방법).

| 열 | 뜻 |
|---|---|
| `날짜` | 2025-01-01 ~ 2025-12-31 |
| `평균기온`·`최고기온`·`최저기온` | 그날 정시 관측 24개의 평균·최댓값·최솟값(°C) |
| `일강수량` | 그날 24시간 강수량의 합(mm) |

- 파일 위치: [Google Drive 01_실습데이터](@@DRIVE_FOLDER@@) · 원본: [기상청 기상자료개방포털](https://data.kma.go.kr/data/grnd/selectAsosRltmList.do?pgmNo=36)
- Drive가 안 되면 수업 GitHub 사본으로, 그것도 안 되면 업로드 창으로 자동 전환됩니다.

✅ **확인:** `✔ [Google Drive] daegu_2025_daily.csv (365, 5)`""")
    add_code("""DRIVE_ID = '@@DRIVE_ID@@'
NAME = '@@DATA@@'
BACKUP = '@@RAW@@/data/' + NAME          # Drive 실패 시 백업
Path('week13_data').mkdir(exist_ok=True)
path = Path('week13_data') / NAME

def read_ok(src):
    try:
        df = pd.read_csv(src, parse_dates=['날짜'])
        return df if df.shape == (365, 5) else None
    except Exception:
        return None

daily = read_ok(path) if path.exists() else None   # ⓪ 이미 받은 파일(다시 실행할 때)
if daily is not None:
    print('✔ [이미 받은 파일]', NAME, daily.shape)
else:
    try:                               # ① Google Drive
        import gdown
        gdown.download(id=DRIVE_ID, output=str(path), quiet=True)
        daily = read_ok(path)
        if daily is not None:
            print('✔ [Google Drive]', NAME, daily.shape)
    except Exception as e:
        print('  Drive 내려받기 실패:', type(e).__name__)
if daily is None:                      # ② 백업: 수업 GitHub
    daily = read_ok(BACKUP)
    if daily is not None:
        print('✔ [GitHub 백업]', NAME, daily.shape)
if daily is None:                      # ③ 직접 업로드
    from google.colab import files
    print('Drive 01_실습데이터에서 CSV를 내려받아 업로드하세요.')
    up = files.upload()
    daily = read_ok(list(up)[0])
    print('✔ [업로드]', daily.shape)

daily = daily.set_index('날짜')
display(daily.head(3))""")

    # ---------- 2 ----------
    add_md("""## 2단계. 데이터에서 '사실' 뽑기 (8분)
카드뉴스에 들어갈 숫자는 **AI가 아니라 데이터가** 정합니다. pandas로 1년치 365일에서 핵심 사실을 계산해 **사실표**를 만듭니다. 이 사실표가 오늘의 '정답지'입니다.

| 코드 | 하는 일 |
|---|---|
| `daily['최고기온'].idxmax()` | 최고기온이 가장 높은 **날짜** |
| `(daily['최고기온'] >= 33).sum()` | 조건을 만족하는 날 **개수** (폭염일: 최고기온 33°C 이상) |
| `daily.groupby(daily.index.month)` | **월별로** 묶어 평균·합계 계산 |

✅ **확인:** 사실표 13줄 — 연평균 **15.2°C**, 가장 더운 날 **7월 7일 37.4°C**, 가장 추운 날 **1월 10일 −10.6°C**, 폭염일 **48일**(7월 18일·8월 21일), 가장 더운 달 **8월 28.7°C**, 가장 추운 달 **2월 1.2°C**, 연강수량 **1,029.0mm**, 비가 가장 많은 달 **7월 248.0mm**, 하루 최다 **7월 17일 102.3mm**. 그림 `fig_monthly.png` 저장.""")
    add_code("""def md_(d):                                    # Timestamp → '7월 7일'
    return f'{d.month}월 {d.day}일'

month = daily.groupby(daily.index.month).agg(평균기온=('평균기온', 'mean'),
                                             강수량=('일강수량', 'sum'),
                                             폭염일=('최고기온', lambda s: int((s >= 33).sum())))
hot, cold, wet = daily['최고기온'].idxmax(), daily['최저기온'].idxmin(), daily['일강수량'].idxmax()
fact_rows = [
    ('연평균기온',          f"{daily['평균기온'].mean():.1f}°C"),
    ('가장 더운 날',        f"{md_(hot)} (최고 {daily.loc[hot, '최고기온']:.1f}°C)"),
    ('가장 추운 날',        f"{md_(cold)} (최저 {daily.loc[cold, '최저기온']:.1f}°C)"),
    ('폭염일(최고 33°C 이상)', f"{int((daily['최고기온'] >= 33).sum())}일"),
    ('7월 폭염일',          f"{month.loc[7, '폭염일']}일"),
    ('8월 폭염일',          f"{month.loc[8, '폭염일']}일"),
    ('가장 더운 달',        f"{month['평균기온'].idxmax()}월 (평균 {month['평균기온'].max():.1f}°C)"),
    ('가장 추운 달',        f"{month['평균기온'].idxmin()}월 (평균 {month['평균기온'].min():.1f}°C)"),
    ('연강수량',            f"{daily['일강수량'].sum():,.1f}mm"),
    ('비가 가장 많은 달',   f"{month['강수량'].idxmax()}월 ({month['강수량'].max():.1f}mm)"),
    ('하루 강수량 최다',    f"{md_(wet)} ({daily.loc[wet, '일강수량']:.1f}mm)"),
    ('관측 지점',           '기상청 ASOS 대구(143), 정시 관측'),
    ('기간',                '2025년 1월 1일 ~ 12월 31일'),
]
facts = pd.DataFrame(fact_rows, columns=['항목', '값'])
FACT_TEXT = '\\n'.join(f'- {a}: {b}' for a, b in facts.values)   # 프롬프트에 넣을 글
display(facts)

# 카드에도 쓸 월별 그림
fig, ax1 = plt.subplots(figsize=(7, 3.6))
ax1.bar(month.index, month['강수량'], color='#7fb3e0', label='월강수량(mm)')
ax1.set(xlabel='월', ylabel='강수량(mm)', xticks=range(1, 13))
ax2 = ax1.twinx()
ax2.plot(month.index, month['평균기온'], color='#e4572e', marker='o', label='월평균기온(°C)')
ax2.set_ylabel('평균기온(°C)')
ax1.set_title('2025년 대구 월평균기온과 월강수량')
fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.88))
fig.tight_layout()
fig.savefig(OUT / 'fig_monthly.png', dpi=150)
plt.show()
facts.to_csv(OUT / 'facts.csv', index=False, encoding='utf-8-sig')""")

    # ---------- 3 ----------
    add_md("""## 3단계. ✍️ 사람 버전 먼저 — AI 없이 카드 4장 쓰기 (8분)
AI를 쓰기 **전에** 위 사실표만 보고 카드뉴스 4장 문구를 직접 씁니다. 나중에 AI 결과와 블라인드로 비교합니다.

**작성 규칙** (AI에게도 같은 규칙을 줍니다)
- 독자: 대학생 · 인스타그램 카드뉴스 4장
- 카드마다 `제목`(15자 이내)과 `본문`(60자 이내)
- 숫자는 **사실표에 있는 것만**
- 아래 형식을 그대로 지키기

```
[카드1] 제목: ... / 본문: ...
[카드2] 제목: ... / 본문: ...
[카드3] 제목: ... / 본문: ...
[카드4] 제목: ... / 본문: ...
```
✅ **확인:** `사람 버전: 카드 4장 인식` (비워 두면 ⚠️ 안내만 나오고 다음 단계는 계속 실행됩니다)""")
    add_code("HUMAN_TEXT = " + pystr(EX["human"] if completed else "\n[카드1] 제목:  / 본문: \n[카드2] 제목:  / 본문: \n[카드3] 제목:  / 본문: \n[카드4] 제목:  / 본문: \n") + """   # ✍️ 직접 작성

CARD_RE = re.compile(r'\\[\\s*카드\\s*(\\d)\\s*\\]')

def parse_cards(text):
    \"\"\"'[카드N] 제목: … / 본문: …' 형식의 글을 카드 목록으로 바꾼다.\"\"\"
    text = (text or '').replace('**', '').replace('#', '')
    parts = CARD_RE.split(text)
    cards = []
    for i in range(1, len(parts) - 1, 2):
        chunk = parts[i + 1].strip()
        t = re.search(r'제목\\s*[:：]\\s*([^/\\n]*)', chunk)
        b = re.search(r'본문\\s*[:：]\\s*(.*)', chunk, re.S)
        if t:
            title, body = t.group(1).strip(), (b.group(1).strip() if b else '')
        else:
            lines = [x.strip() for x in chunk.splitlines() if x.strip()]
            title, body = (lines[0] if lines else ''), ' '.join(lines[1:])
        body = re.sub(r'\\s+', ' ', body)
        if title or body:
            cards.append({'제목': title, '본문': body})
    return cards[:4]

human_cards = parse_cards(HUMAN_TEXT)
if len(human_cards) == 4:
    print('사람 버전: 카드 4장 인식')
    display(pd.DataFrame(human_cards, index=[f'카드{i}' for i in range(1, 5)]))
else:
    print(f'⚠️ 사람 버전 카드 {len(human_cards)}장 인식 — 형식을 확인하세요. (비워 두어도 다음 단계는 실행됩니다)')""")

    # ---------- 4 ----------
    add_md("""## 4단계. 프롬프트 v1 — 그냥 부탁하기 (Zero-shot) (5분)
대부분의 사람이 처음 하는 방식 그대로, **한 줄**로 부탁합니다. 데이터는 주지 않습니다.

그다음 `check_numbers()`로 응답 속 숫자를 모두 찾아 **사실표에 있는 숫자인지** 확인합니다.

| 코드 | 하는 일 |
|---|---|
| `re.findall(숫자 패턴, 글)` | 글에서 `37.4`, `1,029` 같은 숫자를 모두 찾기 |
| `ALLOWED` | 사실표에 나오는 숫자 모음(+ 연도 2025, 기준 33°C, 지점번호 143) |
| ✔ / ✘ | 응답 숫자가 `ALLOWED` 안에 있으면 ✔, 없으면 ✘ |

> 💡 생성형 AI는 **다음에 올 그럴듯한 단어**를 이어 붙여 글을 만듭니다. 2025년 대구 관측값을 모르면, 모른다고 하기보다 *그럴듯한 숫자*를 만들어 낼 수 있습니다(환각).

✅ **확인:** 응답이 출력되고, 아래에 숫자 점검표가 나옵니다. 예비 응답 기준으로 **사실표에 없는 숫자 8개**. 실제 AI 응답은 실행할 때마다 다릅니다 — 몇 개가 나왔는지 기록하세요.""")
    add_code("""NUM_RE = re.compile(r'\\d{1,3}(?:,\\d{3})+(?:\\.\\d+)?|\\d+(?:\\.\\d+)?')

def numbers_in(text):
    t = CARD_RE.sub(' ', text or '')
    t = re.sub(r'\\d+\\s*장', ' ', t)            # '카드 4장' 같은 장수 표현은 제외
    return [float(x.replace(',', '')) for x in NUM_RE.findall(t)]

ALLOWED = set(numbers_in(FACT_TEXT)) | {2025.0, 33.0, 143.0}

def check_numbers(text, show=True):
    nums = numbers_in(text)
    fmt = lambda n: f'{n:,.0f}' if n == int(n) else f'{n:,.1f}'
    ok = [fmt(n) for n in nums if n in ALLOWED]
    ng = [fmt(n) for n in nums if n not in ALLOWED]
    if show:
        print('✔ 사실표에 있는 숫자 :', ', '.join(ok) or '없음')
        print('✘ 사실표에 없는 숫자 :', ', '.join(ng) or '없음')
        print(f'→ 숫자 {len(nums)}개 중 사실표에 없는 숫자 {len(ng)}개')
    return len(ng)

v1 = ask_ai('v1', '2025년 대구 날씨를 정리하는 인스타그램 카드뉴스 4장 문구를 써 줘.')
print()
check_numbers(v1);""")

    add_md("""### 4-1. 🔧 (선택) 다른 AI 결과를 붙여 넣기
Colab AI가 안 되거나, Gemini·ChatGPT 웹에서 받은 결과로 해 보고 싶다면 `PASTE['v1']`처럼 붙여 넣고 **4단계 셀을 다시 실행**합니다. 비워 두면 그대로 진행됩니다.""")
    add_code("# PASTE['v1'] = '''여기에 붙여 넣기'''\nprint('붙여넣기 칸:', {k: ('있음' if v.strip() else '비어 있음') for k, v in PASTE.items()})")

    # ---------- 5 ----------
    add_md("""## 5단계. 프롬프트 v2 — 근거 데이터 주기 (5분)
v1의 문제는 **AI가 숫자를 몰랐다**는 것입니다. 그래서 2단계 사실표(`FACT_TEXT`)를 프롬프트에 넣고 "이 숫자만 쓰라"고 합니다.

| 추가한 요소 | 프롬프트 속 문장 |
|---|---|
| **근거** | `아래 사실표만 사용해` + 사실표 13줄 |
| **제약** | `사실표에 없는 숫자는 쓰지 마` |

✅ **확인:** 사실표에 없는 숫자가 v1보다 크게 줄어듭니다(예비 응답 기준 **0개**). 대신 카드 4장으로 나뉘지 않은 긴 글이 나오기 쉽습니다 → 6단계에서 고칩니다.""")
    add_code("""prompt_v2 = f'''2025년 대구 날씨를 정리하는 인스타그램 카드뉴스 4장 문구를 써 줘.
아래 사실표만 사용해. 사실표에 없는 숫자는 쓰지 마.

[사실표]
{FACT_TEXT}'''
v2 = ask_ai('v2', prompt_v2)
print()
check_numbers(v2)
print('카드 인식:', len(parse_cards(v2)), '장')""")

    # ---------- 6 ----------
    add_md("""## 6단계. 프롬프트 v3 — 역할·독자·형식 정하기 (6분)
v2는 숫자는 맞지만 **카드뉴스로 쓸 수 없는 형태**입니다. 일을 맡길 때처럼 **누가, 누구에게, 어떤 모양으로** 쓰는지 정합니다.

<img src="@@RAW@@/figures/c2_prompt_ladder.png" width="640">

| 요소 | 프롬프트 속 문장 |
|---|---|
| **역할** | `너는 대학 SNS 계정의 콘텐츠 담당자야.` |
| **독자·목표** | `대학생이 끝까지 넘겨 보게` |
| **형식** | `[카드N] 제목: … / 본문: …` 4줄, 제목 15자·본문 60자 이내 |
| **구성** | 카드1 표지, 카드2 더위, 카드3 비, 카드4 추위+출처 |

✅ **확인:** `카드 인식: 4 장`. 예비 응답 기준으로 형식은 지키지만 **본문 60자를 넘는 카드**가 있고 문체가 딱딱합니다 → 7단계에서 예시로 고칩니다.""")
    add_code("""prompt_v3 = f'''너는 대학 SNS 계정의 콘텐츠 담당자야.
대학생이 끝까지 넘겨 보게 2025년 대구 날씨 결산 인스타그램 카드뉴스 4장 문구를 써 줘.

[규칙]
- 아래 사실표만 사용하고, 사실표에 없는 숫자는 쓰지 마.
- 카드1 표지, 카드2 더위, 카드3 비, 카드4 추위와 출처(기상청 ASOS 대구).
- 제목은 15자 이내, 본문은 60자 이내.
- 아래 형식 4줄로만 출력해. 다른 말은 쓰지 마.
[카드1] 제목: ... / 본문: ...

[사실표]
{FACT_TEXT}'''
v3 = ask_ai('v3', prompt_v3)
print()
check_numbers(v3)
cards_v3 = parse_cards(v3)
print('카드 인식:', len(cards_v3), '장')
if cards_v3:
    t = pd.DataFrame(cards_v3)
    t['제목 글자수'], t['본문 글자수'] = t['제목'].str.len(), t['본문'].str.len()
    display(t)""")

    # ---------- 7 ----------
    add_md("""## 7단계. 프롬프트 v4 — 잘 쓴 예시 보여 주기 (Few-shot) (6분)
말로 "재미있게 써 줘"라고 하는 것보다 **잘 쓴 예시 2개**를 보여 주는 것이 문체를 더 정확하게 전달합니다.

예시는 **다른 주제**(도서관 이용 결산)로 넣었습니다. 예시의 숫자(`12만`, `3월` 등)가 대구 날씨 글에 섞여 들어오는지도 숫자 점검표로 확인하세요.

✅ **확인:** `카드 인식: 4 장`, 사실표에 없는 숫자 **1개**(예비 응답 기준 `39` — 7월 18일 + 8월 21일을 AI가 더한 값). ✘라고 해서 모두 틀린 것은 아닙니다. 사람이 판단합니다 → 9단계.""")
    add_code("""FEWSHOT = '''[예시 — 다른 주제, 숫자는 쓰지 말 것]
[카드1] 제목: 도서관, 올해 얼마나 갔니? / 본문: 숫자로 보는 2024 우리 학교 도서관
[카드2] 제목: 12만 명이 다녀갔다 / 본문: 가장 붐빈 달은 시험 기간 4월. 열람실은 매일 만석!'''

prompt_v4 = prompt_v3 + '\\n\\n' + FEWSHOT + '\\n\\n위 예시처럼 짧고 리듬감 있게, 숫자를 제목에 앞세워 써 줘.'
v4 = ask_ai('v4', prompt_v4)
print()
check_numbers(v4)
cards_v4 = parse_cards(v4)
print('카드 인식:', len(cards_v4), '장')
if cards_v4:
    display(pd.DataFrame(cards_v4, index=[f'카드{i}' for i in range(1, len(cards_v4) + 1)]))""")

    add_md("""### 7-1. 🔧 (선택) 같은 프롬프트를 세 번 실행하면?
생성형 AI는 같은 질문에도 매번 다른 답을 냅니다. v4를 3번 실행해 사실표에 없는 숫자 개수가 어떻게 달라지는지 봅니다(Colab AI 연결 시에만 의미가 있습니다).""")
    add_code("""if AI_OK:
    for k in range(3):
        try:
            t = str(ai.generate_text(prompt_v4))
            print(f'[{k + 1}회] 카드 {len(parse_cards(t))}장 · 사실표에 없는 숫자 {check_numbers(t, show=False)}개')
        except Exception as e:
            print(f'[{k + 1}회] 요청 실패:', type(e).__name__)
else:
    print('Colab AI가 연결되지 않아 건너뜁니다.')""")

    # ---------- 8 ----------
    add_md("""## 8단계. 버전별 비교 — 프롬프트 한 줄이 바꾼 것 (6분)
v1~v4와 사람 버전을 같은 기준으로 비교합니다.

| 기준 | 뜻 |
|---|---|
| 사실표에 없는 숫자 | 0이 목표. 단, ✘가 곧 '틀림'은 아님(계산값일 수 있음) |
| 카드 4장 형식 | 카드로 바로 옮길 수 있는가 |
| 본문 60자 초과 | 카드 한 장에 들어가는가 |

✅ **확인:** 표와 막대그래프 `fig_compare.png`. 예비 응답 기준 — v1 **8** → v2 **0** → v3 **0** → v4 **1**, 형식은 v3부터 ✔.""")
    add_code("""rows = []
for name, text in [('사람', HUMAN_TEXT)] + [(v, responses.get(v, '')) for v in ['v1', 'v2', 'v3', 'v4']]:
    cards = parse_cards(text)
    if name == '사람' and len(cards) != 4:
        continue                                 # 사람 버전을 안 썼으면 표에서 제외
    rows.append({'버전': name,
                 '사실표에 없는 숫자': check_numbers(text, show=False),
                 '카드 4장 형식': '✔' if len(cards) == 4 else '✘',
                 '본문 60자 초과': sum(len(c['본문']) > 60 for c in cards) if len(cards) == 4 else '-',
                 '응답 출처': sources.get(name, '직접 작성')})
compare = pd.DataFrame(rows).set_index('버전')
display(compare)
compare.to_csv(OUT / 'compare.csv', encoding='utf-8-sig')

fig, ax = plt.subplots(figsize=(6, 3.4))
colors = ['#6c757d' if i == '사람' else '#2a9d8f' for i in compare.index]
bars = ax.bar(compare.index, compare['사실표에 없는 숫자'], color=colors)
ax.bar_label(bars)
ax.set(title='버전별 사실표에 없는 숫자 개수', ylabel='개수')
ax.set_ylim(0, max(compare['사실표에 없는 숫자'].max() + 1, 3))
fig.tight_layout()
fig.savefig(OUT / 'fig_compare.png', dpi=150)
plt.show()""")

    # ---------- 9 ----------
    add_md("""## 9단계. ✍️ 사람이 검증·편집하기 (8분)
AI 글을 그대로 쓰지 않습니다. v4를 출발점으로 **사실표와 한 줄씩 대조**하며 고칩니다.

**점검 순서**
1. 숫자 점검표의 ✘ 숫자 → 계산이 맞으면 두기, 근거가 없으면 지우기
2. **숫자가 없는 문장**도 확인 — 예: "가장 추운 달은 1월" (자동 검사로 못 잡음!)
3. 제목 15자, 본문 60자 이내
4. 카드4에 출처가 있는지

아래 `FINAL_TEXT`를 고칩니다. 비워 두면 v4를 그대로 씁니다.

✅ **확인:** `→ 숫자 N개 중 사실표에 없는 숫자 M개`와 `최종본: 카드 4장`. 남은 ✘ 숫자는 모두 본인이 확인한 계산값이어야 합니다(완성본 예시: 39 하나).""")
    add_code("print('── v4 원문(복사해서 고치세요) ──')\nprint(responses.get('v4', ''))\n\n"
             "FINAL_TEXT = " + pystr(EX["final"] if completed else "") + """   # ✍️ 고친 최종본

final_text = FINAL_TEXT.strip() or responses.get('v4', '')
final_cards = parse_cards(final_text)
print()
check_numbers(final_text)
print(f'최종본: 카드 {len(final_cards)}장')
display(pd.DataFrame(final_cards, index=[f'카드{i}' for i in range(1, len(final_cards) + 1)]))""")

    # ---------- 10 ----------
    add_md("""## 10단계. 카드뉴스 PNG 4장 만들기 (5분)
최종 문구로 **1080×1080 인스타그램 카드**를 만듭니다. 본문에 `비`·`강수`가 있으면 월강수량 막대, `더위`·`폭염`·`°C`가 있으면 월평균기온 선을 카드 아래에 자동으로 넣습니다. 모든 카드 아래에 출처가 들어갑니다.

| 코드 | 하는 일 |
|---|---|
| `plt.figure(figsize=(6, 6))` + `dpi=180` | 6인치 × 180 = 1080픽셀 정사각형 |
| `textwrap.fill(글, 너비)` | 긴 글을 여러 줄로 나누기 |
| `fig.add_axes([...])` | 카드 안 원하는 위치에 작은 그래프 넣기 |

✅ **확인:** `card_1.png` ~ `card_4.png` 4장 저장, 아래에 미리보기.""")
    add_code("""PALETTE = ['#264653', '#e76f51', '#2a9d8f', '#457b9d']
SOURCE = '자료: 기상청 ASOS 대구(143) 정시 관측 · 2025 | 문구: 사람 + 생성형 AI'

def draw_card(i, card):
    fig = plt.figure(figsize=(6, 6), dpi=180)
    fig.patch.set_facecolor(PALETTE[i % 4])
    fig.text(0.07, 0.92, f'{i + 1} / 4', color='white', fontsize=11, alpha=0.8)
    size = 30 if i == 0 else 24
    fig.text(0.07, 0.80, textwrap.fill(card['제목'], 12 if i == 0 else 14), color='white',
             fontsize=size, fontweight='bold', va='top', linespacing=1.3)
    fig.text(0.07, 0.56 if i == 0 else 0.60, textwrap.fill(card['본문'], 22), color='white',
             fontsize=14, va='top', linespacing=1.6)
    body = card['제목'] + card['본문']
    if i > 0 and ('비' in body or '강수' in body):
        ax = fig.add_axes([0.1, 0.12, 0.8, 0.22])
        ax.bar(month.index, month['강수량'], color='white', alpha=0.85)
        ax.set_title('월강수량(mm)', color='white', fontsize=10)
    elif i > 0 and any(k in body for k in ['더위', '폭염', '더운', '°C']):
        ax = fig.add_axes([0.1, 0.12, 0.8, 0.22])
        ax.plot(month.index, month['평균기온'], color='white', marker='o')
        ax.set_title('월평균기온(°C)', color='white', fontsize=10)
    else:
        ax = None
    if ax is not None:
        ax.set_facecolor('none')
        ax.tick_params(colors='white', labelsize=8)
        ax.set_xticks(range(1, 13))
        for s in ax.spines.values():
            s.set_color('white')
    fig.text(0.07, 0.04, SOURCE, color='white', fontsize=7, alpha=0.85)
    p = OUT / f'card_{i + 1}.png'
    fig.savefig(p, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)
    return p

if len(final_cards) == 4:
    card_files = [draw_card(i, c) for i, c in enumerate(final_cards)]
    fig, axes = plt.subplots(1, 4, figsize=(14, 3.8))
    for ax, p in zip(axes, card_files):
        ax.imshow(plt.imread(p)); ax.axis('off')
    plt.tight_layout(); plt.show()
    print('저장:', ', '.join(p.name for p in card_files))
else:
    print('⚠️ 카드가 4장이 아닙니다. 9단계 FINAL_TEXT 형식을 확인하세요.')""")

    # ---------- 11 ----------
    add_md("""## 11단계. 블라인드 비교 — 짝은 구별할 수 있을까? (10분)
3단계 **사람 버전**과 7단계 **AI v4 원문**(편집 전)을 A·B로 섞어 보여 줍니다. 어느 쪽이 사람인지 화면에 나오지 않습니다.

**진행 방법**
1. 아래 셀을 실행하고 화면을 짝에게 보여 줍니다.
2. 짝이 ① 어느 쪽이 AI인지 고르고 ② 세 기준(1~5점)으로 평가합니다 → 11-1 칸에 기록
3. 11-2 셀을 실행해 정답을 공개합니다.

✅ **확인:** `A`와 `B` 두 글이 출력됩니다(사람 버전을 안 썼다면 ⚠️ 안내).""")
    add_code("""rng = random.Random(sum(map(ord, STUDENT_ID)))       # 학번마다 순서가 다름
order = rng.sample(['사람', 'AI'], 2)                   # order[0] = A, order[1] = B
texts = {'사람': human_cards, 'AI': parse_cards(responses.get('v4', ''))}
if len(human_cards) == 4:
    for label, who in zip('AB', order):
        print(f'━━━━━━━━ {label} ━━━━━━━━')
        for k, cd in enumerate(texts[who], 1):
            print(f'  {k}. {cd["제목"]} — {cd["본문"]}')
        print()
else:
    print('⚠️ 3단계 사람 버전을 먼저 작성하세요.')""")

    add_md("""### 11-1. ✍️ 짝의 판단 기록
`GUESS`에 짝이 AI라고 고른 쪽(`'A'` 또는 `'B'`), `SCORES`에 1~5점을 적습니다.

| 기준 | 질문 |
|---|---|
| 정확성 | 숫자와 내용이 믿을 만한가? (사실표 참고) |
| 읽고 싶음 | 넘겨 보고 싶은가? |
| 행동 유도 | 저장·공유하고 싶은가? |""")
    s = EX["scores"] if completed else {"A": {"정확성": 0, "읽고 싶음": 0, "행동 유도": 0},
                                        "B": {"정확성": 0, "읽고 싶음": 0, "행동 유도": 0}}
    add_code(f"GUESS = '{EX['guess'] if completed else ''}'      # ✍️ 짝이 AI라고 고른 쪽: 'A' 또는 'B'\n"
             f"SCORES = {json.dumps(s, ensure_ascii=False)}   # ✍️ 1~5점")

    add_md("""### 11-2. 정답 공개
✅ **확인:** 실제 순서, 짝이 맞혔는지, 사람/AI별 점수 표""")
    add_code("""blind = {'order': {'A': order[0], 'B': order[1]}, 'guess': GUESS, 'scores': SCORES}
if len(human_cards) == 4 and GUESS in ('A', 'B'):
    ai_label = 'A' if order[0] == 'AI' else 'B'
    print(f'정답: A = {order[0]}, B = {order[1]}')
    print('짝의 판단:', '맞힘 ✔' if GUESS == ai_label else '못 맞힘 ✘ (AI 글을 사람 글로 봄)')
    score_table = pd.DataFrame({order[0]: SCORES['A'], order[1]: SCORES['B']}).T
    display(score_table)
    blind['correct'] = GUESS == ai_label
else:
    print('⚠️ 사람 버전과 GUESS를 입력한 뒤 다시 실행하세요.')
_ = (OUT / 'blind_eval.json').write_text(json.dumps(blind, ensure_ascii=False, indent=2), encoding='utf-8')""")

    # ---------- 12 ----------
    add_md("""## 12단계. ✍️ 기록과 제출 (5분)
Q1~Q5에 답하고 마지막 셀을 실행하면 제출 ZIP이 만들어집니다. **Q5 AI 사용 기록**은 콘텐츠를 공개할 때 밝혀야 하는 정보입니다.""")
    add_code("ANSWERS = " + json.dumps(EX["answers"] if completed else EMPTY_ANS, ensure_ascii=False, indent=4) + "   # ✍️")

    add_md("""✅ **확인:** `제출 파일: week13_<학번>.zip` 과 포함 파일 목록. Colab 왼쪽 📁에서 내려받아 제출합니다.""")
    add_code("""log = {'student': STUDENT_ID, 'time': datetime.datetime.now().isoformat(timespec='minutes'),
       'facts': fact_rows, 'human_text': HUMAN_TEXT, 'prompts': prompts,
       'responses': responses, 'sources': sources, 'final_text': final_text, 'answers': ANSWERS}
_ = (OUT / 'week13_log.json').write_text(json.dumps(log, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
empty = [k for k, v in ANSWERS.items() if not str(v).strip()]
if empty:
    print('⚠️ 아직 비어 있는 답:', ', '.join(empty))
zip_name = shutil.make_archive(f'week13_{STUDENT_ID}', 'zip', OUT)
print('제출 파일:', Path(zip_name).name)
print('포함:', ', '.join(sorted(p.name for p in OUT.iterdir())))""")

    nb = nbf.v4.new_notebook()
    nb.cells = c
    nb.metadata = {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}, "colab": {"provenance": []}}
    return nb


if __name__ == "__main__":
    out = ROOT / "notebooks"
    out.mkdir(exist_ok=True)
    nbf.write(build(False), out / "Week13_Student_Workbook.ipynb")
    nbf.write(build(True), out / "Week13_Instructor_Demo.ipynb")
    print("생성:", *sorted(p.name for p in out.glob("*.ipynb")))
