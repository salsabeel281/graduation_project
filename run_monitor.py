import time
import csv
import joblib
import pandas as pd
import numpy as np

from config import MONITOR_DURATION, SAVE_INTERVAL, FINGERPRINT_FILE
from core.buffer import Buffer
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info

buffer = Buffer()
user_id = "user_1"

# ===============================
# Load Fingerprint
# ===============================
def load_fingerprint():
    with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
        row = next(csv.DictReader(f))
        return {
            k: float(v) if str(v).replace('.', '', 1).isdigit() else v
            for k, v in row.items()
        }

fingerprint = load_fingerprint()

# ===============================
# Load Models
# ===============================
if_model = joblib.load(f"models/{user_id}_if.pkl")
svm_model = joblib.load(f"models/{user_id}_svm.pkl")
lof_model = joblib.load(f"models/{user_id}_lof.pkl")
feature_columns = joblib.load(f"models/{user_id}_columns.pkl")

print("✅ Models + Features loaded")

# ===============================
# Baseline Update
# ===============================
def update_baseline(fp, record, alpha=0.05):
    for key, val in record.items():
        mk = key + "_mean"
        sk = key + "_std"

        if mk in fp:
            try:
                val = float(val)
                fp[mk] = (1 - alpha) * fp[mk] + alpha * val
                fp[sk] = (1 - alpha) * fp.get(sk, 0) + alpha * abs(val - fp[mk])
            except:
                pass

# ===============================
# Location Score
# ===============================
def location_score(record, fp):
    score = 0

    if record.get("country") != fp.get("country"):
        score += 2

    if record.get("isp") != fp.get("isp"):
        score += 3

    try:
        if str(record.get("ip", ""))[:6] != str(fp.get("ip", ""))[:6]:
            score += 3
    except:
        pass

    return score

# ===============================
# ML Voting (FIXED)
# ===============================
def ml_voting(df):
    votes = 0

    # ✔️ تأكيد الشكل النهائي
    df = pd.DataFrame(df, columns=feature_columns)

    if if_model.predict(df)[0] == -1:
        votes += 1

    if svm_model.predict(df)[0] == -1:
        votes += 1

    if lof_model.predict(df)[0] == -1:
        votes += 1

    return votes

# ===============================
# Score Calculation (FULL FIX)
# ===============================
def calculate_score(record, fp, memory):

    rule_score = 0

    for key in ["avg_key_interval", "avg_mouse_speed", "download_bytes", "upload_bytes"]:
        if key + "_mean" in fp:
            try:
                mean = fp[key + "_mean"]
                std = fp[key + "_std"]
                val = float(record.get(key, 0))

                if std > 0:
                    diff = abs(val - mean)

                    if diff > 2 * std:
                        rule_score += 10
                    elif diff > std:
                        rule_score += 4
            except:
                pass

    rule_score += location_score(record, fp)

    # ===============================
    # 🔥 FIX الحقيقي هنا
    # ===============================
    df_numeric = pd.DataFrame([record])

    # ✔️ نفس الأعمدة ونفس الترتيب
    df_numeric = df_numeric.reindex(columns=feature_columns, fill_value=0)

    # ✔️ تأكيد النوع (مهم جدًا)
    df_numeric = df_numeric.astype(float)

    ml_score = 0
    key_hash = str(df_numeric.values.tolist())

    votes = ml_voting(df_numeric)

    if votes > 0:
        memory[key_hash] = memory.get(key_hash, 0) + 1

        if memory[key_hash] > 3:
            ml_score = 2
        else:
            ml_score = votes * 4

    final_score = (0.5 * rule_score) + (0.5 * ml_score)

    return min(final_score, 100)

# ===============================
# Loop
# ===============================
start = time.time()
scores = []
memory = {}

print("==========================================")
print("START MONITORING")
print("==========================================")

while time.time() - start < MONITOR_DURATION:

    record = {}

    record.update(collect_input_event())
    record.update(collect_active_application())
    record.update(collect_network_info())
    record.update(collect_location_info())

    buffer.add(record)
    buffer.flush()

    s = calculate_score(record, fingerprint, memory)

    scores.append(s)
    if len(scores) > 5:
        scores.pop(0)

    smooth = sum(scores) / len(scores)

    print(f"Score: {round(s,2)} | Smoothed: {round(smooth,2)}")

    if smooth < 25:
        update_baseline(fingerprint, record)

    time.sleep(SAVE_INTERVAL)

# ===============================
# Final Result
# ===============================
avg = sum(scores) / len(scores)

print("==========================================")
print("FINAL SCORE:", round(avg, 2))

if avg < 25:
    print("✅ LOW RISK")
elif avg < 60:
    print("⚠️ MEDIUM RISK")
else:
    print("❌ HIGH RISK")

print("==========================================")