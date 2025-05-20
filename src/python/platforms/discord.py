
import requests
import json
import logging
from PIL import Image
from io import BytesIO

from .base import BasePlatform
from cover.event import EventForm

logging.basicConfig(level=logging.INFO)

class Discord(BasePlatform):
    def __init__(self, name, form_url: str, webhook_url: str, event_form: EventForm) -> None:
        # Initialize with form data
        super().__init__(name, form_url, webhook_url, event_form)
        self.webhook_url = webhook_url
        self.username = name
        self.avatar_url = ""

    def _BasePlatform__send_message(self, image: BytesIO) -> bool:
        data = {
            "username": self.username,
            "avatar_url": self.avatar_url
        }
        files = {
            "file": ("image.png", image.getvalue(), "image/png")
        }

        response = requests.post(self.webhook_url, data=data, files=files)
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            logging.error(f"Failed to send message: {response.status_code} - {response.text}")
            return False

    def set_avatar(self, avatar_url: str) -> None:  
        self.avatar_url = avatar_url 
        data = {
            "avatar": avatar_url
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.patch(self.webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to set avatar: {response.status_code} - {response.text}")

    def set_username(self, username: str) -> None: 
        self.username = username 
        data = {
            "username": username
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.patch(self.webhook_url, data=json.dumps(data), headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to set username: {response.status_code} - {response.text}")