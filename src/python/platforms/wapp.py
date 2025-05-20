# WARNING, YOU NEED TO BE RUNNING X11 FOR THIS TO WORK
from .base import BasePlatform
from io import BytesIO
import requests

from cover.event import Event
import os
import signal
from time import sleep

import logging
logging.basicConfig(level=logging.INFO)

class Wapp(BasePlatform):
    def __init__(self, source: str, form_url:str, target: str, event:Event, js_pid:int) -> None:
        super().__init__(source, form_url, target, event)
        self.target = target
        if not js_pid:
            raise ValueError("JavaScript process ID is required for Wapp platform.")
        self.js_pid = int(js_pid) # docker complained
        logging.info(f"JavaScript PID: {self.js_pid}")
        
    def _BasePlatform__send_message(self, image: BytesIO) -> bool:
        try:
            # save the image to a temporary file
            image_path = "temp_image.png"
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())
            
            response = requests.get("https://www.buzzwordipsum.com/buzzwords?format=html&paragraphs=1&type=words")
            random_text = response.text.replace("<p>", "").replace("</p>", "")
            random_words = random_text.split(" ")
            message = " ".join(random_words[:5]).strip()
            
            image_path = os.path.abspath("temp_image.png")
            command = f'"{self.target}" {image_path} "{message}"'
            
            temp_command_file = f"/tmp/wapp_command.txt"
            with open(temp_command_file, "w") as f:
                f.write(command)
            
            # disgusting
            os.kill(self.js_pid, signal.SIGUSR1)
            
            sleep(2)
            # Clean up the temporary image file
            os.remove(image_path)

            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False