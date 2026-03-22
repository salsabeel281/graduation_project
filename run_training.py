import time
import csv
from config import TRAINING_DURATION
from core.buffer import Buffer
from collectors.input_collector import collect_input_event
from collectors.active_collector import collect_active_application
from collectors.network_collector import collect_network_info
from collectors.location_collector import collect_location_info
from config import SAVE_INTERVAL, FINGERPRINT_FILE

buffer = Buffer()
records = []

print("==========================================")
print("START TRAINING (collecting real device data)")
print("Duration: 60 seconds")
print("==========================================")

start = time.time()


while time.time() - start < TRAINING_DURATION:





    record = {}

    # Collect all real data
    record.update(collect_input_event())
    record.update(collect_active_application())
    record.update(collect_network_info())
    record.update(collect_location_info())

    # Save raw data
    buffer.add(record)
    buffer.flush()

    records.append(record)

    time.sleep(SAVE_INTERVAL)

# Safety check
if not records:
    print("❌ No data collected!")
    exit()

print("Creating behavioral fingerprint...")

fingerprint = {}

for key in records[0].keys():

    first_value = records[0][key]

    # If numeric → calculate average
    if isinstance(first_value, (int, float)):
        values = [r[key] for r in records if isinstance(r[key], (int, float))]
        if values:
            fingerprint[key] = sum(values) / len(values)
        else:
            fingerprint[key] = 0

    # If string → keep last observed value
    else:
        fingerprint[key] = records[-1][key]

# Save fingerprint
with open(FINGERPRINT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fingerprint.keys())
    writer.writeheader()
    writer.writerow(fingerprint)

print("==========================================")
print("✅ Training Finished Successfully!")
print("Fingerprint saved in:", FINGERPRINT_FILE)
print("Total Records Collected:", len(records))
print("==========================================")