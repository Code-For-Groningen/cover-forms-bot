import smtplib
import os
import logging
from email.message import EmailMessage
from typing import List, Dict, Any
from .base import BaseNotifier

logging.basicConfig(level=logging.INFO)

class EmailNotifier(BaseNotifier):
    """
    Email notifier that sends emails to new attendees.
    """
    
    def __init__(self, 
                email_field: str, 
                subject_template: str = None, 
                body_template: str = None, 
                smtp_server: str = None,
                smtp_port: int = 587,
                sender_email: str = None,
                sender_password: str = None,
                use_tls: bool = True,
                **config):
        """
        Initialize EmailNotifier.
        
        Template vars:
            - {event_name}: Name of the event
            - {attendee_name}: Name of the attendee (can be derived from form data)
            - {attendee_email}: Email of the attendee (from form data)
        """
        super().__init__(**config)
        self.email_field = email_field
        self.subject_template = subject_template or "Welcome to {event_name}!"
        self.body_template = body_template or "Hi {attendee_name},\n\nThank you for signing up for {event_name}!"
        
        self.smtp_server = smtp_server 
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

        
        if not self.validate_config():
            raise ValueError("EmailNotifier configuration is invalid")
    
    def validate_config(self) -> bool:
        """Validate email configuration."""
        required_fields = [self.smtp_server, self.sender_email, self.sender_password]
        if not all(required_fields):
            logging.error("Missing email configuration. Please pass them")
            return False
        return True
    
    def notify(self, attendees: List[Dict[str, Any]], event_form) -> bool:
        """
        Send welcome emails to new attendees.
        """
        if not attendees:
            return True
            
        success_count = 0
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.sender_email, self.sender_password)
                
                for attendee in attendees:
                    if self._send_email_to_attendee(server, attendee, event_form):
                        success_count += 1
                    
        except Exception as e:
            logging.error(f"Failed to send emails: {e}")
            return False
        
        logging.info(f"Successfully sent {success_count}/{len(attendees)} welcome emails")
        return success_count == len(attendees)
    
    def _send_email_to_attendee(self, server, attendee: Dict[str, Any], event_form) -> bool:
        """Send email to a single attendee."""
        try:
            # Get attendee email
            attendee_email = attendee.get(self.email_field)
            if not attendee_email:
                logging.warning(f"No email found in field '{self.email_field}' for attendee: {attendee}")
                return False
            
            # Get attendee name (try common field names)
            attendee_name = (attendee.get('name') or 
                           attendee.get('first_name') or 
                           attendee.get('full_name') or 
                           attendee_email.split('@')[0] or "Attendee")
            
            # Create email message
            msg = EmailMessage()
            msg['Subject'] = self.subject_template.format(
                event_name=event_form.name,
                attendee_name=attendee_name
            )
            msg['From'] = self.sender_email
            msg['To'] = attendee_email
            
            # Set email body
            body = self.body_template.format(
                event_name=event_form.name,
                attendee_name=attendee_name,
                **attendee 
            )
            msg.set_content(body)
            
            # Send email
            server.send_message(msg)
            logging.info(f"Sent welcome email to {attendee_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {attendee.get(self.email_field, 'unknown')}: {e}")
            return False