"""7주차 노트북·노션 본문 생성 + 완성본 실행 (강의자용).

  python Week07/tools/build_notebooks.py [--execute KERNEL] [--notion OUT_DIR]

- make_main.py(워크북 0~3 원고) 하나에서 실습본·완성본 노트북과 노션 워크북 페이지 본문을 함께 만든다.
  셀 번호(▶ 셀 1-4)·코드가 노트북과 노션에서 같다.
- --execute: 완성본을 처음부터 끝까지 실행(데이터는 GitHub에서 읽음)해 출력까지 저장하고,
  그림은 Week07/figures/, 결과 CSV·프롬프트는 Week07/examples/ 로 복사한다.
- --notion: 실행 결과(실제 출력)를 넣은 노션 마크다운을 OUT_DIR/notion_wb0~3.md 로 저장한다.
- 보조 노트북(유튜브 수집, Drive 준비)은 make_extra.py 에서 한 벌만 만든다.
"""
import os
import re
import shutil
import sys
import tempfile

import nbformat as nbf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_main  # noqa: E402
import make_extra  # noqa: E402
from nb_common import build  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W7 = os.path.join(HERE, "..")
COLAB = os.path.join(W7, "colab")
STEM = "Week07_텍스트시각화"
COLAB_GH = "https://colab.research.google.com/github/itlects/2026-2_ai-data/blob/main/Week07/colab/"


def esc(s):
    return s.replace("|", "\\|")


def explain_table(rows):
    out = ["| 코드 | 뜻 |", "|---|---|"]
    for a, b in rows:
        out.append(f"| `{esc(a)}` | {esc(b)} |")
    return "\n".join(out)


def overview_md(version):
    rows = ["| 워크북 | 셀 | 실습본 TODO |", "|---|---|---|"]
    for wb in make_main.WORKBOOKS:
        cells = [c for st in wb["steps"] for c in st["cells"]]
        rows.append(f"| {wb['name']} | 셀 {cells[0]['no']} ~ {cells[-1]['no']} ({len(cells)}개) | "
                    f"{sum(1 for c in cells if c['todo'])}곳 |")
    return f"""# 7주차 · 텍스트 데이터의 시각화 — {version}

**인공지능과 데이터 활용** · 실제 **온라인 댓글 300건**(네이버 영화 한 줄 평)과 **뉴스 기사 제목 350건**(연합뉴스)을
단어로 나눠 세고 **빈도표·막대그래프·워드클라우드**로 시각화한 뒤, 같은 원문으로 받은 **AI 요약·키워드**를 원문 근거로 검증합니다.

{chr(10).join(rows)}

**따라 하는 방법:** 노션의 워크북 페이지를 위에서부터 읽으며, 이 노트북의 **같은 번호 셀(▶ 셀 0-1, 0-2 …)** 을 `Shift+Enter`로 하나씩 실행합니다.
셀마다 **실행 후 확인**을 보고 내 결과와 비교합니다. 실습본은 `TODO`의 `...`을 채운 뒤 실행합니다. 한 번에 실행하려면 `런타임 → 모두 실행`(약 1~2분).

> 데이터: 네이버 영화 140자평(NSMC, CC0) 300건 · 연합뉴스 기사 제목(KLUE-YNAT, CC BY-SA 4.0) 350건.
> 수업 화면용으로 욕설·성적·혐오 표현은 걸러 냈습니다. 그래도 불편한 문장이 보이면 강의자에게 알려 주세요.
"""


