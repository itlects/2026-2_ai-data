# 9주차 추가 워크북 2 — 이미지 변형에 따른 AI 분류 성능 비교

# 9주차 추가 워크북 2 — 이미지 변형과 AI 분류의 강건성

**권장 35~40분 | 초급/심화 혼합 | Colab에서 순서대로 실행**

## 학습 목표
1. 이미지의 회전, 어두워짐, 잡음(노이즈)이 원본과 어떻게 다른지 관찰합니다.
2. 1차 워크북에서 배운 HOG + 선형 SVM 모델의 평가 정확도 변화를 확인합니다.
3. 학습 데이터에만 변형 이미지를 추가하는 **데이터 증강(Data Augmentation)** 을 체험합니다.

**사전 준비:** 9주차 이미지 데이터 60장(원·사각형·삼각형)은 코드가 자동 다운로드합니다. 학생은 별도 API 키나 GPU가 필요 없습니다.

**공정한 평가:** 45장 학습 / 15장 평가 분할을 유지하고, test의 도형 종류 및 파일 목록은 그대로 둡니다. 변형 조건별 테스트 이미지 15장에 대해 각각 점수를 계산합니다. 변형별 비교는 조건이 다른 별도 시험입니다.

데이터: [Google Drive 이미지 ZIP](https://drive.google.com/file/d/1KTzhtyobHIO5dRle5pYLOFYCsHzdLEDl/view) | [GitHub ZIP](https://github.com/itlects/2026-2_ai-data/raw/refs/heads/main/Week09/data/shapes60.zip)

## 1단계 — 이미지 데이터 불러오기

PNG 60개와 train 45장/test 15장을 확인하세요.

```python
from pathlib import Path
from io import BytesIO
import zipfile, requests
import pandas as pd
from IPython.display import display
from PIL import Image, ImageEnhance
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, ConfusionMatrixDisplay

ZIP_URL = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week09/data/shapes60.zip"
WORK = Path("/content/week09_robustness")
WORK.mkdir(parents=True, exist_ok=True)
r = requests.get(ZIP_URL, timeout=60)
r.raise_for_status()
with zipfile.ZipFile(BytesIO(r.content)) as z:
    z.extractall(WORK)
meta = pd.read_csv(WORK / "labels.csv")
print(meta.groupby(["split", "label"]).size())
assert len(meta) == 60
assert (meta.split == "train").sum() == 45
assert (meta.split == "test").sum() == 15
```

## 2단계 — 변형 전·후 이미지 4개 나란히 보기

회전·밝기·노이즈 이미지가 육안으로 어떻게 다른지 기록하세요.

```python
# 같은 평가 이미지에 회전 / 어둡게 / 노이즈를 적용합니다.
def transform(img, condition, seed=0):
    img = img.convert("RGB")
    if condition == "original":
        return img.copy()
    if condition == "rotate_35":
        return img.rotate(35, resample=Image.Resampling.BILINEAR, fillcolor=(245, 245, 245))
    if condition == "dark_40":
        return ImageEnhance.Brightness(img).enhance(0.4)
    if condition == "noise_45":
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, 45, size=np.asarray(img).shape)
        arr = np.clip(np.asarray(img).astype(float) + noise, 0, 255).astype("uint8")
        return Image.fromarray(arr)
    raise ValueError(f"알 수 없는 조건: {condition}")

conditions = ["original", "rotate_35", "dark_40", "noise_45"]
sample_path = meta.loc[meta.split == "test", "path"].iloc[0]
sample = Image.open(WORK / sample_path)
fig, axes = plt.subplots(1, 4, figsize=(12, 3))
for ax, condition in zip(axes, conditions):
    ax.imshow(transform(sample, condition, seed=42))
    ax.set_title(condition)
    ax.axis("off")
plt.tight_layout()
plt.show()
```

## 3단계 — 기본 이미지 분류 모델 학습

기존 워크북처럼 train 45장으로만 모델을 학습합니다.

```python
# HOG 특징은 밝기 변화로 생기는 경계 방향을 요약합니다.
def feature(img):
    gray = np.asarray(img.convert("L"))
    return hog(gray, orientations=9, pixels_per_cell=(8, 8),
               cells_per_block=(2, 2), feature_vector=True)

train_rows = meta.loc[meta.split == "train"].reset_index(drop=True)
test_rows = meta.loc[meta.split == "test"].reset_index(drop=True)
X_train = np.stack([feature(Image.open(WORK / p)) for p in train_rows.path])
y_train = train_rows.label.to_numpy()
y_test = test_rows.label.to_numpy()
model = SVC(kernel="linear", C=1.0, random_state=42)
model.fit(X_train, y_train)
print("학습:", len(X_train), "평가:", len(y_test))
```

## 4단계 — 이미지 조건별 정확도 그래프

정확도가 반드시 떨어진다는 가정 없이 실제 숫자를 기록하세요.

```python
# 원본 테스트 이미지만 변형합니다. 학습/평가 데이터는 섞이지 않습니다.
results = []
all_preds = {}
for condition in conditions:
    X_eval = np.stack([
        feature(transform(Image.open(WORK / p), condition, seed=1000 + i))
        for i, p in enumerate(test_rows.path)
    ])
    predictions = model.predict(X_eval)
    all_preds[condition] = predictions
    n_correct = int((predictions == y_test).sum())
    results.append({"조건": condition, "평가장수": len(y_test),
                    "정답수": n_correct, "정확도": n_correct / len(y_test)})
result_df = pd.DataFrame(results)
display(result_df)
plt.figure(figsize=(8, 4))
plt.bar(result_df["조건"], result_df["정확도"] * 100)
plt.ylim(0, 100)
plt.ylabel("Accuracy (%)")
plt.xticks(rotation=15)
plt.title("Impact of image transformations")
plt.tight_layout()
plt.show()
```

## 5단계 — 오분류 이미지 직접 관찰

오분류가 없다면 다른 변형 강도를 바꾸는 심화 실습을 할 수 있습니다.

```python
# 가장 낮은 성능 조건에서 잘못 분류된 이미지를 확인합니다.
worst_condition = result_df.sort_values("정확도").iloc[0]["조건"]
wrong = np.flatnonzero(all_preds[worst_condition] != y_test)
print("검토 조건:", worst_condition, "오분류 이미지 수:", len(wrong))
if len(wrong):
    fig, axes = plt.subplots(1, min(len(wrong), 5),
                             figsize=(3 * min(len(wrong), 5), 3), squeeze=False)
    for ax, i in zip(axes.flat, wrong[:5]):
        ax.imshow(transform(Image.open(WORK / test_rows.iloc[i].path),
                            worst_condition, seed=1000 + i))
        ax.set_title(f"실제:{y_test[i]}\n예측:{all_preds[worst_condition][i]}")
        ax.axis("off")
    plt.tight_layout()
    plt.show()
else:
    print("선택 조건에서 오분류가 없습니다. 더 큰 회전각·노이즈를 실험해 보세요.")
```

## 6단계 — 데이터 증강으로 개선 시도

원본 45장과 이들의 변형본만 학습에 추가하고 같은 test 15장으로 평가합니다.

```python
# (확장) 훈련 이미지에 변형 사례를 추가한 후, 동일한 테스트 조건에서 비교합니다.
# 평가용 파일은 학습에 사용하지 않습니다.
aug_conditions = ["original", "rotate_35", "dark_40", "noise_45"]
X_aug, y_aug = [], []
for i, row in train_rows.iterrows():
    original = Image.open(WORK / row.path)
    for condition in aug_conditions:
        X_aug.append(feature(transform(original, condition, seed=i + 2000)))
        y_aug.append(row.label)
aug_model = SVC(kernel="linear", C=1.0, random_state=42)
aug_model.fit(np.stack(X_aug), np.array(y_aug))
aug_results = []
for condition in conditions:
    X_eval = np.stack([
        feature(transform(Image.open(WORK / p), condition, seed=1000 + i))
        for i, p in enumerate(test_rows.path)
    ])
    pred_aug = aug_model.predict(X_eval)
    aug_results.append({"조건": condition,
                        "증강후_정확도": accuracy_score(y_test, pred_aug)})
compare = result_df.merge(pd.DataFrame(aug_results), on="조건")
compare = compare.rename(columns={"정확도": "기본_정확도"})
display(compare[["조건", "기본_정확도", "증강후_정확도"]])
compare.plot(x="조건", y=["기본_정확도", "증강후_정확도"], kind="bar",
             figsize=(9, 4), ylim=(0, 1), rot=15)
plt.ylabel("Accuracy")
plt.tight_layout()
plt.show()
```

## 7단계 — 결과 CSV 저장

결과 CSV와 그래프 화면 캡처를 제출하세요.

```python
# 실습 결과 CSV 파일 다운로드
compare.to_csv("Week09_Workbook2_Results.csv", index=False, encoding="utf-8-sig")
print("저장 파일: Week09_Workbook2_Results.csv")
try:
    from google.colab import files
    files.download("Week09_Workbook2_Results.csv")
except ImportError:
    print("로컬에서는 현재 실행 폴더에서 CSV를 찾으세요.")
```

## 결과 보고 표

| 조건 | 기본 모델 정답수 / 15 | 기본 정확도 | 증강 후 정확도 | 해석 |
| --- | --- | --- | --- | --- |
| 원본 | | | | |
| 35도 회전 | | | | |
| 밝기 40% | | | | |
| 노이즈 표준편차 45 | | | | |

## 해석 질문
1. 이미지 변형 중 가장 큰 성능 변화를 보인 조건은 무엇이었나요? 실제 수치를 제시하세요.
2. 밝기를 40%로 줄인 이미지가 무조건 더 어렵다고 할 수 있나요? 실행 결과로 판단하세요.
3. 데이터 증강 후 모든 조건에서 성능이 반드시 향상되나요? 결과를 바탕으로 설명하세요.
4. 훈련 데이터만 변형해야 하는 이유는 무엇인가요? (평가 데이터 유출 방지)
5. 실제 사진에서는 이 실습보다 고려해야 할 변형이 무엇인지 2가지 제시하세요.

**제출:** 변형 이미지 4장 비교 캡처, 정확도 막대그래프, 오분류 검토 결과(없다면 '0장'), 증강 전·후 비교 그래프, 결과 CSV, 질문 답변 5개.

**참고:** HOG + SVM은 사전학습 심층신경망이 아닙니다. 합성 도형 결과만으로 실물 인식 성능을 주장할 수 없습니다.