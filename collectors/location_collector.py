import requests

def collect_location_info():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        data = response.json()

        if data["status"] == "success":
            return {
                "city": data.get("city", "Unknown"),
                "country": data.get("country", "Unknown")
            }
        else:
            return {
                "city": "Unknown",
                "country": "Unknown"
            }

    except Exception as e:
        return {
            "city": "Unknown",
            "country": "Unknown"
        }