# 9주차 추가 워크북 3 | 실제 패션 이미지 분류 과제 (Fashion-MNIST)

**목표**: 기존 도형 분류를 실제 의류 이미지로 확장해, **HOG+SVM**과 **간단한 신경망(MLP)**의 처리 방식을 비교합니다. 각 코드를 먼저 읽고 실행한 뒤 결과를 기록하세요.

- 대상: 입문 교양 / CPU만으로 실습 가능 / 예상 45~60분(실행 환경에 따라 차이)
- 데이터: Zalando Fashion-MNIST, **28×28 흑백 이미지, 10개 의류 분류, 전체 학습 60,000장·평가 10,000장**. 수업 시간에는 그중 고정된 일부만 사용합니다.
- 출처 및 라이선스: https://github.com/zalandoresearch/fashion-mnist (MIT), https://keras.io/api/datasets/fashion_mnist/
- 준비: Colab에서 **런타임 → 모두 실행**, 최초 실행은 데이터 다운로드를 위해 인터넷 필요. **GPU, API 키, 개인 사진 불필요**
- 데이터 누수 방지: 공식 `test` 이미지는 모델 학습에 절대로 넣지 않습니다. 평가 이미지 600장에 대해 양쪽 모델을 동일하게 비교합니다.

## AI 발전과 연계

**HOG+SVM:** 사람이 설계한 경계선 특징(HOG)을 SVM 분류기에 입력합니다.  
**MLP 신경망:** 28×28 픽셀을 784개 숫자로 펼친 뒤 신경망이 가중치를 학습합니다.  
**Teachable Machine:** 이미지 업로드와 훈련을 노코드로 처리하며 일반적으로 사전 학습된 이미지 특징을 활용합니다. 9·10단계에서 Teachable Machine 실습을 진행하며, 평가 조건이 다른 모델의 정확도는 직접 비교할 수 없음을 설명합니다.

> HOG+SVM과 MLP는 학습 방식의 차이를 보여 주기 위한 **교육용 기준선**입니다. MLP는 CNN이 아니며, 어느 모델의 성능이 반드시 더 높다고 단정하지 않습니다.


## 1단계 | 필요한 라이브러리 불러오기

**Python 문법**: `import`는 모듈 전체를, `from 모듈 import 이름`은 필요한 기능을 불러옵니다. `as`는 짧은 별명을 지정합니다. 주석(`#`)은 실행되지 않는 설명입니다.

**알고리즘 역할**: 이미지 처리(NumPy), 시각화(Matplotlib), HOG 특징, SVM 분류, MLP 분류, 성능 평가 도구를 준비합니다.

**실행 결과**: 라이브러리 버전이 출력됩니다. 오류가 발생하면 Colab의 기본 Python 런타임인지 확인하세요.

**확인 질문**: `np`, `plt`가 왜 코드에서 등장하나요?


```python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sklearn
from skimage.feature import hog
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, ConfusionMatrixDisplay, classification_report
from IPython.display import display

print("scikit-learn 버전:", sklearn.__version__)
```

## 2단계 | Fashion-MNIST 자동 다운로드와 데이터 구조 확인

**Python 문법**: `(a, b), (c, d) = ...`는 두 쌍의 반환값을 나누어 받는 *튜플 언패킹*입니다. `.shape`는 배열 크기이고, `len()`은 데이터 개수입니다. `assert`는 조건이 참인지 검사합니다.

**알고리즘 역할**: 공식 학습/시험 분할을 유지하고, 수업시간 단축을 위해 앞에서부터 학습 3,000장과 평가 600장을 사용합니다. 원본 데이터의 클래스 분포가 비교적 고르더라도 표본 추출 방식에 따라 정확도는 달라질 수 있습니다.

**실행 결과**: 전체 (60000,28,28)/(10000,28,28) 및 실습 (3000,28,28)/(600,28,28)이 출력됩니다.

**확인 질문**: 28×28 이미지 한 장에는 흑백 픽셀값이 몇 개 있나요?


