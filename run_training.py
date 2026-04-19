import time
import csv
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
import joblib
import pandas as pd
import numpy as np
import os

from config import TRAINING_DURATION, SAVE_INTERVAL, FINGERPRINT_FILE
from core.buffer import Buffer
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

buffer = Buffer()
records = []

user_id = "user_1"
os.makedirs("models", exist_ok=True)

print("==========================================")
print("START TRAINING")
print(f"Duration: {TRAINING_DURATION} seconds")
print("==========================================")

start = time.time()

# ===============================
# Collect Data
# ===============================
while time.time() - start < TRAINING_DURATION:

    record = {}
    record.update(collect_input_event())
    record.update(collect_active_application())
    record.update(collect_network_info())
    record.update(collect_location_info())

    buffer.add(record)
    buffer.flush()
    records.append(record)

    time.sleep(SAVE_INTERVAL)

if not records:
    print("❌ No data collected!")
    exit()

# ===============================
# Fingerprint
# ===============================
print("Creating fingerprint...")

fingerprint = {}

for key in records[0].keys():
    values = [r[key] for r in records if isinstance(r[key], (int, float))]

    if values:
        fingerprint[key + "_mean"] = np.mean(values)
        fingerprint[key + "_std"] = np.std(values)
    else:
        fingerprint[key] = records[-1][key]

with open(FINGERPRINT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fingerprint.keys())
    writer.writeheader()
    writer.writerow(fingerprint)

print("✅ Fingerprint saved!")

# ===============================
# ML Training
# ===============================
df = pd.DataFrame(records)

df_numeric = df.select_dtypes(include=['int64', 'float64']).fillna(0)

# 🔥 مهم جدًا (حل warning نهائي)
feature_columns = df_numeric.columns.tolist()
joblib.dump(feature_columns, f"models/{user_id}_columns.pkl")

if not df_numeric.empty:
    try:
        if_model = IsolationForest(contamination=0.1, random_state=42)
        if_model.fit(df_numeric)
        joblib.dump(if_model, f"models/{user_id}_if.pkl")

        svm_model = OneClassSVM(nu=0.1, kernel="rbf")
        svm_model.fit(df_numeric)
        joblib.dump(svm_model, f"models/{user_id}_svm.pkl")

        lof_model = LocalOutlierFactor(n_neighbors=20, novelty=True)
        lof_model.fit(df_numeric)
        joblib.dump(lof_model, f"models/{user_id}_lof.pkl")

        print("✅ All ML models saved!")

    except Exception as e:
        print("❌ ML Error:", e)

print("==========================================")
print("🎉 Training Completed!")
print("Records:", len(records))
print("==========================================")