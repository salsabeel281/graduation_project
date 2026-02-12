def detect_anomaly(record, fingerprint, thresholds=None):
    if thresholds is None:
        thresholds = {
            "avg_key_interval": 0.5,
            "avg_mouse_speed": 0.5,
            "download_bytes": 0.5,
            "upload_bytes": 0.5
        }
    anomalies = {}
    for key, threshold in thresholds.items():
        record_value = float(record.get(key, 0))
        fingerprint_value = float(fingerprint.get(key, 0))
        diff_ratio = abs(record_value - fingerprint_value) / (fingerprint_value + 1e-5)
        if diff_ratio > threshold:
            anomalies[key] = {
                "record": record_value,
                "fingerprint": fingerprint_value
            }
    return anomalies