```python
from tensorflow.keras.datasets import fashion_mnist

(x_train_all, y_train_all), (x_test_all, y_test_all) = fashion_mnist.load_data()
class_names = ["T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
               "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"]
print("공식 데이터:", x_train_all.shape, x_test_all.shape)
assert x_train_all.shape == (60000, 28, 28)
assert x_test_all.shape == (10000, 28, 28)

# 공식 train/test 분할을 유지하며 속도에 맞춰 일부만 선택
x_train = x_train_all[:3000]
y_train = y_train_all[:3000]
x_test = x_test_all[:600]
y_test = y_test_all[:600]
print("실습 데이터:", x_train.shape, x_test.shape)
```

## 3단계 | 의류 이미지와 정답 레이블 시각화

**Python 문법**: `for i in range(12)`는 i에 0~11을 차례로 대입합니다. `enumerate(...)`는 순서 번호와 값을 함께 반환합니다. `class_names[y_train[i]]`는 정수 레이블을 클래스 이름으로 변환하는 리스트 인덱싱입니다.

**알고리즘 역할**: 모델 학습 전에 사람이 원본 이미지와 레이블을 확인하는 탐색적 데이터 분석(EDA)을 수행합니다.

**실행 결과**: 12개의 흑백 이미지가 3행×4열로 출력됩니다.

**확인 질문**: `Shirt`와 `T-shirt/top`은 무엇이 비슷해서 AI가 혼동할 수 있을까요?


```python
fig, axes = plt.subplots(3, 4, figsize=(9, 7))
for i, ax in enumerate(axes.flat):
    ax.imshow(x_train[i], cmap="gray")
    ax.set_title(class_names[int(y_train[i])])
    ax.axis("off")
plt.tight_layout()
plt.show()
print("첫 이미지 배열 크기:", x_train[0].shape)
print("픽셀 값 범위:", x_train.min(), "~", x_train.max())
```

## 4단계 | 밝기 분포와 데이터 정규화

**Python 문법**: `x_train.astype("float32") / 255.0`은 정수 픽셀(0~255)을 실수(0~1)로 바꾸는 배열 연산입니다. `.reshape(3000, -1)`은 각 이미지를 1차원으로 펼치며 `-1`은 남은 크기를 자동 계산합니다.

**알고리즘 역할**: MLP는 픽셀 784개를 입력받습니다. 반면 HOG는 형태의 경계선 방향을 입력으로 쓰므로 같은 데이터를 서로 다르게 표현합니다.

**실행 결과**: MLP 학습 입력 (3000,784)과 평가 입력 (600,784)이 출력됩니다.

**확인 질문**: 픽셀을 0~1로 바꾸는 정규화가 모델 학습에 유리한 이유는 무엇일까요?


```python
plt.figure(figsize=(6, 3))
plt.hist(x_train[0].ravel(), bins=20, range=(0, 255))
plt.title("Pixel intensity histogram")
plt.xlabel("Pixel value")
plt.ylabel("Count")
plt.show()

X_train_pixel = x_train.astype("float32").reshape(len(x_train), -1) / 255.0
X_test_pixel = x_test.astype("float32").reshape(len(x_test), -1) / 255.0
print("MLP 입력:", X_train_pixel.shape, X_test_pixel.shape)
```

## 5단계 | HOG 특징 추출 및 SVM 학습

**Python 문법**: `def hog_features(image):`는 함수를 정의하고 `return`은 계산 결과를 돌려줍니다. `[hog_features(img) for img in x_train]`은 **리스트 컴프리헨션**으로 모든 이미지에 함수를 적용합니다. `np.stack(...)`은 특징 벡터 여러 개를 2차원 배열로 합칩니다.

**HOG 알고리즘**: 이미지의 밝기 변화 방향을 작은 영역별로 집계합니다. `pixels_per_cell=(4,4)`는 4×4 픽셀 단위, `orientations=9`는 방향을 9개 구간으로 나누겠다는 뜻입니다.

**SVM 알고리즘**: HOG 특징을 사용해 여러 의류 클래스를 분리하는 경계(초평면)를 학습합니다. `fit(X, y)`는 학습이고 `predict(X)`는 평가입니다.

**실행 결과**: HOG 특징 행렬 크기와 SVM 정확도가 출력됩니다. 처리 시간은 실행 환경에 따라 다릅니다.

**확인 질문**: HOG가 직접 의류 이름을 예측하나요, 아니면 SVM이 예측하나요?


