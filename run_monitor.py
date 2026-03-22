import time
import csv
from config import MONITOR_DURATION

from core.buffer import Buffer
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info
from config import SAVE_INTERVAL, FINGERPRINT_FILE

buffer = Buffer()

# ===============================
# Load Fingerprint
# ===============================

def load_fingerprint():
    try:
        with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
            row = next(csv.DictReader(f))
            fingerprint = {}

            for k, v in row.items():
                try:
                    fingerprint[k] = float(v)
                except:
                    fingerprint[k] = v

            return fingerprint
    except:
        return None


fingerprint = load_fingerprint()

if not fingerprint:
    print("❌ No fingerprint found! Run training first.")
    exit()

print("==========================================")
print("START MONITORING (60 seconds)")
print("==========================================")

# ===============================
# Threat Scoring Function
# ===============================

def calculate_threat_score(record, fingerprint):

    score = 0

    # Numeric comparison
    numeric_keys = [
        "avg_key_interval",
        "avg_mouse_speed",
        "download_bytes",
        "upload_bytes"
    ]

    for key in numeric_keys:
        if key in fingerprint and key in record:
            fp_val = float(fingerprint.get(key, 0))
            rec_val = float(record.get(key, 0))

            if fp_val != 0:
                diff_ratio = abs(rec_val - fp_val) / fp_val

                if diff_ratio > 0.5:
                    score += 20
                elif diff_ratio > 0.3:
                    score += 10

    # Location check
    if record.get("country") != fingerprint.get("country"):
        print("⚠️ COUNTRY CHANGED!")
        score += 40

    return min(score, 100)


# ===============================
# Monitoring Loop
# ===============================

start = time.time()
total_records = 0
total_score = 0
while time.time() - start < MONITOR_DURATION:


    record = {}
    record.update(collect_input_event())
    record.update(collect_active_application())
    record.update(collect_network_info())
    record.update(collect_location_info())

    buffer.add(record)
    buffer.flush()

    threat_score = calculate_threat_score(record, fingerprint)

    total_score += threat_score
    total_records += 1

    print(f"Threat Score: {threat_score}")

    time.sleep(SAVE_INTERVAL)


# ===============================
# Final Report
# ===============================

average_score = total_score / total_records if total_records else 0

print("==========================================")
print("MONITORING FINISHED")
print("Average Threat Score:", round(average_score, 2))

if average_score < 20:
    print("✅ Behavior Normal (Low Risk)")
elif average_score < 50:
    print("⚠️ Medium Risk Detected")
else:
    print("❌ High Risk Behavior Detected")

print("==========================================")