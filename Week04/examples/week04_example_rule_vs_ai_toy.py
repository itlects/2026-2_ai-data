"""4주차 예제 — 소형 연습 데이터(42일, 1인)로 규칙 기반 알림 vs Isolation Forest 맛보기

* 이 CSV는 개념 설명용으로 '의도적으로 오류를 심어 둔' 가상 데이터입니다.
  (결측 1건, 칼로리 음수, 고강도 활동 720분, 걸음수 0, 걸음수 35,500 등)
* 본 실습은 Kaggle FitBit 원자료(Week04/data)로 진행합니다.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

URL = ('https://raw.githubusercontent.com/itlects/2026-2_ai-data/main/'
       'Week04/examples/week04_toy_steps_sleep.csv')
try:
    df = pd.read_csv('week04_toy_steps_sleep.csv')
except FileNotFoundError:
    df = pd.read_csv(URL)

df['date'] = pd.to_datetime(df['date'])
print(df.shape)
print(df.isna().sum())


def rule_alert(row):
    alerts = []
    if pd.notna(row['steps']) and row['steps'] < 1000:
        alerts.append('low_steps')
    if pd.notna(row['sleep_hours']) and row['sleep_hours'] < 4:
        alerts.append('short_sleep')
    if pd.notna(row['sleep_hours']) and row['sleep_hours'] > 12:
        alerts.append('long_sleep')
    if pd.notna(row['calories']) and row['calories'] <= 0:
        alerts.append('invalid_calories')
    if pd.notna(row['very_active_minutes']) and row['very_active_minutes'] > 300:
        alerts.append('active_minutes_outlier')
    return ','.join(alerts) if alerts else 'normal'


df['rule_alert'] = df.apply(rule_alert, axis=1)

features = ['steps', 'sleep_hours', 'calories', 'sedentary_minutes', 'very_active_minutes']
X = df[features].fillna(df[features].median(numeric_only=True))
df['ai_anomaly'] = np.where(
    IsolationForest(contamination=0.12, random_state=42).fit_predict(X) == -1,
    'anomaly', 'normal')
df['rule_flag'] = np.where(df['rule_alert'] == 'normal', 'normal', 'anomaly')

print(pd.crosstab(df['rule_flag'], df['ai_anomaly'], margins=True))
print(df[df['rule_flag'] != df['ai_anomaly']][['date'] + features + ['rule_alert', 'ai_anomaly']])