```python
def hog_features(image):
    return hog(image, orientations=9, pixels_per_cell=(4, 4),
               cells_per_block=(2, 2), feature_vector=True)

X_train_hog = np.stack([hog_features(img) for img in x_train])
X_test_hog = np.stack([hog_features(img) for img in x_test])
print("HOG 특징 크기:", X_train_hog.shape)

svm_model = SVC(kernel="linear", C=1.0)
svm_model.fit(X_train_hog, y_train)
svm_pred = svm_model.predict(X_test_hog)
svm_acc = accuracy_score(y_test, svm_pred)
print("HOG+SVM 평가 정확도:", round(svm_acc, 4))
```

## 6단계 | MLP 신경망으로 같은 이미지 분류

**Python 문법**: `MLPClassifier(...)`는 클래스의 인스턴스(모델)를 생성합니다. `hidden_layer_sizes=(64,)`는 은닉층 하나에 뉴런 64개를 둔다는 뜻이며, 쉼표가 있는 `(64,)`는 원소 1개의 튜플입니다.

**알고리즘 역할**: MLP는 정규화된 픽셀 784개로부터 연결 가중치를 학습합니다. 이미지 전용 합성곱(CNN) 모델은 아니며, HOG와 달리 미리 지정한 방향 히스토그램을 사용하지 않습니다.

**실행 결과**: MLP 정확도가 출력됩니다. `max_iter=30`으로 학습을 제한해 수렴 경고가 나올 수 있으며, 이는 반드시 실행 실패를 뜻하지 않습니다.

**확인 질문**: HOG+SVM과 MLP의 입력 배열 모양이 서로 다른 이유는 무엇인가요?


```python
mlp_model = MLPClassifier(hidden_layer_sizes=(64,), activation="relu",
                          solver="adam", max_iter=30, random_state=42)
mlp_model.fit(X_train_pixel, y_train)
mlp_pred = mlp_model.predict(X_test_pixel)
mlp_acc = accuracy_score(y_test, mlp_pred)
print("픽셀 기반 MLP 평가 정확도:", round(mlp_acc, 4))
```

## 7단계 | 두 모델의 정확도, 혼동행렬, 오류 이미지 비교

**Python 문법**: `pd.DataFrame({...})`은 사전(`dict`)으로 표를 만듭니다. `np.flatnonzero(조건)`은 참인 위치의 인덱스를 구합니다. `for ax, i in zip(...)`은 두 목록을 짝지어 순회합니다.

**알고리즘 역할**: 같은 600장의 정답으로 두 모델을 공정하게 평가하고, 어떤 의류가 자주 혼동되는지 혼동행렬(정답×예측)과 오류 이미지를 통해 확인합니다.

**실행 결과**: 정확도 비교표·혼동행렬 2개·오분류 이미지(최대 6개)가 출력됩니다.

**확인 질문**: 정확도가 같더라도 어떤 클래스를 틀리는지 다른 두 모델을 어떻게 비교할 수 있나요?


```python
summary = pd.DataFrame({"모델": ["HOG+SVM", "Pixel+MLP"],
                        "정확도": [svm_acc, mlp_acc],
                        "정답수": [int((svm_pred == y_test).sum()),
                                int((mlp_pred == y_test).sum())]})
display(summary)
for name, pred in [("HOG+SVM", svm_pred), ("Pixel+MLP", mlp_pred)]:
    ConfusionMatrixDisplay.from_predictions(y_test, pred, display_labels=class_names,
                                            xticks_rotation=90, cmap="Blues")
    plt.title(name)
    plt.tight_layout()
    plt.show()

wrong = np.flatnonzero(svm_pred != y_test)
fig, axes = plt.subplots(1, 6, figsize=(15, 3))
for ax in axes:
    ax.axis("off")
for ax, i in zip(axes, wrong[:6]):
    ax.imshow(x_test[i], cmap="gray")
    ax.set_title(f"True:{class_names[int(y_test[i])]}\nPred:{class_names[int(svm_pred[i])]}", fontsize=8)
    ax.axis("off")
plt.tight_layout()
plt.show()
print("SVM 오분류 개수:", len(wrong))
```

## 8단계 | 개별 예측표 CSV 저장과 다운로드

