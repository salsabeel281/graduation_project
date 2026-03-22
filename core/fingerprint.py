def generate_fingerprint(records):
    if not records:
        return {}

    fingerprint = {}
    fingerprint["avg_key_interval"] = sum(r["avg_key_interval"] for r in records) / len(records)
    fingerprint["avg_mouse_speed"] = sum(r["avg_mouse_speed"] for r in records) / len(records)
    fingerprint["avg_download_speed_mbps"] = sum(r["download_speed_mbps"] for r in records) / len(records)
    fingerprint["avg_upload_speed_mbps"] = sum(r["upload_speed_mbps"] for r in records) / len(records)
    fingerprint["avg_signal_strength"] = sum(r["signal_strength"] for r in records) / len(records)
    return fingerprint