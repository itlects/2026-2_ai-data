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

**학습 목적:** 데이터셋을 내려받고 학습용 45장·평가용 15장으로 구분되었는지 확인합니다.

**주요 코드 설명**
- `Path`, `WORK.mkdir(...)`: 실습 데이터를 저장할 폴더를 생성합니다.
- `requests.get(...)`, `raise_for_status()`: ZIP 파일을 요청하고 다운로드 오류를 확인합니다.
- `zipfile.ZipFile(...)`: ZIP 압축을 해제합니다.
- `pd.read_csv(...)`: `labels.csv`를 표(`DataFrame`)로 읽습니다. `meta`에는 파일 경로(`path`), 정답 클래스(`label`), 분할(`split`)이 있습니다.
- `groupby(["split", "label"]).size()`: 분할 및 클래스별 이미지 개수를 셉니다.
- `assert`: 이미지 개수가 조건과 다르면 실습을 중단해 데이터 오류를 빨리 발견합니다.

**실행 결과:** 클래스별 훈련 15장, 평가 5장(합계 훈련 45장·평가 15장)이 출력되어야 합니다.

**확인 질문:** 왜 학습에 사용한 이미지를 평가에 다시 사용하면 공정한 정확도를 측정하기 어렵나요?

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

**학습 목적:** 같은 이미지가 회전·밝기·노이즈에 따라 어떻게 달라지는지 눈으로 비교합니다.

**주요 코드 설명**
- `transform(img, condition, seed)`: 조건에 따라 이미지를 변환하는 사용자 정의 함수입니다.
- `convert("RGB")`: 입력 이미지의 색상 표현을 RGB로 통일합니다.
- `rotate(35, ...)`: 이미지를 35도 회전합니다. 빈 공간은 지정된 배경색으로 채웁니다.
- `ImageEnhance.Brightness(...).enhance(0.4)`: 밝기를 원래의 40% 수준으로 낮춥니다.
- `np.random.default_rng(seed)`와 `rng.normal(0, 45, ...)`: 재현 가능한 가우시안 노이즈를 만듭니다. 45는 노이즈의 표준편차입니다.
- `np.clip(..., 0, 255)`: 픽셀값이 허용 범위(0~255)를 벗어나지 않도록 제한합니다.
- `plt.subplots(1, 4)`: 원본·회전·어둡게·노이즈 이미지를 같은 화면에 나란히 표시합니다.

**실행 결과:** 도형 하나가 네 가지 형태로 표시됩니다. `seed`를 유지하면 같은 노이즈 패턴을 다시 만들 수 있습니다.

**확인 질문:** 회전은 도형의 경계선 방향에, 어둡게 만드는 변형은 픽셀의 밝기값에 각각 어떤 영향을 주나요?

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

**학습 목적:** 기본 모델을 원본 훈련 이미지 45장으로 학습하고, 평가에 사용할 정답을 분리합니다.

**주요 코드 설명**
- `feature(img)`: RGB 이미지를 회색조로 변환한 후 HOG 특징 벡터로 바꿉니다.
- `hog(... orientations=9, pixels_per_cell=(8,8), cells_per_block=(2,2))`: 이미지의 국소적인 밝기 변화 방향을 수치로 표현합니다. 이 값은 훈련 이미지가 아니라 이미지에서 뽑아낸 **특징**입니다.
- `train_rows`, `test_rows`: `split` 열을 기준으로 학습과 평가용 데이터를 분리합니다.
- `np.stack(...)`: 여러 이미지의 특징 벡터를 모델이 처리할 배열로 합칩니다.
- `y_train`, `y_test`: 정답 클래스 이름을 담습니다.
- `SVC(kernel="linear")`: 선형 SVM 분류기를 준비합니다.
- `model.fit(X_train, y_train)`: 훈련 특징과 정답을 사용하여 모델을 학습합니다.

**실행 결과:** `학습: 45 평가: 15`가 출력됩니다. 여기서는 평가 데이터로 모델을 학습하지 않습니다.

**확인 질문:** HOG와 SVM은 같은 역할인가요? 특징 추출과 분류 모델의 역할을 구분해 보세요.

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

**학습 목적:** 기본 모델이 각 변형 조건에서 얼마나 정확하게 분류하는지 수치와 그래프로 확인합니다.

**주요 코드 설명**
- `for condition in conditions`: 원본·35도 회전·밝기 40%·노이즈 조건을 차례로 평가합니다.
- `X_eval`: **평가용** 이미지 15장을 현재 조건으로 바꾼 뒤 HOG 특징으로 변환합니다.
- `model.predict(X_eval)`: 각 이미지의 예측 클래스 이름을 얻습니다.
- `all_preds[condition]`: 뒤의 오분류 분석을 위해 조건별 예측값을 저장합니다.
- `(predictions == y_test).sum()`: 정답과 예측이 일치하는 이미지 개수입니다.
- `n_correct / len(y_test)`: 분류 정확도(0~1)입니다.
- `pd.DataFrame(results)`, `plt.bar(...)`: 정확도 표와 막대그래프를 출력합니다. 그래프는 `×100`으로 백분율을 표시합니다.