**Python 문법**: `to_csv(..., index=False)`는 표의 행 번호를 제외하고 CSV로 저장합니다. `try/except ImportError`는 Colab 전용 파일 다운로드 기능이 다른 환경에서 없을 때를 대비합니다.

**알고리즘 역할**: 각 평가 이미지의 실제 정답과 두 모델의 예측값을 저장하여 오분류 분석의 근거를 남깁니다.

**실행 결과**: `Week09_Fashion_Predictions.csv`와 `Week09_Fashion_Summary.csv`가 생성됩니다.

**확인 질문**: 어떤 열의 두 값을 비교해야 분류 오류인지 판별할 수 있나요?


```python
detail = pd.DataFrame({"image_index": np.arange(len(y_test)),
                       "actual": [class_names[int(k)] for k in y_test],
                       "HOG_SVM": [class_names[int(k)] for k in svm_pred],
                       "Pixel_MLP": [class_names[int(k)] for k in mlp_pred]})
detail.to_csv("Week09_Fashion_Predictions.csv", index=False, encoding="utf-8-sig")
summary.to_csv("Week09_Fashion_Summary.csv", index=False, encoding="utf-8-sig")
print("CSV 저장 완료: Week09_Fashion_Predictions.csv / Week09_Fashion_Summary.csv")
try:
    from google.colab import files
    files.download("Week09_Fashion_Predictions.csv")
    files.download("Week09_Fashion_Summary.csv")
except ImportError:
    print("Colab 외 환경에서는 작업 폴더에서 파일을 확인하세요.")
```

## 제출 과제 및 평가 기준

**필수 제출**: ① 데이터 이미지 12장 화면 ② 픽셀 히스토그램 ③ 두 모델의 정확도 비교표 ④ 혼동행렬 2개 ⑤ 오분류 사례 2개 이상 분석 ⑥ CSV 파일 2개 ⑦ 서술형 질문 답변.

| 질문 | 학생 작성 내용 |
| --- | --- |
| Q1 | 28×28 흑백 이미지와 64×64 RGB 이미지의 숫자 구성 차이는? |
| Q2 | HOG 특징 추출과 SVM 학습의 역할은 각각 무엇인가? |
| Q3 | MLP가 입력받는 784개의 값은 무엇이며 정규화는 왜 필요한가? |
| Q4 | HOG+SVM과 MLP의 정확도·정답수를 실제 수치로 비교하라. |
| Q5 | 가장 혼동되는 의류 2개를 오류 이미지·혼동행렬로 설명하라. |
| Q6 | 데이터가 3,000장이 아니라 6,000장이라면 어떤 변화가 있을지 가설을 제시하라(실험 결과라고 단정하지 말 것). |
| Q7 | 실제 쇼핑몰 제품 사진에서 28×28 흑백 이미지와 다른 점을 2가지 설명하라. |

**권장 점수(100점)**: 환경 및 코드 실행 25점, 시각화·결과물 25점, 비교 분석 30점, 서술형 답변 20점.

**심화 선택 과제**: `max_iter=30`을 60으로 바꾸거나 훈련 데이터를 3,000→6,000장으로 늘린 뒤 학습시간·정확도를 기록하세요. 단, **평가 데이터 600장과 지표 계산 방법은 유지**해야 합니다.

**학습 윤리·재현성**: 정확도 수치를 미리 적지 말고 실제 실행값을 기록하세요. 데이터 표본, 라이브러리 버전, 랜덤 시드가 바뀌면 결과가 달라질 수 있습니다. 데이터셋은 Zalando Fashion-MNIST(MIT)를 사용하며 원본 출처를 기록합니다.


## 9단계 | Fashion-MNIST를 Teachable Machine용 PNG로 준비하기 (선택 심화)

**학습 목적:** HOG+SVM, MLP와 별도로 노코드 학습 도구를 체험합니다. Teachable Machine 웹사이트는 Fashion-MNIST 데이터를 자동으로 가져오지 않으므로, 동일한 데이터 원본에서 일부 이미지를 클래스별 PNG로 내보냅니다.

