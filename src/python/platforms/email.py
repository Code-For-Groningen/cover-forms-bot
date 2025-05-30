# This module is used to send emails to latest attendees

import requests
import json
import logging

import smtplib
from email.message import EmailMessage

import os

from .base import BasePlatform
from cover.event import EventForm

logging.basicConfig(level=logging.INFO)

class Email(BasePlatform):
    def __init__(self, from_email: str, form_url: str, to_email: str, event_form: EventForm, message:str=None) -> None:
        super().__init__(name, form_url, to_email, event_form)
        
        # Shitty dogshit hack ass email init
        # TODO: Add a way to specifically link emails and passwords
        # FIXME: This project is getting too complex
        if os.getenv("EMAIL_NAME") != from_email:
            raise ValueError(f"{from_email} != {os.getenv('EMAIL_NAME')}, please set it correctly")
        
        self.email_pass = os.getenv("EMAIL_PASS")
        self.email_host = os.getenv("EMAIL_HOST")

        if not self.email_pass or not self.email_host:
            raise ValueError("EMAIL_PASS and EMAIL_HOST environment variables must be set.")
        
        if not message:
            raise ValueError("Message cannot be empty.")
        
        # send email to latest attendees
        self.ping(message=message)

    # override ping method to send an email
    def ping(self, tagline=None, image: str = None, message: str = self.message) -> bool:
        """
        Send an email with the given image and message.
        """
        # if no image is provided, do not create an image
        if isinstance(image, str):
            response = requests.get(image)
            if response.status_code == 200:
                image = BytesIO(response.content)
            else:
                raise ValueError(f"Failed to retrieve image from URL: {image}")
        return self._BasePlatform__send_message(image, message)

    def _BasePlatform__send_message(self, image: BytesIO, message: str) -> bool:
        """
        Send an email message (and optionally image)
        """

        # create the email message
        msg = EmailMessage()
        msg['Subject'] = f'Notification for {self.event.name}'
        msg['From'] = os.getenv("EMAIL_NAME")
        msg['To'] = self.target
        logging.info(f"Sending email with message: {message}")
        return True