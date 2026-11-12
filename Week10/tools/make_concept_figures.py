"""노션 강의자료용 개념 그림 4장 → figures/c1~c4.png"""
from pathlib import Path

import koreanize_matplotlib  # noqa: F401
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1] / "figures"
OUT.mkdir(exist_ok=True)
BLUE, ORANGE, GREEN, GRAY, INK = "#2b6cb0", "#dd6b20", "#2f855a", "#718096", "#1a202c"


def box(ax, x, y, w, h, text, fc, ec=None, fs=11, color="white", weight="bold"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec or fc, lw=1.5))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight, linespacing=1.5)


def arrow(ax, x1, y1, x2, y2, color=GRAY):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18, color=color, lw=2))


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off")
    return fig, ax


# C1 수업 흐름
fig, ax = canvas(13, 3.4)
steps = [("① 데이터 불러오기", "승하차·혼잡도·121장소", BLUE), ("② 구조 이해·변환", "가로표 → 세로표(melt)", BLUE),
         ("③ 시각화", "막대·선·히트맵", BLUE), ("④ 혼잡도 비교", "이용 인원 ≠ 열차 혼잡", ORANGE),
         ("⑤ AI 예측 체험", "랜덤포레스트·MAE", GREEN), ("⑥ AI 서비스 비교", "실시간 도시데이터", GREEN)]
for i, (t, sub, col) in enumerate(steps):
    x = 0.3 + i * 2.13
    box(ax, x, 1.35, 1.8, 1.1, t, col, fs=11)
    ax.text(x + 0.9, 0.95, sub, ha="center", fontsize=9.5, color=INK)
    if i < len(steps) - 1:
        arrow(ax, x + 1.82, 1.9, x + 2.11, 1.9)