**Python 문법:** `Path`는 폴더·파일 경로를 다루며, `mkdir(..., exist_ok=True)`는 폴더가 없을 때 생성합니다. `np.flatnonzero(y_train == k)`는 클래스 번호 `k`에 해당하는 행의 위치를 찾습니다. `[:30]`은 앞의 30개를 선택합니다. `for split, images, labels, n in ...`는 여러 묶음을 반복합니다. `Image.fromarray(...).resize(...).convert('RGB').save(...)`는 NumPy 이미지를 PNG로 저장합니다.

**알고리즘 설명:** `T-shirt/top(0)`, `Trouser(1)`, `Sneaker(7)` 세 가지로 범위를 좁힙니다. 원래 28×28 흑백 이미지의 내용을 바꾸지 않고 224×224 크기의 RGB PNG로 변환합니다. 훈련용 90장(클래스당 30), 평가용 30장(클래스당 10)을 각각 폴더에 저장합니다. **평가용 이미지를 학습에 넣지 마세요.**

**실행 결과:** `Week09_Fashion_TM_Images.zip` 파일을 다운로드합니다. ZIP 안의 `train/`과 `test/` 폴더를 확인하세요.

**확인 질문:** 28×28 픽셀을 224×224로 확대해도 원본에 없던 새로운 시각 정보가 생기지는 않는 이유가 무엇인가요?

```python
from pathlib import Path
from PIL import Image
import zipfile

EXPORT_DIR = Path('/content/week09_fashion_tm')
classes_for_tm = {0: 'Tshirt', 1: 'Trouser', 7: 'Sneaker'}
for split, images, labels, num_per_class in [
    ('train', x_train, y_train, 30),
    ('test', x_test, y_test, 10),
]:
    for label_id, name in classes_for_tm.items():
        outdir = EXPORT_DIR / split / name
        outdir.mkdir(parents=True, exist_ok=True)
        indices = np.flatnonzero(labels == label_id)[:num_per_class]
        assert len(indices) == num_per_class, (split, name, len(indices))
        for j, idx in enumerate(indices):
            image = Image.fromarray(images[idx])
            image = image.resize((224, 224), resample=Image.Resampling.NEAREST)
            image.convert('RGB').save(outdir / f'{name}_{j:03d}.png')

ZIP_PATH = Path('Week09_Fashion_TM_Images.zip')
with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for file in sorted(EXPORT_DIR.rglob('*.png')):
        z.write(file, file.relative_to(EXPORT_DIR))
with zipfile.ZipFile(ZIP_PATH) as z:
    assert len(z.namelist()) == 120
print('훈련용 90장 + 평가용 30장 ZIP 저장:', ZIP_PATH)
try:
    from google.colab import files
    files.download(str(ZIP_PATH))
except ImportError:
    print('로컬 실행에서는 현재 작업 폴더에서 ZIP 파일을 찾으세요.')

```

## 10단계 | Teachable Machine으로 분류하고 실제 옷 사진도 분류해 보기

**실습 A — 동일한 Fashion-MNIST 데이터 기반 Teachable Machine 비교**

