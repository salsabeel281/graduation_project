import requests

class UserDashboardService:
    def __init__(self, token):
        self.base_url = "http://127.0.0.1:8000"
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    def get_profile(self):
        try:
            response = requests.get(
                f"{self.base_url}/user-profile",
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
            else:
                print("Error:", response.text)
                return None

        except Exception as e:
            print("Connection error:", e)
            return None