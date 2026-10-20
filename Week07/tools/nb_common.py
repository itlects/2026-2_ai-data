"""노트북 생성 공통 도구 (강의자용). 실습본·완성본을 같은 원고에서 만든다.

셀 표기
  md("...")                 마크다운
  code("완성 코드")          두 버전 동일
  code("완성 코드", todo="실습본 코드")   실습본에서는 todo 코드로 바뀜
"""
import nbformat as nbf


def md(src):
    return ("md", src.strip("\n"), None)


def code(src, todo=None):
    return ("code", src.strip("\n"), None if todo is None else todo.strip("\n"))


def build(cells, version):
    """version: 'solution' | 'practice'"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "colab": {"provenance": [], "toc_visible": True},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    }
    out = []
    for kind, src, todo in cells:
        if kind == "md":
            out.append(nbf.v4.new_markdown_cell(src))
        else:
            body = todo if (version == "practice" and todo is not None) else src
            out.append(nbf.v4.new_code_cell(body))
    nb.cells = out
    return nb


def count_todo(cells):
    return sum(1 for k, _, t in cells if k == "code" and t is not None)
