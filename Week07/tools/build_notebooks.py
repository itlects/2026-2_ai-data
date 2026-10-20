"""7주차 노트북 생성 + 완성본 실행 (강의자용).

  python Week07/tools/build_notebooks.py [--execute KERNEL] [--data-dir 로컬데이터폴더]

실습본·완성본을 같은 원고(make_main.py)에서 만든다. 보조 노트북(유튜브 수집, Drive 준비)은 한 벌만 만든다.
--execute 를 주면 완성본을 처음부터 끝까지 실행해 출력까지 저장하고, 그림을 Week07/figures/,
결과 CSV를 Week07/examples/ 로 복사한다.
--data-dir 를 주면 실행할 때만 DATA_SOURCE 를 그 폴더로 바꾼다(저장되는 노트북은 "auto" 그대로).
"""
import os
import shutil
import sys
import tempfile

import nbformat as nbf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nb_common import build, count_todo  # noqa: E402
import make_main  # noqa: E402
import make_extra  # noqa: E402
from expect_values import fill_expect  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W7 = os.path.join(HERE, "..")
COLAB = os.path.join(W7, "colab")


def main():
    kernel = sys.argv[sys.argv.index("--execute") + 1] if "--execute" in sys.argv else None
    data_dir = sys.argv[sys.argv.index("--data-dir") + 1] if "--data-dir" in sys.argv else None
    os.makedirs(COLAB, exist_ok=True)

    # 보조 노트북 (출력 없이 저장)
    nbf.write(build(make_extra.youtube_cells("선택 과제"), "solution"),
              os.path.join(COLAB, "Week07_00_유튜브댓글수집.ipynb"))
    nbf.write(build(make_extra.drive_prep_cells(""), "solution"),
              os.path.join(COLAB, "Week07_00_데이터준비_Drive저장.ipynb"))

    stem = "Week07_텍스트시각화"
    sol_cells = fill_expect(make_main.cells("완성본"))
    pra_cells = fill_expect(make_main.cells("실습본 (TODO 채우기)"))
    print(stem, "TODO", count_todo(pra_cells), "곳")
    nbf.write(build(pra_cells, "practice"), os.path.join(COLAB, stem + "_실습.ipynb"))

    sol = build(sol_cells, "solution")
    if kernel:
        from nbclient import NotebookClient
        work = tempfile.mkdtemp(prefix="w7_")
        loader_idx = None
        if data_dir:
            for i, c in enumerate(sol.cells):
                if c.cell_type == "code" and 'DATA_SOURCE = "auto"' in c.source:
                    loader_idx, original = i, c.source
                    c.source = c.source.replace('DATA_SOURCE = "auto"', f'DATA_SOURCE = "{os.path.abspath(data_dir)}"')
        NotebookClient(sol, timeout=900, kernel_name=kernel,
                       resources={"metadata": {"path": work}}).execute()
        if loader_idx is not None:                       # 저장본에는 "auto"로 되돌리고 경로 출력도 지움
            sol.cells[loader_idx].source = original
            for o in sol.cells[loader_idx].outputs:
                if o.get("output_type") == "stream":
                    o["text"] = o["text"].replace(os.path.abspath(data_dir) + "/", GITHUB_HINT)
        errs = [(i, o.get("ename"), o.get("evalue")) for i, c in enumerate(sol.cells) if c.cell_type == "code"
                for o in c.get("outputs", []) if o.get("output_type") == "error"]
        print("  실행 완료, 오류", len(errs), "개 | 작업폴더", work, errs)
        os.makedirs(os.path.join(W7, "figures"), exist_ok=True)
        os.makedirs(os.path.join(W7, "examples"), exist_ok=True)
        for f in sorted(os.listdir(os.path.join(work, "figures"))):
            shutil.copy(os.path.join(work, "figures", f), os.path.join(W7, "figures"))
        for f in sorted(os.listdir(os.path.join(work, "results"))):
            shutil.copy(os.path.join(work, "results", f), os.path.join(W7, "examples"))
        sol.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
    nbf.write(sol, os.path.join(COLAB, stem + "_완성.ipynb"))


GITHUB_HINT = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week07/data/"

if __name__ == "__main__":
    main()