def notebook(version):
    """(cells, meta) — meta[i] = 셀 번호(코드 셀)"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"colab": {"provenance": [], "toc_visible": True},
                   "kernelspec": {"name": "python3", "display_name": "Python 3"},
                   "language_info": {"name": "python"}}
    cells = [nbf.v4.new_markdown_cell(overview_md("완성본" if version == "solution" else "실습본 (TODO 채우기)"))]
    for wb in make_main.WORKBOOKS:
        cells.append(nbf.v4.new_markdown_cell(f"---\n# {wb['name']}\n**목표** {wb['goal']}"))
        for st in wb["steps"]:
            cells.append(nbf.v4.new_markdown_cell(f"## {st['title']}\n{st['concept']}"))
            for c in st["cells"]:
                head = f"**▶ 셀 {c['no']}. {c['title']}** — 실행 후 확인: {c['check']}"
                if c["todo"] and version == "practice":
                    head += "  \n✏️ `TODO`의 `...`을 채운 뒤 실행하세요."
                cells.append(nbf.v4.new_markdown_cell(head))
                src = c["todo"] if (version == "practice" and c["todo"]) else c["src"]
                cells.append(nbf.v4.new_code_cell(src, metadata={"w7_cell": c["no"]}))
                parts = []
                if c["explain"]:
                    parts.append("**코드 읽기**\n\n" + explain_table(c["explain"]))
                if c["try_"]:
                    parts.append(f"**직접 바꿔 보기:** {c['try_']}")
                if parts:
                    cells.append(nbf.v4.new_markdown_cell("\n\n".join(parts)))
            if st["after"]:
                cells.append(nbf.v4.new_markdown_cell(st["after"]))
        if wb.get("after"):
            cells.append(nbf.v4.new_markdown_cell(wb["after"].strip("\n")))
    nb.cells = cells
    return nb


# ─────────────────────────────────────────────── 노션 내보내기
def outputs_text(cell, max_lines=24):
    out = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream" and o.get("name") == "stdout":
            out.append("".join(o["text"]))
        elif "data" in o and "text/plain" in o["data"] and "image/png" not in o["data"]:
            out.append("".join(o["data"]["text/plain"]) + "\n")
    lines = "".join(out).rstrip("\n").split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"... (이하 {len(lines) - max_lines}줄 생략)"]
    return "\n".join(lines).strip("\n")


GH_DOCS = {0: "워크북0_실습준비_데이터연결.md", 1: "워크북1_댓글워드클라우드.md",
           2: "워크북2_뉴스워드클라우드.md", 3: "워크북3_AI요약키워드비교.md"}


def to_github_md(text):
    """노션 전용 태그를 GitHub 마크다운으로 바꾼다"""
    text = re.sub(r'<callout icon="([^"]*)"[^>]*>\n(.*?)\n</callout>',
                  lambda m: "> " + m.group(1) + " " + m.group(2).replace("\n", "\n> "), text, flags=re.S)
    return text.replace("```plain text", "```text")


def export_notion(nb, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    by_no = {c.metadata.get("w7_cell"): c for c in nb.cells if c.cell_type == "code"}
    nb_link = f"[실습본]({COLAB_GH}{STEM}_실습.ipynb) · [완성본]({COLAB_GH}{STEM}_완성.ipynb)"
    for wb in make_main.WORKBOOKS:
        cells = [c for st in wb["steps"] for c in st["cells"]]
        b = [f"<callout icon=\"🎯\" color=\"blue_bg\">\n<b>목표</b> {wb['goal']}\n</callout>", "",
             f"<b>노트북</b> {nb_link} — 이 페이지의 <b>▶ 셀 번호</b>와 노트북의 셀 번호·코드가 같습니다. "
             f"위에서부터 읽으며 같은 번호 셀을 <code>Shift+Enter</code>로 하나씩 실행하고, <b>실행 결과</b>·<b>✔ 실행 후 확인</b>과 비교합니다.", "",
             "| 단계 | 셀 | 하는 일 |", "| --- | --- | --- |"]
        for st in wb["steps"]:
            nos = [c["no"] for c in st["cells"]]
            rng = "–" if not nos else (nos[0] if len(nos) == 1 else f"{nos[0]} ~ {nos[-1]}")
            todo = sum(1 for c in st["cells"] if c["todo"])
            what = ", ".join(c["title"] for c in st["cells"]) or "(읽기)"
            b.append(f"| {esc(st['title'])} | {rng}{' (TODO ' + str(todo) + ')' if todo else ''} | {esc(what)} |")
        b.append("")
        for st in wb["steps"]:
            b += [f"## {st['title']}", "", st["concept"], ""]
            if st["notion_only"]:
                b += [st["notion_only"], ""]
            for c in st["cells"]:
                b += [f"### ▶ 셀 {c['no']}. {c['title']}", "", "```python\n" + c["src"] + "\n```", ""]
                if c["todo"]:
                    b += ["<callout icon=\"✏️\" color=\"yellow_bg\">\n실습본에서는 <code># TODO</code> 아래 줄이 <code>...</code>으로 비어 있습니다. "
                          "먼저 힌트를 보고 직접 써서 실행한 뒤, 막히면 위 코드와 비교하세요.\n</callout>", ""]
                code_cell = by_no.get(c["no"])
                res = outputs_text(code_cell) if (code_cell is not None and c["no"] != "0-1") else ""
                res = res.replace("Colab이 아니므로 다운로드 창은 생략 (zip 파일은 현재 폴더에 있음)",
                                  "(Colab에서는 여기서 week07_results.zip, week07_figures.zip 두 파일이 내려받아짐)")
                if res:
                    b += ["<b>실행 결과</b>", "", "```plain text\n" + res + "\n```", ""]
                for f in c["figs"]:
                    b += [f"![셀 {c['no']} 실행 결과 — {f}]({make_main.GH}{f})", ""]
                b += [f"✔ <b>실행 후 확인:</b> {c['check']}", ""]
                if c["explain"]:
                    b += ["<b>코드 읽기</b>", ""] + [f"- `{a}` — {m}" for a, m in c["explain"]] + [""]
                if c["try_"]:
                    b += [f"🔁 <b>직접 바꿔 보기:</b> {c['try_']}", ""]
            if st["after"]:
                b += [st["after"], ""]
        if wb.get("after"):
            b += ["## 정리", "", wb["after"].strip("\n"), ""]
        text = "\n".join(b).rstrip() + "\n"
        with open(os.path.join(out_dir, f"notion_wb{wb['no']}.md"), "w", encoding="utf-8") as fh:
            fh.write(text)
        with open(os.path.join(W7, "workbook", GH_DOCS[wb["no"]]), "w", encoding="utf-8") as fh:   # GitHub용 같은 내용
            fh.write(f"# {wb['name']}\n\n" + to_github_md(text))
    print("노션 본문 저장:", out_dir)


def main():
    kernel = sys.argv[sys.argv.index("--execute") + 1] if "--execute" in sys.argv else None
    notion_dir = sys.argv[sys.argv.index("--notion") + 1] if "--notion" in sys.argv else None
    os.makedirs(COLAB, exist_ok=True)

    nbf.write(build(make_extra.youtube_cells("선택 과제"), "solution"), os.path.join(COLAB, "Week07_00_유튜브댓글수집.ipynb"))
    nbf.write(build(make_extra.drive_prep_cells(""), "solution"), os.path.join(COLAB, "Week07_00_데이터준비_Drive저장.ipynb"))

    pra = notebook("practice")
    print(STEM, "TODO", sum(1 for wb in make_main.WORKBOOKS for st in wb["steps"] for c in st["cells"] if c["todo"]), "곳",
          "| 코드 셀", sum(1 for c in pra.cells if c.cell_type == "code"))
    nbf.write(pra, os.path.join(COLAB, STEM + "_실습.ipynb"))

    sol = notebook("solution")
    if kernel:
        from nbclient import NotebookClient
        work = tempfile.mkdtemp(prefix="w7_")
        NotebookClient(sol, timeout=900, kernel_name=kernel, resources={"metadata": {"path": work}}).execute()
        errs = [(c.metadata.get("w7_cell"), o.get("ename"), o.get("evalue")) for c in sol.cells if c.cell_type == "code"
                for o in c.get("outputs", []) if o.get("output_type") == "error"]
        print("  실행 완료, 오류", len(errs), "개 | 작업폴더", work, errs)
        for d, dest in [("figures", "figures"), ("results", "examples")]:
            os.makedirs(os.path.join(W7, dest), exist_ok=True)
            for f in sorted(os.listdir(os.path.join(work, d))):
                if not f.startswith("test_"):
                    shutil.copy(os.path.join(work, d, f), os.path.join(W7, dest))
        sol.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
        if notion_dir:
            export_notion(sol, notion_dir)
    nbf.write(sol, os.path.join(COLAB, STEM + "_완성.ipynb"))


if __name__ == "__main__":
    main()