**실행 결과:** 4개 조건의 정답 수·정확도가 표와 그래프로 나타납니다. 성능 변화의 방향과 크기를 직접 확인합니다.

**확인 질문:** 회전과 노이즈 중 어떤 변형에서 정확도가 가장 낮았나요? 정확도 차이를 퍼센트포인트(%p)로 계산해 보세요.

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

**학습 목적:** 숫자로만 보던 오류를 실제 이미지와 정답·예측 클래스로 확인합니다.

**주요 코드 설명**
- `sort_values("정확도").iloc[0]`: 정확도가 가장 낮은 변형 조건을 선택합니다.
- `np.flatnonzero(all_preds[...] != y_test)`: 틀린 예측이 발생한 평가 이미지의 위치를 찾아냅니다.
- `len(wrong)`: 오분류 이미지 수입니다.
- `wrong[:5]`: 화면에 최대 다섯 장만 출력합니다. 오류가 더 많아도 다섯 장만 보여 줍니다.
- `test_rows.iloc[i].path`: 오류 이미지의 원래 파일 경로를 찾습니다.
- `ax.set_title(...)`: 실제 정답과 모델 예측을 함께 표기합니다.
- `if len(wrong)`: 오분류가 없을 때 빈 그래프를 만들지 않도록 분기합니다.

**실행 결과:** 오분류가 있으면 해당 변형 이미지와 정답·예측이 출력됩니다. 없으면 오분류가 0장이라는 메시지가 나타납니다.

**확인 질문:** 잘못 분류된 이미지는 모양, 회전, 밝기, 잡음 중 어떤 특징 때문에 어려워 보이나요?

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

**학습 목적:** 훈련 이미지에만 다양한 변형을 추가하는 **데이터 증강**이 성능에 미치는 영향을 비교합니다.

**주요 코드 설명**
- `aug_conditions`: 훈련 이미지에 추가할 원본·회전·밝기·노이즈 조건을 정의합니다.
- `for i, row in train_rows.iterrows()`: 원본 훈련 이미지 45장을 하나씩 가져옵니다.
- `X_aug.append(...)`, `y_aug.append(...)`: 각 원본의 네 가지 변형 특징과 같은 정답 레이블을 저장합니다. 총 45×4=180개의 훈련 예제를 만듭니다.
- `aug_model.fit(...)`: 확장된 훈련 데이터로 **새** SVM을 학습합니다.
- `test_rows`와 동일한 `seed=1000+i`: 기본 모델을 평가할 때와 동일한 평가 이미지·노이즈 조건을 사용합니다.
- `accuracy_score(y_test, pred_aug)`: 데이터 증강 모델의 조건별 정확도를 계산합니다.
- `merge(...)`, `rename(...)`: 기본 모델과 증강 모델의 결과를 조건별로 합칩니다.
- `compare.plot(...)`: 두 모델의 정확도를 나란히 비교합니다.

**실행 결과:** 조건별 기본 정확도와 증강 후 정확도, 비교 막대그래프가 출력됩니다.

**중요:** 테스트 이미지는 **훈련에 추가하지 않습니다**. 데이터 증강이 성능을 늘릴 수도 있지만 반드시 모든 조건에서 개선되는 것은 아닙니다.

**확인 질문:** 원본 45장이 180개 학습 예제로 늘어난 계산 과정을 설명하고, 이 180장이 서로 독립적인 실제 사진 180장과 왜 다른지 생각해 보세요.

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

**학습 목적:** 모델 비교 결과를 제출용 CSV로 저장합니다.

**주요 코드 설명**
- `compare.to_csv(...)`: 조건별 결과표를 CSV 파일로 저장합니다.
- `index=False`: pandas의 행 번호를 불필요하게 파일에 저장하지 않습니다.
- `encoding="utf-8-sig"`: 일부 Windows 스프레드시트 프로그램에서 한글 열 이름이 깨지는 현상을 줄입니다.
- `google.colab.files.download(...)`: Colab에서 파일 다운로드를 실행합니다.
- `except ImportError`: Colab이 아닌 로컬 Python에서는 다운로드 호출 대신 저장 경로 안내만 출력합니다.

**실행 결과:** `Week09_Workbook2_Results.csv` 파일이 저장됩니다. Colab에서는 다운로드 안내가 표시됩니다.

**확인 질문:** CSV의 `기본_정확도`와 `증강후_정확도`를 비교하여 가장 큰 차이가 난 조건과 그 이유를 적으세요.

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