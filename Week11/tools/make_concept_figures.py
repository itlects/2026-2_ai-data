"""11주차 노션·노트북용 개념 그림 c1~c6 생성.

python tools/make_concept_figures.py → figures/c*.png
"""
from pathlib import Path

import koreanize_matplotlib  # noqa: F401
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)
plt.rcParams["axes.unicode_minus"] = False

BLUE, ORANGE, GRAY, GREEN, RED, PURPLE = "#2b6cb0", "#dd6b20", "#718096", "#2f855a", "#c53030", "#6b46c1"


def box(ax, x, y, w, h, text, fc, ec=None, fs=12, color="black", weight="normal"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec=ec or fc, lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight)


def arrow(ax, x1, y1, x2, y2, color="0.3"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18, color=color, lw=1.8))


def blank(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax


def save(fig, name):
    fig.savefig(FIG / name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# c1 수업 흐름
fig, ax = blank(13, 3.2)
steps = [("① 수집", "기상청 ASOS\n시간자료 43,823행", "#ebf4ff"),
         ("② 가공", "시간 → 일자료\n품질 점검", "#e6fffa"),
         ("③ 탐색", "변동성·계절성\n그래프", "#fefcbf"),
         ("④ 예측", "단순 규칙 3 vs\nAI 모델 2", "#feebc8"),
         ("⑤ 평가", "MAE·RMSE\n해석", "#fed7d7")]
for i, (t, s, fc) in enumerate(steps):
    x = 0.3 + i * 2.55
    box(ax, x, 0.5, 2.1, 2.2, "", fc, ec="0.6")
    ax.text(x + 1.05, 2.15, t, ha="center", fontsize=15, weight="bold")
    ax.text(x + 1.05, 1.25, s, ha="center", va="center", fontsize=11.5)
    if i < 4:
        arrow(ax, x + 2.15, 1.6, x + 2.5, 1.6)
ax.set_title("11주차 수업 흐름: 기상 관측 데이터 → 하루 뒤 기온 예측", fontsize=15, weight="bold")
save(fig, "c1_lesson_flow.png")

# c2 시간자료 → 일자료 (실제 2025-01-10 값)
raw = pd.read_csv(ROOT / "data" / "daegu_asos_hourly_2021_2025.csv", parse_dates=["일시"])
ex = raw[raw["일시"].dt.normalize() == "2025-01-10"].set_index("일시")
et = ex["기온(°C)"]
hv = lambda h: f"{et.iloc[h]:.1f}"
fig, ax = blank(13, 5.2)
ax.text(2.4, 4.85, "시간자료 (한 행 = 1시간)", ha="center", fontsize=13, weight="bold", color=BLUE)
rows = [("일시", "기온", "강수량"), ("2025-01-10 00:00", hv(0), "(빈칸)"), ("2025-01-10 01:00", hv(1), "(빈칸)"),
        ("…", "…", "…"), ("2025-01-10 14:00", hv(14), "(빈칸)"), ("…", "…", "…"), ("2025-01-10 23:00", hv(23), "(빈칸)")]
for r, row in enumerate(rows):
    y = 4.2 - r * 0.52
    fc = "#bee3f8" if r == 0 else ("white" if r % 2 else "#f7fafc")
    for k, (val, w, x0) in enumerate(zip(row, [2.4, 1.0, 1.0], [0.2, 2.6, 3.6])):
        ax.add_patch(plt.Rectangle((x0, y), w, 0.5, fc=fc, ec="0.7"))
        ax.text(x0 + w / 2, y + 0.25, val, ha="center", va="center", fontsize=10.5,
                weight="bold" if r == 0 else "normal")
ax.text(2.4, 0.35, "같은 날짜 24행", ha="center", fontsize=11, color=GRAY)
ax.annotate("", xy=(4.75, 0.65), xytext=(4.75, 4.15), arrowprops=dict(arrowstyle="-", color=BLUE, lw=2))
box(ax, 5.3, 1.6, 2.6, 1.9, "groupby('날짜')\n.agg(...)\n\n24개 → 1개로 요약", "#e6fffa", ec=GREEN, fs=11.5)
arrow(ax, 4.9, 2.55, 5.25, 2.55); arrow(ax, 7.95, 2.55, 8.3, 2.55)
ax.text(10.6, 4.85, "일자료 (한 행 = 하루)", ha="center", fontsize=13, weight="bold", color=GREEN)
rows2 = [("열", "계산", "값"), ("평균기온", "mean", f"{et.mean():.1f}"), ("최고기온", "max", f"{et.max():.1f}"),
         ("최저기온", "min", f"{et.min():.1f}"), ("일교차", "최고−최저", f"{et.max() - et.min():.1f}"),
         ("일강수량", "sum", f"{ex['강수량(mm)'].fillna(0).sum():.1f}"), ("관측수", "count", f"{et.count()}")]
for r, row in enumerate(rows2):
    y = 4.2 - r * 0.52
    fc = "#c6f6d5" if r == 0 else ("white" if r % 2 else "#f7fafc")
    for val, w, x0 in zip(row, [1.5, 1.6, 1.0], [8.4, 9.9, 11.5]):
        ax.add_patch(plt.Rectangle((x0, y), w, 0.5, fc=fc, ec="0.7"))
        ax.text(x0 + w / 2, y + 0.25, val, ha="center", va="center", fontsize=10.5,
                weight="bold" if r == 0 else "normal")
ax.text(10.45, 0.35, "관측수 < 24 인 날 → 기온 값을 결측(NaN) 처리", ha="center", fontsize=11, color=RED)
save(fig, "c2_hourly_to_daily.png")

# c3 lag window
fig, ax = blank(13, 3.6)
labels = ["D−7", "D−6", "D−5", "D−4", "D−3", "D−2", "D−1", "D"]
for i, lab in enumerate(labels):
    x = 0.4 + i * 1.5
    fc = "#bee3f8" if i < 7 else "#feebc8"
    box(ax, x, 1.4, 1.2, 1.0, lab, fc, ec=BLUE if i < 7 else ORANGE, fs=13, weight="bold")
    ax.text(x + 0.6, 1.05, f"lag_{7 - i}" if i < 7 else "정답", ha="center", fontsize=11,
            color=BLUE if i < 7 else ORANGE)
ax.annotate("", xy=(0.4, 2.75), xytext=(10.9, 2.75), arrowprops=dict(arrowstyle="<->", color=BLUE, lw=1.6))
ax.text(5.65, 2.95, "입력: 지난 7일 평균기온 (+ 1년 중 위치)", ha="center", fontsize=12.5, color=BLUE)
ax.text(11.6, 2.75, "예측할 날", ha="center", fontsize=12.5, color=ORANGE)
ax.text(6.5, 0.3, "temp.shift(1) → 1일 전 값이 D 행으로 내려옴  ·  하루씩 밀면서 365번 반복(슬라이딩 윈도우)",
        ha="center", fontsize=11, color=GRAY)
save(fig, "c3_lag_window.png")

# c4 time split
fig, ax = blank(13, 3.4)
years = ["2021", "2022", "2023", "2024", "2025"]
for i, y in enumerate(years):
    x = 0.4 + i * 2.45
    fc, ec = ("#c6f6d5", GREEN) if i < 4 else ("#fed7d7", RED)
    box(ax, x, 1.5, 2.3, 1.0, y, fc, ec=ec, fs=14, weight="bold")
ax.text(5.1, 2.85, "학습(train) 1,446일: 규칙을 배우는 기간", ha="center", fontsize=12.5, color=GREEN)
ax.text(11.4, 2.85, "평가(test) 365일", ha="center", fontsize=12.5, color=RED)
ax.text(6.5, 0.85, "✔ 과거로 배우고 미래로 시험  ·  ✘ 날짜를 무작위로 섞으면 '미래로 과거를 맞히는' 반칙이 생김",
        ha="center", fontsize=11.5)
ax.text(6.5, 0.35, "2022-08-06(23시간 관측)이 정답 또는 입력에 들어간 8일, 처음 7일은 제외",
        ha="center", fontsize=10.5, color=GRAY)
save(fig, "c4_time_split.png")

# c5 simple rules on a real example (2025-01-10, 한파 이틀째)
t = raw.groupby(raw["일시"].dt.normalize())["기온(°C)"].mean()
d = pd.Timestamp("2025-01-10")
hist = t.loc[d - pd.Timedelta(days=7): d - pd.Timedelta(days=1)]
x = np.arange(-7, 0)
s, b = np.polyfit(x, hist.values, 1)
fig, ax = plt.subplots(figsize=(10, 4.4))
ax.plot(x, hist.values, "o-", color=BLUE, lw=2, label="지난 7일 실제")
xx = np.linspace(-7, 0, 20)
ax.plot(xx, s * xx + b, color=PURPLE, ls=":", lw=2)
ax.scatter([0], [t.loc[d]], s=140, color="black", zorder=5, label=f"실제 {t.loc[d]:.1f}°C")
ax.scatter([0], [hist.iloc[-1]], s=110, marker="s", color=GRAY, zorder=5, label=f"① 어제 그대로 {hist.iloc[-1]:.1f}")
ax.scatter([0], [hist.mean()], s=110, marker="D", color=GREEN, zorder=5, label=f"② 7일 평균 {hist.mean():.1f}")
ax.scatter([0], [b], s=130, marker="^", color=PURPLE, zorder=5, label=f"③ 7일 직선추세 {b:.1f}")
ax.set_xticks(range(-7, 1), [f"D{k}" if k else "D\n(1/10)" for k in range(-7, 1)])
ax.set(title="단순 추세 예측 3가지 — 2025년 1월 10일(한파 이틀째) 예", ylabel="평균기온(°C)")
ax.axvline(-0.5, color="0.8", ls="--")
ax.legend(loc="lower left", fontsize=10)
fig.tight_layout()
save(fig, "c5_simple_rules.png")

# c6 AI train/predict
fig, ax = blank(13, 3.8)
box(ax, 0.3, 1.2, 3.2, 1.8, "학습 데이터\n2021~2024\n(입력 9개 → 정답) 1,446쌍", "#c6f6d5", ec=GREEN, fs=11.5)
arrow(ax, 3.6, 2.1, 4.4, 2.1)
box(ax, 4.5, 1.2, 3.4, 1.8, "model.fit()\n선형회귀: 가중치 학습\n랜덤포레스트: 트리 200개", "#feebc8", ec=ORANGE, fs=11.5)
arrow(ax, 8.0, 2.1, 8.8, 2.1)
box(ax, 8.9, 1.2, 3.8, 1.8, "model.predict()\n2025년 입력 365개\n→ 예측 365개 → 실제와 비교", "#fed7d7", ec=RED, fs=11.5)
ax.text(6.5, 0.45, "규칙을 사람이 정하면 '단순 추세', 데이터에서 찾게 하면 'AI(머신러닝)'", ha="center", fontsize=12, color=GRAY)
save(fig, "c6_ai_train_predict.png")
