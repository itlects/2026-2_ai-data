"""노트북 → 노션 워크북 하위 페이지 마크다운 (코드는 노트북과 완전히 같게 추출).

python tools/make_notion_workbooks.py → materials/notion_wb1.md, materials/notion_wb2.md
"""
from pathlib import Path
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]
RAW = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/week13"
stu = nbformat.read(ROOT / "notebooks" / "Week13_Student_Workbook.ipynb", as_version=4)
ins = nbformat.read(ROOT / "notebooks" / "Week13_Instructor_Demo.ipynb", as_version=4)
assert len(stu.cells) == len(ins.cells)

STUDENT_COLAB = "https://colab.research.google.com/drive/1yfC_Y1NFxIZgmNFaaBpeaYSPRuOpzIUy"
INSTR_COLAB = "https://colab.research.google.com/drive/10l9irpctHZoZUQ6pyWyWYyI0VFUprkOq"

# 단계 머리(## N단계) 앞에 넣을 진행 callout, 단계 끝에 넣을 CP
CUE = {
    0: ("🧑‍🏫", "gray_bg", "<b>같이 치기 · 20분</b> 강사 화면 = 강의자 Colab. 한 셀씩 함께 실행합니다. 0-1 셀은 길어서 설명 없이 실행만 합니다."),
    2: ("🧑‍🏫", "gray_bg", "<b>같이 치기 · 25분</b> 표 아래 계산 세 줄(idxmax, sum, groupby)만 짚고 실행합니다."),
    3: ("🧑‍🏫", "gray_bg", "<b>개별 · 33분 (8분)</b> 화면을 노션 사실표로 돌리고 타이머를 켭니다. 이 시간에는 AI를 쓰지 않습니다."),
    4: ("🧑‍🏫", "gray_bg", "<b>같이 치기 · 43분</b> v1 응답이 나오면 바로 묻습니다. \"이 숫자들, 믿어도 될까요?\" 그다음 점검표를 봅니다."),
    5: ("🧑‍🏫", "gray_bg", "<b>같이 치기 · 55분</b> v2~v4는 같은 리듬으로 갑니다. ① 무엇을 한 줄 더했나 → ② 실행 → ③ 무엇이 좋아졌고 무엇이 남았나."),
    8: ("🧑‍🏫", "gray_bg", "<b>해설 · 72분</b> 학생 화면의 숫자가 예시와 달라도 괜찮습니다. 몇 명에게 v1 숫자를 물어 칠판에 적습니다."),
    9: ("🧑‍🏫", "gray_bg", "<b>개별 · 78분 (14분)</b> 9단계 편집 → 10단계 카드. 순회하면서 '숫자 없는 오류'를 찾았는지 확인합니다."),
    11: ("🧑‍🏫", "gray_bg", "<b>짝 활동 · 92분</b> 노션 §7로 돌아가 진행합니다. 짝과 노트북 화면을 바꿔 봅니다."),
    12: ("🧑‍🏫", "gray_bg", "<b>개별 · 110분</b> 남은 시간에 Q1~Q5를 쓰고 ZIP을 만듭니다. 못 끝낸 학생은 과제로 이어 갑니다."),
}
CP = {
    1: "<b>CP1 · 25분</b> `✔ [Google Drive] daegu_2025_daily.csv (365, 5)`(또는 GitHub 백업) + `✔ Colab AI 연결됨` 또는 `⚠️ 오프라인 예비 응답 모드`. 막히면 `런타임 → 모두 실행`.",
    2: "<b>CP2 · 33분</b> 사실표 13줄. 연평균 15.2°C, 7월 7일 37.4°C, 폭염일 48일, 연강수량 1,029.0mm. 막히면 `런타임 → 이전 셀 모두 실행`.",
    4: "<b>CP3 · 50분</b> v1 응답 아래 `→ 숫자 N개 중 사실표에 없는 숫자 M개`가 보이면 통과. M은 사람마다 다릅니다(예비 응답 기준 8).",
    8: "<b>CP4 · 78분</b> 비교표 5줄(사람, v1~v4) + 막대그래프. 사람 줄이 없으면 3단계가 비어 있는 것입니다. 그대로 진행해도 됩니다.",
    10: "<b>CP5 · 92분</b> `저장: card_1.png, card_2.png, card_3.png, card_4.png` + 미리보기 4장. 카드가 4장이 아니면 9단계 형식을 확인합니다.",
}
RESULT_IMG = {2: f"{RAW}/results/fig_monthly.png", 8: f"{RAW}/results/fig_compare.png",
              10: f"{RAW}/results/cards_all.png"}
FOLD = {"OFFLINE = "}           # 너무 긴 코드 셀은 접기
WRITE_CELLS = ("HUMAN_TEXT = ", "FINAL_TEXT", "GUESS = ", "ANSWERS = ", "STUDENT_ID = ")


def step_of(src):
    m = re.match(r"##\s*(\d+)단계", src)
    return int(m.group(1)) if m else None


