TRAINING_DURATION = 60  # 30 minutes
MAX_STACK_SIZE = 10000
MONITOR_DURATION = 600  # 10 minutes

SAVE_INTERVAL = 0.5   # seconds
RAW_DATA_FILE = "raw_training_data.csv"
FINGERPRINT_FILE = "fingerprint.csv"
CSV_FIELDS = [
    "timestamp", "session_id", "active_application", "window_title",
    "avg_key_interval", "min_key_interval", "max_key_interval", "key_presses_count",
    "avg_mouse_speed", "min_mouse_speed", "max_mouse_speed", "mouse_moves_count",
    "ip_address", "city", "country",
    "local_ip", "public_ip", "network_ssid", "signal_strength",
    "download_bytes", "upload_bytes", "system_time"
]