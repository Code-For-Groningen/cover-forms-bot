from typing import Protocol, List
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)

class EventProtocol(ABC):
    """Base protocol for handling event notifications"""
    
    @abstractmethod
    def handleEvent(self, form):
        """Handle an event with the given form"""
        pass

class EventForm:
    """Container for event form data"""
    
    def __init__(self, name: str, url: str, cover) -> None:
        self.name = name
        self.url = url
        self.cover = cover
        self.attendee_count = 0
        self.banner_url = None
        self.latest_attendees = None
        self.notifiers = []

    def add_notifier(self, notifier: EventProtocol) -> None:
        """Add a notifier to the event form."""
        self.notifiers.append(notifier)

    
    
    def find_banner(self) -> str:
        """Find the banner image for the event."""
        if self.banner_url:
            return self.banner_url
            
        self.cover.check_login()
        session = self.cover.get_session()
        
        signup_url = "https://svcover.nl/sign_up"
        r = session.get(signup_url)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        form_id = self.url.strip('/').split('/')[-2]
        form_rows = soup.select("tr")
        event_url = None
        for row in form_rows:
            form_link = row.select_one("a[href*='/sign_up/']")
            if form_link and form_id in form_link['href']:
                event_link = row.select_one("a[href*='/events/']")
                if event_link:
                    event_url = "https://svcover.nl" + event_link['href']
                    break
        if not event_url:
            logging.info(f"No event URL found for form ID: {form_id}")

        if not event_url:
            raise ValueError(f"Could not find event URL for form ID: {form_id}")

        r = session.get(event_url)
        r.raise_for_status()
        event_soup = BeautifulSoup(r.text, "html.parser")

        banner_img = event_soup.select_one("header.event-header figure.image img")
        if banner_img and 'src' in banner_img.attrs:
            self.banner_url = banner_img['src']
            return self.banner_url
        else:
            raise Exception("Could not find banner image for event")

class Event:
    """Main event class that handles form processing and notifications"""
    
    def __init__(self, form: EventForm, protocols: List[EventProtocol]) -> None:
        self.id = form.url.strip('/').split('/')[-1]
        self.form = form
        self.supportedProtocols = protocols
    
    def process(self) -> None:
        """process event data and notify protocols"""
        for protocol in self.supportedProtocols:
            protocol.handleEvent(self.form)
        
        # notify all notifiers about the latest attendees
        if self.form.latest_attendees and self.form.notifiers:
            for notifier in self.form.notifiers:
                try:
                    notifier.notify(self.form.latest_attendees, self.form)
                except Exception as e:
                    logging.error(f"Notifier {type(notifier).__name__} failed: {e}")