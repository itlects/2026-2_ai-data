"""6주차 노트북 생성 + 완성본 실행 (강의자용).

  python Week06/tools/build_notebooks.py [--execute KERNEL]

실습본·완성본을 같은 원고(make_wb0.py, make_main.py)에서 만든다.
--execute 를 주면 완성본을 처음부터 끝까지 실행해 출력까지 저장하고, 그림을 Week06/figures/ 로 복사한다.
"""
import os
import shutil
import sys
import tempfile

import nbformat as nbf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nb_common import build, count_todo  # noqa: E402
import make_wb0  # noqa: E402
import make_main  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
COLAB = os.path.join(HERE, "..", "colab")
FIG = os.path.join(HERE, "..", "figures")

BOOKS = [
    ("Week06_00_감성데이터수집", make_wb0.cells),
    ("Week06_리뷰감성분석", make_main.cells),
]


def main():
    kernel = None
    if "--execute" in sys.argv:
        kernel = sys.argv[sys.argv.index("--execute") + 1]
    os.makedirs(COLAB, exist_ok=True)
    for stem, fn in BOOKS:
        sol_cells = fn("완성본")
        pra_cells = fn("실습본 (TODO 채우기)")
        print(stem, "TODO", count_todo(pra_cells), "곳")
        pra = build(pra_cells, "practice")
        nbf.write(pra, os.path.join(COLAB, stem + "_실습.ipynb"))
        sol = build(sol_cells, "solution")
        out_path = os.path.join(COLAB, stem + "_완성.ipynb")
        if kernel:
            from nbclient import NotebookClient
            work = tempfile.mkdtemp(prefix="w6_")
            NotebookClient(sol, timeout=900, kernel_name=kernel,
                           resources={"metadata": {"path": work}}).execute()
            errs = [o for c in sol.cells if c.cell_type == "code"
                    for o in c.get("outputs", []) if o.get("output_type") == "error"]
            print("  실행 완료, 오류", len(errs), "개 | 작업폴더", work)
            for f in sorted(os.listdir(os.path.join(work, "figures"))):
                shutil.copy(os.path.join(work, "figures", f), FIG)
            for f in os.listdir(work):
                if f.endswith((".csv", ".json")):
                    shutil.copy(os.path.join(work, f), os.path.join(FIG, "..", "examples", f))
            sol.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
        nbf.write(sol, out_path)


if __name__ == "__main__":
    main()
