import socket
import requests
import psutil

last_sent = psutil.net_io_counters().bytes_sent
last_recv = psutil.net_io_counters().bytes_recv

def collect_network_info():
    global last_sent, last_recv
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except:
        local_ip = "0.0.0.0"
    try:
        public_ip = requests.get("https://api.ipify.org").text
    except:
        public_ip = "0.0.0.0"
    counters = psutil.net_io_counters()
    upload_bytes = counters.bytes_sent - last_sent
    download_bytes = counters.bytes_recv - last_recv
    last_sent, last_recv = counters.bytes_sent, counters.bytes_recv
    return {
        "ip_address": local_ip,
        "public_ip": public_ip,
        "download_bytes": download_bytes,
        "upload_bytes": upload_bytes
    }
