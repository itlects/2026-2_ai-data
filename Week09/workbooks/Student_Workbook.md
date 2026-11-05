# 9주차 학생 워크북 | 이미지 데이터의 시각화와 소량 이미지 분류

**학습 목표:** (1) 이미지 배열·RGB 채널·히스토그램 이해 (2) 3개 도형 이미지를 SVM으로 분류 (3) 같은 학습/평가 이미지로 Teachable Machine과 비교.

**데이터:** 64×64 PNG **60장** (circle / square / triangle 각 20장). 클래스마다 **훈련 15장 + 평가 5장**, 총 훈련 45장·평가 15장. 예제용으로 직접 만든 합성 이미지입니다. 실제 사물 인식 성능을 대표하지 않습니다.

**실습 순서:** `런타임 > 모두 실행` 또는 셀을 위에서 아래로 실행하세요. 실행 환경은 Google Colab(Python 3)이며, 업로드나 인증 없이 GitHub 공개 데이터 ZIP을 다운로드합니다.

**원본 이미지 ZIP:** [shapes60.zip](https://github.com/itlects/2026-2_ai-data/raw/refs/heads/main/Week09/data/shapes60.zip)


## 먼저 배우는 기술 발전 배경 — 왜 HOG + SVM을 실습할까요?

**핵심 질문:** 컴퓨터는 원·사각형·삼각형을 어떻게 구분할까요? 사람은 윤곽선을 바로 볼 수 있지만, 컴퓨터가 읽는 이미지는 픽셀값의 배열입니다. 이미지 분류 기술의 큰 흐름을 이해하면 HOG와 SVM을 따로 배우는 이유가 명확해집니다.

### 이미지 인식 기술의 발전 흐름

1. **전통적 영상처리(딥러닝 이전부터 사용)**: 색상 평균, 모서리, 윤곽선 등 사람이 유용하다고 판단한 수치를 직접 설계했습니다. 조명·각도 변화에 취약할 수 있습니다.
2. **특징 추출 + 기계학습 분류(HOG + SVM)**: HOG가 밝기 변화의 방향과 분포를 숫자 벡터로 바꿉니다. SVM은 그 벡터를 입력받아 도형을 구별하는 경계를 데이터에서 학습합니다. HOG는 Dalal·Triggs의 2005년 보행자 검출 연구로 널리 알려졌고, SVM은 1990년대에 확립된 기계학습 기법입니다. 둘이 동시에 발명된 단일 기술은 아닙니다.
3. **딥러닝 CNN(2010년대 급속 발전)**: 이미지를 입력하면 신경망이 특징 추출과 분류에 사용할 표현을 함께 학습합니다. 사람이 HOG 같은 특징 계산 규칙을 미리 설계할 필요가 줄어듭니다.
4. **사전학습 모델과 전이학습**: 많은 이미지로 이미 학습한 모델의 표현을 활용해 소규모 사용자 데이터에 맞게 분류할 수 있습니다. **Teachable Machine**은 이 접근을 코드 없이 체험하는 도구입니다. 정확한 학습 내부 구조는 모델 선택과 서비스 구현에 따라 다릅니다.

### 왜 두 방식을 비교하나요?

| 비교 항목 | HOG + SVM (코드 실습) | Teachable Machine (노코드 실습) |
| --- | --- | --- |
| 특징 추출 | HOG 규칙을 사람이 지정 | 이미지 모델이 학습한 표현 활용 |
| 분류 모델 | SVM을 Python으로 학습 | 웹 인터페이스에서 훈련 |
| 학생이 관찰할 점 | 픽셀→특징 벡터→분류의 중간 단계 | 데이터 업로드→학습→예측의 전체 흐름 |
| 한계 | 회전·조명·실제 사진에 취약할 수 있음 | 데이터 규모와 편향, 실행 환경의 영향을 받음 |

**주의:** 어느 모델이 언제나 더 정확하다고 가정하지 않습니다. 두 모델에 *같은 train 이미지 45장*을 제공하고 *같은 test 이미지 15장*으로 평가해야 비교의 출발점이 공정합니다. 테스트 이미지는 어느 쪽의 훈련에도 사용하지 않습니다.

### 한 장의 이미지가 분류될 때

`64×64 RGB 이미지(픽셀)` → `회색조 이미지` → `HOG 특징 벡터` → `학습된 SVM` → `circle / square / triangle 예측`

**알고리즘을 Python 문법과 연결하기:** `def features(...)`는 특징 계산 절차를 함수로 묶고, `for` 반복문 또는 리스트 컴프리헨션은 모든 이미지에 그 절차를 반복합니다. `model.fit(X_train, y_train)`은 분류 경계 학습이고 `model.predict(X_test)`는 처음 보는 평가 이미지의 예측입니다.

**읽어보기:** Dalal & Triggs, *Histograms of Oriented Gradients for Human Detection* (CVPR 2005), https://lear.inrialpes.fr/people/triggs/pubs/Dalal-cvpr05.pdf

### 코드 셀 해설 — 1. 데이터 다운로드·압축 해제

**Python 문법:** `from pathlib import Path`는 모듈에서 필요한 기능을 가져오는 문법입니다. `변수 = 값`은 대입, `.mkdir(...)`는 폴더 생성, `with ... as ...:`와 들여쓰기는 파일 처리 구역을 뜻합니다. `requests.get()`은 데이터를 요청하고 `assert 조건`은 파일 개수를 검사합니다.

**알고리즘 흐름:** 주소 지정 → ZIP 다운로드 → 압축 해제 → 파일 개수 확인.

**실행 후 확인:** PNG 60장이 준비되어야 합니다.

**스스로 확인:** `assert`를 빼면 데이터가 누락되어도 어떤 문제가 생길 수 있나요?

```python
# 1. 실습 데이터 다운로드 · 압축 해제 (셀 순서대로 실행)
from pathlib import Path
import requests, zipfile, io
DATA_URL = "https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/Week09/data/shapes60.zip"
DATA_DIR = Path("/content/week09_shapes")
DATA_DIR.mkdir(parents=True, exist_ok=True)
response = requests.get(DATA_URL, timeout=60)
response.raise_for_status()
with zipfile.ZipFile(io.BytesIO(response.content)) as z:
    z.extractall(DATA_DIR)
print("데이터 저장 위치:", DATA_DIR)
print("이미지 수:", len(list(DATA_DIR.rglob("*.png"))))
assert len(list(DATA_DIR.rglob("*.png"))) == 60, "60장 이미지 다운로드 확인"
```

### 코드 셀 해설 — 2. 메타데이터 확인

**Python 문법:** `import pandas as pd`는 별명을 붙여 가져오는 문법입니다. `pd.read_csv(...)`로 CSV를 표로 읽습니다. `meta.groupby(["split","label"]).size()`의 `[...]`는 열 이름 문자열을 담은 리스트이며 `.`은 객체의 메서드에 접근하는 기호입니다.

**알고리즘 흐름:** 정답표 로딩 → train/test 및 클래스별 수량 집계.

**실행 후 확인:** 클래스마다 train 15장, test 5장입니다.

**스스로 확인:** `split`과 `label` 열은 어떤 정보를 담나요?

```python
# 2. 데이터 구조 확인
import pandas as pd
meta = pd.read_csv(DATA_DIR / "labels.csv")
display(meta.groupby(["split", "label"]).size().unstack(fill_value=0))
assert len(meta) == 60
```

### 코드 셀 해설 — 3. 이미지 미리보기

**Python 문법:** `for 항목 in 목록:`은 반복문이고 `enumerate(...)`는 (인덱스, 값)을 제공합니다. `axes[i,j]`는 2차원 배열에 접근하는 인덱스 문법입니다. Python 배열의 첫 인덱스는 **0**입니다. `subset`은 조건으로 선택한 DataFrame입니다.

**알고리즘 흐름:** 클래스별 이미지 4장 선택 → 각 칸에 출력.

**실행 후 확인:** 도형 3종×4장 = 12장의 미리보기입니다.

**스스로 확인:** 중첩 `for` 문에서 안쪽 반복문은 총 몇 번 수행되나요?

```python
# 3. 이미지 미리보기: 클래스별 4장
import matplotlib.pyplot as plt
from PIL import Image
fig, ax = plt.subplots(3, 4, figsize=(9, 7))
for row, label in enumerate(["circle", "square", "triangle"]):
    samples = meta[(meta.label == label) & (meta.split == "train")].head(4)
    for col, rel_path in enumerate(samples.path):
        ax[row, col].imshow(Image.open(DATA_DIR / rel_path))
        ax[row, col].set_title(label)
        ax[row, col].axis("off")
plt.tight_layout()
plt.show()
```

### 코드 셀 해설 — 4. RGB 픽셀과 히스토그램

**Python 문법:** `np.array(...)`는 이미지를 수치 배열로 변환합니다. `pixels.shape`는 배열 크기, `pixels[32,32]`는 특정 픽셀, `pixels[:,:,0]`은 모든 행과 열에서 빨강 채널만 꺼내는 **슬라이싱**입니다. `.ravel()`은 배열을 일렬로 펼칩니다.

**알고리즘 흐름:** 이미지 → (64,64,3) 배열 → RGB 채널 분리 → 픽셀 값 분포 집계.

**실행 후 확인:** 원본, 빨강 채널, RGB 히스토그램이 표시됩니다.

**스스로 확인:** `pixels[:,:,2]`는 어떤 색상 채널인가요?

```python
# 4. RGB 픽셀과 색상 채널, 히스토그램 시각화
import numpy as np
sample_path = DATA_DIR / meta.iloc[0]["path"]
pixels = np.array(Image.open(sample_path).convert("RGB"))
print("크기 (세로, 가로, 채널):", pixels.shape)
print("중앙 픽셀 RGB:", pixels[32, 32].tolist())
fig, axes = plt.subplots(1, 3, figsize=(12, 3))
axes[0].imshow(pixels); axes[0].set_title("원본 이미지"); axes[0].axis("off")
axes[1].imshow(pixels[:, :, 0], cmap="Reds", vmin=0, vmax=255)
axes[1].set_title("R 채널"); axes[1].axis("off")
for k, color in enumerate(["red", "green", "blue"]):
    axes[2].hist(pixels[:, :, k].ravel(), bins=20, range=(0, 255), alpha=.45, color=color, label=color)
axes[2].set_title("RGB 히스토그램"); axes[2].legend()
plt.tight_layout(); plt.show()
```

### 코드 셀 해설 — 5. HOG 특징과 훈련·평가 분리

**Python 문법:** `def features(path):`는 함수 정의, `return`은 결과 반환입니다. `[features(p) for p in meta.path]`는 **리스트 컴프리헨션**으로, 파일마다 특징을 계산합니다. `np.stack(...)`은 특징 벡터를 행으로 쌓습니다. `train = (meta.split=="train").to_numpy()`는 **불리언 마스크**이며 `X[train]`은 참인 행만 선택합니다.

**알고리즘 흐름:** 회색조 전환 → 국소적인 윤곽선 방향 분포(HOG) → 숫자 벡터 → 훈련 45장/평가 15장 분리.

**실행 후 확인:** HOG 벡터가 모델의 입력 X가 되고, 실제 클래스가 정답 y가 됩니다.

**스스로 확인:** HOG 자체가 분류 모델이 아닌 이유는 무엇인가요?

```python
# 5. 이미지 특징(HOG) 추출 및 학습/평가 데이터 구성
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay

def image_to_feature(rel_path):
    gray = np.array(Image.open(DATA_DIR / rel_path).convert("L"))
    return hog(gray, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)

X = np.stack([image_to_feature(p) for p in meta.path])
y = meta.label.to_numpy()
train_mask = (meta.split == "train").to_numpy()
X_train, X_test = X[train_mask], X[~train_mask]
y_train, y_test = y[train_mask], y[~train_mask]
print("훈련 데이터:", X_train.shape, "평가 데이터:", X_test.shape)
assert X_train.shape[0] == 45 and X_test.shape[0] == 15
```

### 코드 셀 해설 — 6. SVM 학습과 성능 평가

**Python 문법:** `model = SVC(...)`는 객체 생성입니다. `.fit(X_train,y_train)`은 모델 학습, `.predict(X_test)`는 예측, `accuracy_score(y_test,pred)`는 평가입니다. `round(...,3)`은 소수 셋째 자리까지 반올림합니다. `classification_report`는 클래스별 정밀도·재현율·F1을 계산합니다.

**알고리즘 흐름:** HOG 벡터 → SVM 분류 경계 학습 → 평가 이미지 예측 → 혼동행렬·지표 확인.

**실행 후 확인:** 정확도와 혼동행렬을 확인합니다. 실제 수치는 실행 결과를 기록하세요.

**스스로 확인:** 혼동행렬의 대각선과 대각선 밖의 값은 각각 무엇인가요?

```python
# 6. 소량 이미지 분류 및 성능 평가
model = SVC(kernel="linear", C=1.0, probability=True, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)
accuracy = accuracy_score(y_test, pred)
print(f"평가 정확도: {accuracy:.3f} ({int((pred == y_test).sum())}/15)")
print(classification_report(y_test, pred, zero_division=0))
ConfusionMatrixDisplay.from_predictions(y_test, pred, labels=["circle", "square", "triangle"], cmap="Blues")
plt.title("Colab 분류 결과 - 혼동행렬")
plt.show()
```

### 코드 셀 해설 — 7. 잘못 분류된 이미지 확인

**Python 문법:** `pred != y_test`는 예측값과 정답의 원소별 비교, `np.flatnonzero(...)`는 참인 위치를 반환합니다. `if ...:`·`else:`는 조건 분기이고 `wrong[:5]`는 슬라이싱입니다.

**알고리즘 흐름:** 예측과 정답 비교 → 오분류 위치 추출 → 이미지·정답·예측 보기.

**실행 후 확인:** 오분류 이미지가 있으면 출력하고 없으면 0장으로 기록합니다.

**스스로 확인:** 정확도가 높더라도 오분류를 살펴봐야 하는 이유는 무엇인가요?

```python
# 7. 오분류 이미지 확인 (없으면 안내문 출력)
test_meta = meta[meta.split == "test"].reset_index(drop=True)
wrong = np.flatnonzero(pred != y_test)
if len(wrong) == 0:
    print("오분류 0장: 현재 평가 데이터 15장을 모두 맞혔습니다.")
else:
    fig, axes = plt.subplots(1, len(wrong), figsize=(3 * len(wrong), 3), squeeze=False)
    for ax, j in zip(axes.flat, wrong):
        ax.imshow(Image.open(DATA_DIR / test_meta.iloc[j]["path"]))
        ax.set_title(f"정답:{y_test[j]} / 예측:{pred[j]}")
        ax.axis("off")
    plt.tight_layout(); plt.show()
```

### 코드 셀 해설 — 8. 비교 결과 CSV 만들기

**Python 문법:** `df[["path","label"]]`는 여러 열을 선택합니다. `.copy()`는 별도 표를 만들며 `df["tm_prediction"]=""`는 새 열을 추가합니다. `.to_csv(...,index=False,encoding="utf-8-sig")`는 행 번호를 빼고 한글 호환 인코딩으로 저장합니다.

**알고리즘 흐름:** 15장 테스트 결과표 생성 → Colab 예측 기입 → Teachable Machine용 빈 열 추가 → CSV 저장.

**실행 후 확인:** 동일한 15장으로 두 모델의 예측을 비교할 표가 생성됩니다.

**스스로 확인:** 평가 이미지가 서로 다르면 정확도를 직접 비교하기 어려운 이유는 무엇인가요?

```python
# 8. Teachable Machine과 비교하기 위한 평가표 저장
# TM에서 동일한 test/ 폴더 15장에 대한 예측 결과를 직접 조사해 tm_prediction을 입력하세요.
compare = test_meta[["path", "label"]].copy()
compare["colab_prediction"] = pred
compare["tm_prediction"] = ""  # 직접 입력한 뒤 다시 실행
compare.to_csv("week09_comparison_template.csv", index=False, encoding="utf-8-sig")
display(compare.head(15))
print("파일 생성: week09_comparison_template.csv")
```

## 실습 B | Teachable Machine 이미지 분류 비교 (노코드)

1. https://teachablemachine.withgoogle.com/ 접속 → **Get Started → Image Project → Standard image model**.
2. 클래스 이름을 `circle`, `square`, `triangle`로 설정합니다.
3. 위 셀에서 만든 `/content/week09_shapes/train/`의 클래스별 **PNG 15장**을 각각 업로드합니다. Colab 왼쪽 파일 패널에서 폴더를 내려받는 대신, [이미지 ZIP](https://github.com/itlects/2026-2_ai-data/raw/refs/heads/main/Week09/data/shapes60.zip)을 PC에 다운로드해서 압축을 풀면 편리합니다.
4. **Train Model** 클릭. 브라우저/네트워크/학습 환경에 따라 학습 시간과 결과가 달라질 수 있습니다.
5. **Preview**에서 `test/circle`, `test/square`, `test/triangle`의 총 **15장**을 이미지 파일로 하나씩 입력합니다. 각 이미지의 가장 높은 확률 클래스를 예측으로 기록합니다. **절대로 평가용 test 이미지를 학습에 넣지 마세요.**
6. `week09_comparison_template.csv`의 `tm_prediction` 열에 예상 클래스 영문명을 기록하고 두 모델의 정답 개수를 비교합니다.

**비교 유의사항:** Colab은 HOG+선형 SVM, Teachable Machine은 브라우저 전이학습 기반 이미지 분류 도구입니다. 데이터는 동일하게 고정하지만 알고리즘/전처리가 달라 결과는 다를 수 있습니다. `confidence`는 정답 확률을 보장하지 않습니다.

### 결과기록

| 항목 | Colab(HOG+SVM) | Teachable Machine |
|---|---|---|
| 학습 이미지 | 45장 | 45장 |
| 평가 이미지 | 15장 | 15장 |
| 정답 수 | 코드 실행 결과를 기입 | 직접 확인한 정답 수 기입 |
| 정확도 | 정답 수/15 | 정답 수/15 |
| 가장 어려웠던 도형 | 오분류 이미지 참고 | 직접 조사 |

### 제출 체크

- [ ] 클래스별 원본 이미지 4장 미리보기 캡처
- [ ] RGB 채널/히스토그램 결과 캡처 및 픽셀 값 설명
- [ ] Colab 혼동행렬과 정확도 캡처
- [ ] Teachable Machine 훈련 화면/예측 화면 캡처
- [ ] 동일한 평가 이미지 15장의 비교표 작성
- [ ] 두 방법의 차이와 오분류 원인 3~5문장 정리

### 생각해 보기

1. 64×64 RGB 이미지 한 장은 숫자 몇 개로 표현될까요?
2. 정확도가 높아도 새로운 실제 사진을 잘 구분한다는 보장이 없는 이유는 무엇인가요?
3. 일부 이미지를 훈련 데이터에 중복 넣으면 평가가 공정할까요?
4. 색깔만으로 구분하지 않도록 3종류 도형의 색을 섞어 만든 이유는 무엇인가요?
