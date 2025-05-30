from abc import ABC, abstractmethod
from typing import Any
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from cover.event import EventForm

class BasePlatform(ABC):
    """
    Base class for all platforms.
    """

    def __init__(self, source: str, form_url: str, target: str, event_form:EventForm) -> None:
        self.source = source
        self.url = form_url
        self.target = target
        self.event = event_form
        if event_form:
            self.banner_url = event_form.find_banner()
        else:
            self.banner_url = None
        
    def ping(self, tagline, image:str=None, message="") -> bool:
        """
        Send a message to the target platform.
        """

        if not image:
            image = self.__create_image(tagline)
        else:
            if isinstance(image, str):
                response = requests.get(image)
                if response.status_code == 200:
                    image = BytesIO(response.content)
                else:
                    raise ValueError(f"Failed to retrieve image from URL: {image}")
            elif not isinstance(image, BytesIO):
                raise ValueError("Image must be a URL or a BytesIO object.")

        return self.__send_message(image, message)

    @abstractmethod
    def __send_message(self, image: BytesIO, message:str) -> bool:
        pass

    def __create_image(self, message: str):
        """
        Create an image with the message and banner.
        """
        # retrieve banner
        response = requests.get(self.banner_url)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve banner: {response.status_code}")
            
        # create image, banners are 2:1 ratio, so 1000x500
        # so, to include text at the bottom, we need to create a 1000x600 image
        img = Image.new("RGB", (1000, 600), (30, 30, 30))
        
        banner = Image.open(BytesIO(response.content))
        banner = banner.resize((1000, 500))
        img.paste(banner, (0, 0))

        # add text to the image with a large font
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("FiraSans.ttf", 32)
        except IOError:
            font = ImageFont.load_default().font_variant(size=32)

        attendee_count = getattr(self.event, 'attendee_count', 0)
        lines = [message, f"Total attendees: {attendee_count - 1} "]  # Leave space for +1
        
        # First line of text
        bbox1 = draw.textbbox((0, 0), lines[0], font=font)
        text_width1 = bbox1[2] - bbox1[0]
        text_position1 = ((1000 - text_width1) // 2, 510)
        
        base_text = lines[1]
        plus_text = "+1"
        bbox2 = draw.textbbox((0, 0), base_text + plus_text, font=font)
        text_width2 = bbox2[2] - bbox2[0]
        text_position2 = ((1000 - text_width2) // 2, 550)
        
        draw.text(text_position1, lines[0], fill=(255, 255, 255), font=font)
        draw.text(text_position2, base_text, fill=(255, 255, 255), font=font)
        
        # Calculate position for +1 and draw it in green
        bbox_base = draw.textbbox((0, 0), base_text, font=font)
        plus_pos_x = text_position2[0] + (bbox_base[2] - bbox_base[0])
        
        # Draw +1 with shadow effect in green
        draw.text((plus_pos_x + 2, text_position2[1] + 2), plus_text, fill=(0, 0, 0, 128), font=font)
        draw.text((plus_pos_x, text_position2[1]), plus_text, fill=(0, 255, 0), font=font)  # Green color

        # return bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return img_bytes