ax.text(0.3, 2.95, "10주차 수업 흐름 — 워크북 1(①~③) · 워크북 2(④~⑥)", fontsize=13, weight="bold", color=INK)
fig.savefig(OUT / "c1_lesson_flow.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# C2 가로 → 세로 변환
fig, ax = canvas(13, 5.2)
ax.text(0.2, 4.8, "가로 표(원본): 시간대가 열 이름에 들어 있음", fontsize=12, weight="bold", color=INK)
hdr = ["호선명", "지하철역", "08시-09시\n승차인원", "08시-09시\n하차인원", "18시-19시\n승차인원", "…"]
row = ["2호선", "강남", "63,086", "314,572", "313,031", "…"]
for j, (hh, rr) in enumerate(zip(hdr, row)):
    fc = "#e2e8f0" if j < 2 else "#bee3f8"
    box(ax, 0.2 + j * 0.95, 3.75, 0.9, 0.75, hh, fc, fs=8.5, color=INK, weight="bold")
    box(ax, 0.2 + j * 0.95, 3.0, 0.9, 0.65, rr, "white", ec="#cbd5e0", fs=9, color=INK, weight="normal")
arrow(ax, 6.2, 3.7, 7.0, 3.7, color=BLUE)
ax.text(6.6, 4.0, "melt", ha="center", fontsize=12, color=BLUE, weight="bold")
ax.text(7.2, 4.8, "세로 표(long): 한 행 = 역·시간·구분 하나", fontsize=12, weight="bold", color=INK)
hdr2 = ["호선명", "지하철역", "시간", "구분", "인원", "일평균(÷30)"]
rows2 = [["2호선", "강남", "8", "승차", "63,086", "2,103"], ["2호선", "강남", "8", "하차", "314,572", "10,486"],
         ["2호선", "강남", "18", "승차", "313,031", "10,434"], ["…", "…", "…", "…", "…", "…"]]
for j, hh in enumerate(hdr2):
    box(ax, 7.2 + j * 0.93, 3.95, 0.88, 0.55, hh, "#e2e8f0" if j < 2 else "#c6f6d5", fs=9, color=INK)
    for i, r in enumerate(rows2):
        box(ax, 7.2 + j * 0.93, 3.3 - i * 0.62, 0.88, 0.55, r[j], "white", ec="#cbd5e0", fs=9, color=INK, weight="normal")
ax.text(0.2, 1.9, "• 621개 역 × 48칸(24시간×승차/하차) = 29,808행", fontsize=11, color=INK)
ax.text(0.2, 1.4, "• '08시-09시 승차인원'의 앞 두 글자 → 시간 8, '승차' 포함 여부 → 구분", fontsize=11, color=INK)
ax.text(0.2, 0.9, "• 세로 표가 되면 groupby·pivot_table로 역별·시간별 합계와 그래프를 쉽게 만든다", fontsize=11, color=INK)
fig.savefig(OUT / "c2_wide_to_long.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# C3 세 가지 '붐빔' 데이터
fig, ax = canvas(13, 5.4)
ax.text(0.2, 5.0, "같은 '강남역'이라도 세 데이터는 서로 다른 것을 센다", fontsize=13, weight="bold", color=INK)
cards = [
    (BLUE, "역 승하차 인원", ["교통카드 개찰구 태그 수", "역 단위 · 1시간 · 한 달 합계", "단위: 명 (÷30 → 명/일)", "서울 열린데이터광장 OA-12252", "2026년 9월"]),
    (ORANGE, "열차 혼잡도", ["열차 안 탑승 인원 ÷ 정원", "역·방향 · 30분 · 평일/토/일", "단위: % (34% 좌석 다 참,\n100% 정원)", "서울교통공사 · 공공데이터포털", "2025년 3월 기준 파일"]),
    (GREEN, "장소 인구 (AI 예측)", ["KT 통신 신호로 추정한 인구", "역 주변 구역 · 실시간", "단위: 인구 범위 + 4단계", "+ 향후 12시간 AI 예측", "서울 실시간 도시데이터"]),
]
for i, (col, title, lines) in enumerate(cards):
    x = 0.2 + i * 4.3
    box(ax, x, 3.85, 4.0, 0.7, title, col, fs=13)
    ax.add_patch(FancyBboxPatch((x, 0.35), 4.0, 3.35, boxstyle="round,pad=0.02,rounding_size=0.08", fc="white", ec=col, lw=1.5))
    for k, ln in enumerate(lines):
        ax.text(x + 0.2, 3.35 - k * 0.65, "• " + ln, fontsize=10.5, color=INK, va="top")
fig.savefig(OUT / "c3_three_crowd_data.png", dpi=160, bbox_inches="tight"); plt.close(fig)

# C4 AI 예측과 평가
fig, ax = canvas(13, 5.6)
ax.text(0.2, 5.2, "10단계 AI 예측 실험: 처음 보는 역의 혼잡도를 맞힐 수 있을까?", fontsize=13, weight="bold", color=INK)
ax.text(0.2, 4.55, "입력 = 시각·호선·방향·그 시간 승차/하차   →   정답 = 평일 30분 혼잡도(%)", fontsize=11, color=INK)
box(ax, 0.2, 2.9, 2.8, 1.2, "학습 역 75%\n(205역)", BLUE, fs=12)
arrow(ax, 3.05, 3.5, 3.95, 3.5)
box(ax, 4.0, 2.9, 3.0, 1.2, "랜덤포레스트 학습\n(결정나무 200개)", GREEN, fs=12)
ax.text(5.7, 2.45, "모델 + 학습 역 평균(기준값)", ha="left", fontsize=9.5, color=GRAY)
box(ax, 0.2, 0.9, 2.8, 1.2, "평가 역 25%\n(68역, 학습 안 함)", GRAY, fs=12)
arrow(ax, 3.05, 1.5, 3.95, 1.5)
box(ax, 4.0, 0.9, 3.0, 1.2, "AI 예측 / 기준값 예측", "#4a5568", fs=12)
arrow(ax, 5.5, 2.85, 5.5, 2.15, color=GREEN)
arrow(ax, 7.05, 1.5, 7.95, 1.5)
box(ax, 8.0, 0.9, 2.3, 1.2, "실제 혼잡도와\n비교", "#a0aec0", fs=12)
arrow(ax, 10.35, 1.5, 10.75, 1.5)
box(ax, 10.8, 0.9, 2.0, 1.2, "MAE\n작을수록 좋음", "#2d3748", fs=12)
ax.text(0.2, 0.3, "핵심: 같은 역이 학습과 평가에 동시에 들어가지 않도록 '역 단위'로 나눈다 → 처음 보는 역에서의 실력을 잰다", fontsize=10.5, color=INK)
fig.savefig(OUT / "c4_ai_experiment.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("concept figures done")
