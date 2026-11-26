"""13주차 개념 그림 c1~c4 (figures/). 숫자는 실제 데이터·예비 응답 점검 결과 값."""
from pathlib import Path
import koreanize_matplotlib  # noqa: F401
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
plt.rcParams["axes.unicode_minus"] = False
INK, MUTED = "#1f2933", "#6b7280"


def box(ax, x, y, w, h, text, fc, fs=11, color="white", weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="none"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=color, fontweight=weight, linespacing=1.4)


def arrow(ax, x1, y1, x2, y2, color=MUTED):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8))


# c1 수업 흐름 ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 3.6))
ax.set(xlim=(0, 12), ylim=(0, 3.6)); ax.axis("off")
steps = [("① 데이터\n365일", "#457b9d", "1단계"), ("② 사실표\n13줄", "#457b9d", "2단계"),
         ("③ 사람 버전\n먼저 쓰기", "#6c757d", "3단계"), ("④ 프롬프트\nv1 → v4", "#2a9d8f", "4~8단계"),
         ("⑤ 사람이\n검증·편집", "#e76f51", "9단계"), ("⑥ 카드뉴스\nPNG 4장", "#264653", "10단계"),
         ("⑦ 블라인드\n비교", "#6c757d", "11단계")]
w, gap = 1.45, 0.24
for i, (t, c, s) in enumerate(steps):
    x = 0.2 + i * (w + gap)
    box(ax, x, 1.2, w, 1.4, t, c, fs=11.5)
    ax.text(x + w / 2, 0.85, s, ha="center", fontsize=9.5, color=MUTED)
    if i < len(steps) - 1:
        arrow(ax, x + w + 0.02, 1.9, x + w + gap - 0.02, 1.9)
ax.text(6, 3.25, "13주차 수업 흐름 — 데이터로 사실을 정하고, AI로 쓰고, 사람이 책임진다",
        ha="center", fontsize=13.5, fontweight="bold", color=INK)
ax.annotate("", (0.2 + 2 * (w + gap) + w / 2, 0.55), (0.2 + 6 * (w + gap) + w / 2, 0.55),
            arrowprops=dict(arrowstyle="<->", color="#6c757d", lw=1.2, ls="--"))
ax.text(0.2 + 4 * (w + gap) + w / 2, 0.15, "같은 기준으로 비교 (사람 vs AI)", ha="center",
        fontsize=9.5, color="#6c757d")
