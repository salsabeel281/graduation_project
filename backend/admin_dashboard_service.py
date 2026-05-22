import requests

class AdminDashboardService:
    def __init__(self, token):
        self.base_url = "http://127.0.0.1:8000"
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_profile(self):
        try:
            r = requests.get(f"{self.base_url}/user-profile", headers=self.headers)
            return r.json() if r.status_code == 200 else None
        except Exception as e:
            print("get_profile error:", e)
            return None

    def get_all_users(self):
        try:
            r = requests.get(f"{self.base_url}/admin/users", headers=self.headers)
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            print("get_all_users error:", e)
            return []

    def get_frozen_users(self):
        try:
            r = requests.get(f"{self.base_url}/admin/frozen-users", headers=self.headers)
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            print("get_frozen_users error:", e)
            return []

    def get_system_dashboard(self):
        try:
            r = requests.get(f"{self.base_url}/system-dashboard", headers=self.headers)
            return r.json() if r.status_code == 200 else {}
        except Exception as e:
            print("get_system_dashboard error:", e)
            return {}

    def get_latest_threats(self):
        try:
            r = requests.get(f"{self.base_url}/latest-threats", headers=self.headers)
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            print("get_latest_threats error:", e)
            return []

    def unfreeze_user(self, user_id):
        try:
            r = requests.post(
                f"{self.base_url}/admin/unfreeze/{user_id}",
                headers=self.headers
            )
            return r.status_code == 200
        except Exception as e:
            print("unfreeze_user error:", e)
            return False