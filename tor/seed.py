import requests
import json
import os
from lg import logger as l

class SeedrClient:
    CONFIG_FILE = "seedr_session.json"
    BASE_URL = "https://www.seedr.cc"
    COMMON_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.cookies = {}
        self.load_session()

    def load_session(self):
        """Load session cookies from a file."""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "r") as file:
                data = json.load(file)
                self.cookies = data.get("cookies", {})
                self.email = data.get("email")
                for name, value in self.cookies.items():
                    self.session.cookies.set(name, value)
            l.info("Session loaded from file.")

    def save_session(self):
        """Save session cookies to a file."""
        with open(self.CONFIG_FILE, "w") as file:
            data = {"email": self.email, "cookies": self.cookies}
            json.dump(data, file)
            l.info("Session saved to file.")

    def check_session(self):
        """Check if the session is still valid."""
        response = self.session.get(f"{self.BASE_URL}/account/settings", headers=self.COMMON_HEADERS)
        return response.status_code == 200

    def login(self):
        """
        Log in to the Seedr account.
        If a valid session exists, reuse it.
        """
        if self.cookies and self.check_session():
            l.info(f"Using existing session for {self.email}.")
            return True

        if not self.email or not self.password:
            l.info("Email and password are required to log in.")
            return False

        url = f"{self.BASE_URL}/auth/login"
        headers = self.COMMON_HEADERS.copy()
        headers["Content-Type"] = "application/json"
        data = {
            "username": self.email,
            "password": self.password,
            "rememberme": "on"
        }
        response = self.session.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()
        if response_data.get("success", False):
            l.info(f"Logged in as {self.email}.")
            self.cookies = {cookie.name: cookie.value for cookie in self.session.cookies}
            self.save_session()
            return True
        l.info("Login failed.")
        return False

    def logout(self):
        """Log out the current session."""
        url = f"{self.BASE_URL}/auth/logout"
        headers = self.COMMON_HEADERS.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Referer"] = "https://www.seedr.cc/files"
        response = self.session.post(url, headers=headers)
        
        if response.status_code == 200:
            l.info(f"Logged out successfully.")
            # Clear session cookies after logout
            self.session.cookies.clear()
            if os.path.exists(self.CONFIG_FILE):
                os.remove(self.CONFIG_FILE)  # Remove the session file
            return True
        else:
            l.info("Logout failed.")
            return False

    def get_account_settings(self):
        """Retrieve account settings."""
        url = f"{self.BASE_URL}/account/settings"
        response = self.session.get(url, headers=self.COMMON_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def get_quota_used(self):
        """Retrieve quota usage."""
        url = f"{self.BASE_URL}/account/quota/used"
        response = self.session.get(url, headers=self.COMMON_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def get_folder_items(self, folder_id=0, timestamp=None):
        """Retrieve items in a folder."""
        url = f"{self.BASE_URL}/fs/folder/{folder_id}/items"
        if timestamp:
            url = f"{url}?timestamp={timestamp}"
        response = self.session.get(url, headers=self.COMMON_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def get_video_url(self, item_id):
        """Retrieve video URL for a specific item."""
        url = f"{self.BASE_URL}/presentation/fs/item/{item_id}/video/url"
        response = self.session.get(url, headers=self.COMMON_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def get_download_url(self, item_id):
        """Retrieve download URL for a specific item."""
        url = f"{self.BASE_URL}/download/file/{item_id}/url"
        response = self.session.get(url, headers=self.COMMON_HEADERS)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def fetch_torrent(self, torrent_url):
        """Fetch magnet link from a given torrent URL."""
        url = f"{self.BASE_URL}/scrape/html/torrents"
        headers = self.COMMON_HEADERS.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {"url": torrent_url}
        response = self.session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            if self.cookies and not self.check_session():
                return {"error":"Not loged or login expired"}
            else:
                return {"error":"No sesstion"}

    def add_magnet(self, magnet_link, folder_id=0):
        """Add a torrent to the account using a magnet link."""
        url = f"{self.BASE_URL}/task"
        headers = self.COMMON_HEADERS.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {
            "folder_id": folder_id,
            "type": "torrent",
            "torrent_magnet": magnet_link
        }
        response = self.session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return False

    def delete(self, item_ids):
        """
        Delete files or folders by their IDs.
        Args:
            item_ids (list): List of dictionaries with `type` and `id` for items to delete.
        """
        url = f"{self.BASE_URL}/fs/batch/delete"
        headers = self.COMMON_HEADERS.copy()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        data = {
            "delete_arr": json.dumps(item_ids)  # Convert item_ids to a JSON-encoded string
        }
        response = self.session.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return False