def md_conv(src):
    src = re.sub(r'<img src="([^"]+)"[^>]*>', r"![](\1)", src)
    src = re.sub(r"^# ", "## ", src, flags=re.M) if src.startswith("# ") else src
    src = src.replace("**", "**")
    return src.strip()


def outputs_text(cell):
    out, imgs = [], 0
    for o in cell.get("outputs", []):
        if o.output_type == "stream":
            out.append(o.text)
        elif "data" in o:
            if "image/png" in o["data"]:
                imgs += 1
            elif "text/plain" in o["data"]:
                out.append(o["data"]["text/plain"] + "\n")
    return "".join(out).rstrip(), imgs


def fence(code, lang="python"):
    n = max([len(m) for m in re.findall(r"`+", code)] + [2]) + 1
    f = "`" * max(3, n)
    return f"{f}{lang}\n{code}\n{f}"


def render(cells_range, title_note):
    parts = [title_note]
    cur_step = None
    for i in cells_range:
        s, t = stu.cells[i], ins.cells[i]
        if s.cell_type == "markdown":
            st = step_of(s.source)
            if st is not None:
                if cur_step is not None and cur_step in CP:
                    parts.append(f'<callout icon="🚩" color="red_bg">\n{CP[cur_step]}\n</callout>')
                cur_step = st
                if st in CUE:
                    ic, col, txt = CUE[st]
                    parts.append(f'<callout icon="{ic}" color="{col}">\n{txt}\n</callout>')
            parts.append(md_conv(s.source))
            continue
        code = s.source
        if any(code.startswith(k) for k in FOLD):
            parts.append(f'<toggle>\n코드 보기 (예비 응답 4개 + ask_ai 함수, 길어서 접어 둠)\n\n{fence(code)}\n</toggle>')
        else:
            parts.append(fence(code))
        if any(code.lstrip().startswith(k) or k in code.split("\n")[0] for k in WRITE_CELLS) or "FINAL_TEXT = " in code:
            if t.source != s.source:
                lines = t.source.split("\n")
                cut = next((k for k, L in enumerate(lines) if "✍️" in L), len(lines) - 1)
                parts.append(f'<toggle>\n✍️ 강의자 예시 답 (완성본 노트북의 값)\n\n{fence(chr(10).join(lines[:cut + 1]))}\n</toggle>')
        txt, imgs = outputs_text(t)
        if txt:
            if len(txt) > 2500:
                txt = txt[:2500] + "\n…(생략)"
            note = ""
            if "Drive 내려받기 실패" in txt:
                note = "\n\n자료 제작 환경에서는 Drive 접속이 막혀 GitHub 백업으로 읽었습니다. Colab에서는 보통 `✔ [Google Drive] daegu_2025_daily.csv (365, 5)`가 나옵니다."
            parts.append("<b>실행 결과 예시</b> (강의자 완성본, 오프라인 예비 응답 기준)" + note + "\n\n" + fence(txt, "plain text"))
        if cur_step in RESULT_IMG and imgs:
            parts.append(f"![실행 결과 그림 — {cur_step}단계]({RESULT_IMG[cur_step]})")
    if cur_step in CP:
        parts.append(f'<callout icon="🚩" color="red_bg">\n{CP[cur_step]}\n</callout>')
    return "\n\n".join(parts) + "\n"


# 경계: 9단계 머리 셀 인덱스
split = next(i for i, c in enumerate(stu.cells) if c.cell_type == "markdown" and step_of(c.source) == 9)
first = next(i for i, c in enumerate(stu.cells) if c.cell_type == "markdown" and step_of(c.source) == 0)

head = lambda rng, nm: f"""<callout icon="📒" color="blue_bg">
<b>{nm}</b>

- 학생: [학생 워크북 Colab]({STUDENT_COLAB}) → `파일 → Drive에 사본 저장` 후 실행
- 강의자: [강의자 시연 완성본 Colab]({INSTR_COLAB}) (실행 결과·예시 답 저장본)
- 두 노트북은 서로 다른 파일입니다. 강의자가 실행해도 학생 노트북에는 영향이 없습니다.
- 이 페이지의 코드는 노트북 코드와 같습니다. '실행 결과 예시'는 오프라인 예비 응답 기준이며, 실제 AI 응답은 실행할 때마다 달라집니다.
</callout>"""

wb1 = render(range(first, split), head(None, "워크북 1 — 사실표 만들기와 프롬프트 v1→v4 (0~8단계 · 20~78분)"))
wb2 = render(range(split, len(stu.cells)), head(None, "워크북 2 — 검증·편집, 카드뉴스 제작, 블라인드 비교 (9~12단계 · 78~120분)"))
(ROOT / "materials" / "notion_wb1.md").write_text(wb1, encoding="utf-8")
(ROOT / "materials" / "notion_wb2.md").write_text(wb2, encoding="utf-8")
print(len(wb1), len(wb2))
