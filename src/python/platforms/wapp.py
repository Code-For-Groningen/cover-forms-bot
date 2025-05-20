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
        self.command_file = "/tmp/wapp_command.txt"
        logging.info(f"JavaScript PID: {self.js_pid}")
        # wait for the Wapp to be ready
        self.__wait_for_wapp()
        self.ping(tagline="Hi! I am **definitely** not a bot! I'm on WhatsApp now!",
                  image="https://static.wikia.nocookie.net/among-us-wiki/images/7/72/Green.png/revision/latest?cb=20211122214650",
                  message=f"Hi! I am *definitely* not a bot! Glad to be in the `{target}` clique now!")

    def __wait_for_wapp(self) -> None:
        # wait until the command_file is created and contains IAMREADY
        while not os.path.exists(self.command_file):
            sleep(1)
        with open(self.command_file, "r") as f:
            count = 0
            while 1<2:
                if count > 60:
                    raise RuntimeError("Timeout, log into whatsapp faster bro.")
                logging.info("Waiting for Wapp")
                command = f.read()
                if command.strip() == "IAMREADY":
                    logging.info("Handshake with Wapp completed.")
                    # clear the command file
                    with open(self.command_file, "w") as f:
                        f.write("")
                    break
                sleep(5) # busy wait

    def _BasePlatform__send_message(self, image: BytesIO, message) -> bool:
        try:
            # save the image to a temporary file
            image_path = "temp_image.png"
            with open(image_path, "wb") as f:
                f.write(image.getbuffer())
            
            if not message:
                response = requests.get("https://www.buzzwordipsum.com/buzzwords?format=html&paragraphs=1&type=words")
                random_text = response.text.replace("<p>", "").replace("</p>", "")
                random_words = random_text.split(" ")
                message = " ".join(random_words[:5]).strip()
            
            image_path = os.path.abspath("temp_image.png")
            command = f'"{self.target}" {image_path} "{message}"'
            
            with open(self.command_file, "w") as f:
                f.write(command)
            
            # disgusting
            os.kill(self.js_pid, signal.SIGUSR1)
            
            sleep(10) # absolutely horrid massive delay, but js slow 
            # Clean up the temporary image file
            os.remove(image_path)

            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False