fig.savefig(FIG / "c1_lesson_flow.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# c2 프롬프트 사다리 ----------------------------------------------------------
fig, ax = plt.subplots(figsize=(12.5, 5.4))
ax.set(xlim=(0, 12.5), ylim=(0, 5.4)); ax.axis("off")
rows = [("v1  그냥 부탁", "\"2025년 대구 날씨 카드뉴스 4장 써 줘\"", "숫자를 지어냄", "8개", "#9ca3af"),
        ("v2  + 근거", "+ 사실표 13줄, '사실표에 없는 숫자 금지'", "숫자는 맞지만 긴 글", "0개", "#7fb3d5"),
        ("v3  + 역할·독자·형식", "+ SNS 담당자, 대학생, [카드N] 제목/본문, 글자 수", "형식 OK, 딱딱·60자 초과", "0개", "#48a9a6"),
        ("v4  + 예시(Few-shot)", "+ 다른 주제의 잘 쓴 카드 2장", "쓸 만함, 단 '추운 달=1월' 오류", "1개*", "#2a9d8f")]
ax.text(0.1, 5.05, "프롬프트 사다리 — 앞 단계의 실패가 다음 한 줄을 부른다", fontsize=13.5,
        fontweight="bold", color=INK)
ax.text(8.3, 4.55, "드러난 문제", fontsize=10, color=MUTED)
ax.text(11.6, 4.55, "사실표에 없는 숫자", fontsize=10, color=MUTED, ha="center")
for i, (name, add, prob, n, c) in enumerate(rows):
    y = 3.55 - i * 1.0
    x0 = 0.1 + i * 0.35
    box(ax, x0, y, 2.2, 0.75, name, c, fs=11)
    ax.text(x0 + 2.35, y + 0.375, add, va="center", fontsize=10, color=INK)
    ax.text(8.3, y + 0.375, prob, va="center", fontsize=10, color="#b42318" if i == 0 else INK)
    ax.text(11.6, y + 0.375, n, va="center", ha="center", fontsize=13, fontweight="bold",
            color="#b42318" if i == 0 else "#14532d")
ax.text(0.1, 0.12, "* 오프라인 예비 응답 기준. v4의 1개는 39(=7월 18일+8월 21일, AI가 더한 값) → 틀린 숫자는 아님. "
        "실제 AI 응답은 실행마다 달라집니다.", fontsize=8.8, color=MUTED)
fig.savefig(FIG / "c2_prompt_ladder.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# c3 숫자 점검 원리 -----------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.set(xlim=(0, 11), ylim=(0, 4.6)); ax.axis("off")
ax.text(0.1, 4.25, "check_numbers() — 글 속 숫자를 모두 찾아 사실표와 맞춰 본다", fontsize=13.5,
        fontweight="bold", color=INK)
box(ax, 0.1, 2.35, 4.2, 1.45, "사실표 (2단계, 데이터로 계산)\n15.2 · 37.4 · −10.6 · 48 · 18 · 21\n28.7 · 1.2 · 1,029.0 · 248.0 · 102.3 …",
    "#457b9d", fs=10.5)
ax.text(5.0, 3.55, "v1 응답의 한 줄", fontsize=10, color=MUTED)
tokens = [("8월 2일 낮 최고 ", None), ("39.8", False), ("°C! 폭염 ", None), ("41", False),
          ("일, 열대야도 ", None), ("30", False), ("일…", None)]
x = 5.0
for t, ok in tokens:
    col = INK if ok is None else ("#b42318" if ok is False else "#14532d")
    txt = ax.text(x, 3.05, t, fontsize=12, color=col, fontweight="bold" if ok is not None else "normal")
    x += 0.155 * len(t) + (0.12 if ok is not None else 0.05)
arrow(ax, 4.35, 3.05, 4.9, 3.05)
box(ax, 5.0, 1.55, 2.6, 0.9, "× 39.8 · 41 · 30\n사실표에 없음", "#b42318", fs=10.5)
box(ax, 7.9, 1.55, 3.0, 0.9, "○ 8 · 2\n사실표에 있음 (8월·2월)", "#14532d", fs=10.5)
ax.text(0.1, 0.95, "×는 '사람이 확인할 숫자' 표시입니다.  ① AI가 더한 계산값(39)도 ×가 될 수 있고", fontsize=10.5, color=INK)
ax.text(0.1, 0.55, "② 숫자가 없는 오류('가장 추운 달은 1월')나 사실표 숫자로 조합된 틀린 날짜('8월 2일')는 ○로 통과합니다.",
        fontsize=10.5, color=INK)
ax.text(0.1, 0.15, "→ 자동 점검은 거름망이고, 마지막 판단은 사람이 합니다.", fontsize=10.5, color="#e76f51",
        fontweight="bold")
fig.savefig(FIG / "c3_number_check.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# c4 다음 단어 예측 ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.set(xlim=(0, 11), ylim=(0, 4.8)); ax.axis("off")
ax.text(0.1, 4.45, "생성형 AI는 '사실'이 아니라 '다음에 올 그럴듯한 말'을 고른다", fontsize=13.5,
        fontweight="bold", color=INK)
box(ax, 0.1, 2.35, 4.6, 1.1, "\"2025년 대구에서 가장 더운 날은\"", "#264653", fs=12)
arrow(ax, 4.8, 2.9, 5.5, 2.9)
cands = [("8월 초", 0.9), ("7월 말", 0.75), ("8월 15일", 0.5), ("7월 7일", 0.25)]
for i, (t, L) in enumerate(cands):
    y = 3.7 - i * 0.55
    ax.add_patch(FancyBboxPatch((5.6, y), L * 3.2, 0.38, boxstyle="round,pad=0.01", fc="#2a9d8f",
                                ec="none", alpha=0.35 + 0.65 * L))
    ax.text(5.7, y + 0.19, t, va="center", fontsize=11, color=INK, fontweight="bold")
ax.text(9.0, 3.9, "막대 길이 = 그럴듯함\n(설명용 모식도)", fontsize=9, color=MUTED, va="top")
ax.text(0.1, 1.2, "· 모델은 '대구는 8월 초가 덥다'는 많은 글의 패턴으로 다음 말을 고릅니다. 실제 정답(7월 7일, 37.4°C)은 데이터에 있습니다.",
        fontsize=10.3, color=INK)
ax.text(0.1, 0.75, "· 그래서 학습 시점 이후 숫자나 지역 관측값처럼 모르는 사실도 그럴듯하게 만들어 낼 수 있습니다(환각).",
        fontsize=10.3, color=INK)
ax.text(0.1, 0.3, "→ 해결: 프롬프트에 '근거(사실표)'를 넣고, 결과를 사람이 확인한다.", fontsize=10.5,
        color="#e76f51", fontweight="bold")
fig.savefig(FIG / "c4_next_word.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("저장:", *sorted(p.name for p in FIG.glob("c*.png")))