1. [Teachable Machine](https://teachablemachine.withgoogle.com/) → Get Started → Image Project → Standard image model을 선택합니다.
2. ZIP을 압축 해제한 후 `train/Tshirt`, `train/Trouser`, `train/Sneaker` 폴더의 이미지를 각각 해당 클래스에 업로드합니다. 한 클래스당 30장씩 총 90장입니다.
3. **Train Model**을 누릅니다. 사진·이미지를 학습에 사용한 뒤 모델을 평가합니다.
4. `test/` 폴더의 이미지 30장(각 10장)을 **하나씩** Preview에 넣고 예측 클래스와 신뢰도 점수를 기록합니다. 시험용 이미지는 Train Model에 넣지 마세요.
5. 정답 수 ÷ 30으로 정확도를 계산합니다. Colab의 HOG+SVM·MLP는 10개 클래스/600장 평가, Teachable Machine 실습 A는 3개 클래스/30장 평가이므로 **세 수치를 직접 공정 비교할 수는 없습니다**. 비교할 때 반드시 클래스 수와 평가 표본이 다름을 적습니다. 세 모델의 공정한 정량 비교를 하려면 동일한 3개 클래스·동일한 30장 평가로 Colab 모델도 별도로 재학습·재평가해야 합니다.

**실습 B — 학생이 스마트폰으로 촬영한 의류 분류 (선택 개인 과제, 권장)**

1. 본인이 소유하거나 촬영 허락을 받은 옷 중 `티셔츠`, `바지`, `운동화` 3개 클래스를 선택합니다. 실제 의류가 부족한 경우 팀별로 같은 카테고리의 소지품을 활용합니다.
2. 각 클래스별 **학습 사진 20장 이상**을 촬영합니다. 정면·측면·거리·조명·배경을 다양하게 하되, 사진 속 의류가 무엇인지 명확해야 합니다. 웹캠을 이용할 경우 촬영 대상에 사람 얼굴이 나오지 않게 합니다.
3. 학습 사진과 별개로 **평가 사진 5장 이상/클래스**를 촬영해 따로 보관합니다. 연속 촬영으로 거의 같은 이미지가 섞이면 평가가 지나치게 쉬워질 수 있으므로 배경·각도를 바꿉니다.
4. 새로운 Teachable Machine 이미지 프로젝트에서 세 클래스를 생성하고 **학습 사진만** 업로드합니다. Train Model을 실행합니다.
5. 평가 사진 15장 이상을 하나씩 Preview에서 분류합니다. 정답 클래스·예측 클래스·신뢰도 점수를 표에 기록합니다.
6. 정답 수/전체 평가 수로 정확도를 계산하고 오분류 2개 이상(없다면 오분류 0건이라고 명시)의 원인을 분석합니다.

**주의:** Fashion-MNIST 흑백 이미지로 학습한 모델의 성능과 스마트폰 촬영 컬러 사진 모델의 성능은 평가 조건이 다릅니다. **서로 다른 영역(도메인)의 실험**으로 정리합니다. 사람 얼굴, 개인정보, 촬영 허락 없는 타인의 소지품 사진은 사용하지 않습니다.

**과제 결과표**

| 구분 | 모델/실습 | 학습 이미지 | 평가 이미지 | 정확도(%) | 주요 오분류 원인 |
| --- | --- | ---: | ---: | ---: | --- |
| Fashion-MNIST | HOG+SVM(10클래스) | 3,000 | 600 | 학생 작성 | |
| Fashion-MNIST | MLP(10클래스) | 3,000 | 600 | 학생 작성 | |
| Fashion-MNIST | Teachable Machine(3클래스) | 90 | 30 | 학생 작성 | |
| 스마트폰 옷 사진 | Teachable Machine(3클래스) | 60장 이상 | 15장 이상 | 학생 작성 | |

**최종 제출:** Teachable Machine 클래스별 학습 화면, 평가 결과표, 스마트폰 사진의 실제 예시(개인정보 제거), 오분류 분석, Fashion-MNIST와 실제 사진의 차이 설명을 기존 CSV 및 캡처 자료에 추가합니다.

## 11단계 | 제공된 의류 이미지로 Teachable Machine 파일·웹캠 분류하기

**학습 목적:** 스마트폰 촬영이 어려운 학생도 바로 실습할 수 있도록 티셔츠·바지·운동화의 **학습용 72장 및 시험용 30장** 이미지 파일을 제공하고, 같은 Teachable Machine 프로젝트에서 **File(파일)**과 **Webcam(웹캠)** 두 방법을 각각 실행합니다.

**준비된 이미지:** [티셔츠·바지·운동화 이미지 ZIP 다운로드](https://github.com/itlects/2026-2_ai-data/raw/refs/heads/main/Week09/data/Week09_TM_Clothes_Train_Test.zip) / [Google Drive 이미지 ZIP](https://drive.google.com/file/d/1PGfP_i0kq_Q1OO6HYxc91An3TqJGwwGT/view)

> 이미지들은 저작권 걱정 없이 수업에 사용할 수 있도록 만든 **합성 의류 일러스트**입니다. 실제 의류 상품 사진은 아니므로, 실제 사진을 잘 분류할지는 별도 평가해야 합니다. `train`과 `test` 폴더를 절대 섞지 않습니다.

**11-1. 클래스별 학습(파일 업로드)**

1. ZIP을 다운로드하고 압축 해제합니다. `train/tshirt`, `train/pants`, `train/sneakers` 및 `test/` 폴더가 생성됩니다.
2. [Teachable Machine](https://teachablemachine.withgoogle.com/) → **Get Started → Image Project → Standard image model**을 선택합니다.
3. `Class 1`, `Class 2`, `Class 3`의 이름을 각각 `T-shirt`, `Pants`, `Sneakers`로 변경합니다.
4. 각 클래스의 **Upload** 버튼을 눌러 `train` 폴더의 해당 이미지 **24장씩**을 업로드합니다. 3개 클래스 × 24장 = **72장**입니다.
5. **Train Model**을 클릭하고 학습 완료를 기다립니다. 이때 `test` 이미지는 사용하지 않습니다.

**11-2. 방법 A — Webcam으로 실시간 분류**

1. **Preview**에서 입력 방법으로 **Webcam**을 선택하고 브라우저의 카메라 권한을 허용합니다.
2. 티셔츠·바지·운동화 실물을 차례로 카메라 앞에 놓습니다. 사용자의 얼굴이나 다른 사람은 촬영하지 않습니다.
3. 각 물체를 정면과 옆면, 밝은 배경과 어두운 배경으로 바꾸어 비추고 **예측 클래스 및 신뢰도(%)**를 기록합니다.
4. 웹캠 미지원 PC라면 스마트폰으로 촬영하여 파일로 저장한 후, 다음 방법 B로 대체할 수 있습니다.
5. **주의:** 제공된 학습 이미지가 일러스트이므로 실제 제품을 웹캠으로 비추면 오분류될 수 있습니다. 이때 직접 촬영한 실물 사진을 클래스별로 추가 학습한 뒤 다시 시험해 보고 결과 차이를 적습니다. 추가 학습에 사용한 사진은 평가에 사용하지 않습니다.

**11-3. 방법 B — File(파일 업로드)로 분류**

1. Preview의 입력 유형을 **File(또는 Upload)**로 변경합니다. UI 명칭은 업데이트에 따라 달라질 수 있습니다.
2. **`test/tshirt`의 10장**을 하나씩 선택하고 예측값을 기록합니다. 이어서 `test/pants` 10장, `test/sneakers` 10장도 평가합니다.
3. 반드시 학습에 넣지 않은 **총 30장**을 테스트하고 정확도를 `정답 수 ÷ 30 × 100`으로 계산합니다.
4. 정답과 예측이 다른 이미지가 있으면 해당 이미지의 파일명·예측 클래스·신뢰도를 기록합니다.

**11-4. 결과 기록표**

| 테스트 방식 | 평가 대상 | 평가 개수 | 정답 수 | 정확도 | 관찰 내용 |
| --- | --- | ---: | ---: | ---: | --- |
| File | 제공 시험 이미지(`test/`) | 30 | 직접 기록 | 정답수/30 | 잘못 분류된 이미지 확인 |
| Webcam | 실제 옷 실물, 각 클래스 3회 이상 | 9회 이상 | 직접 기록 | 정답수/평가수 | 각도·배경·조명 영향 |
| File | 본인이 찍은 새로운 옷 사진(선택) | 9장 이상 | 직접 기록 | 정답수/평가수 | 실제 사진의 오분류 이유 |

**Python 개념 연결:** 이 단계에서는 Python으로 모델을 훈련시키지는 않습니다. 그러나 `train`과 `test`의 분리는 앞선 Colab의 `fit(X_train, y_train)`과 `predict(X_test)`에 대응합니다. `정확도 = 정답 수 / 전체 평가 개수`는 앞선 `accuracy_score(y_test, pred)`와 같은 개념입니다.

**확인 질문:** (1) File 테스트 정확도와 Webcam 테스트 정확도가 왜 다를까요? (2) 카메라 권한이 없으면 어떤 대체 실습을 할 수 있나요? (3) `test` 사진을 학습시켜 버리면 결과가 왜 신뢰하기 어려울까요?

**제출:** 학습 클래스 3개 화면, File 분류 3회 이상 캡처(클래스별 1회 이상), Webcam 분류 3회 이상 캡처(클래스별 1회 이상), 평가표 및 오류 해석. 카메라가 없는 학생은 파일 업로드로 직접 촬영한 의류 사진 9장 이상을 별도로 시험하고 대체 사유를 기록합니다.

