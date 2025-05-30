from .cover import Cover
from .event import Event, EventForm, EventProtocol
from platforms.base import BasePlatform
import csv
import os
import logging

class Form:
    def __init__(self, name: str, url: str, cover: Cover, platforms: list) -> None:
        self.form = EventForm(name, url, cover)
        self.cover = cover
        self.url = url

        protocols = [FormProtocol(platform) for platform in platforms]
        self.event = Event(self.form, protocols)
        self.attendees = self.__check_event()
        self.form.attendee_count = len(self.attendees)
        
        logging.debug(f"Attendees: {self.attendees}")

    def run(self) -> None:
        new_attendees = self.__check_event()
        
        old_attendees = set(str(attendee) for attendee in self.attendees)
        new_attendees = [attendee for attendee in new_attendees if str(attendee) not in old_attendees]
        
        if new_attendees:
            self.attendees.extend(new_attendees)
            self.form.attendee_count = len(self.attendees)
            self.form.latest_attendees = new_attendees
            self.event.process()


    def __parse_csv(self, filename: str="attendees.csv") -> list[str]:
        """
        Parse the CSV file and return a list of attendees.
        """
        attendees = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            raw_fields = next(reader)
            fields = []
            for field in raw_fields:
                field = field.replace('\ufeff', '').strip()
                fields.append(field)
            
            logging.debug(f"Field names: {fields}")
            
            for row in reader:
                if row and len(row) > 0: 
                    attendee = {fields[i].lower().replace(" ", "_"): row[i] for i in range(len(fields))}
                    if attendee not in attendees:
                        attendees.append(attendee)
        os.remove(filename)
        return attendees

    def __check_event(self):
        """
        Check the event for new attendees.
        """
        
        # check if logged in
        if not self.cover.logged_in:
            self.cover.check_login()
        # get the event page
        session = self.cover.get_session()
        r = session.get(self.url)
        r.raise_for_status()

        # download the CSV file (append /export to the URL)
        csv_url = self.url + "/export"
        r = session.get(csv_url)
        r.raise_for_status()

        with open("attendees.csv", "wb") as f:
            f.write(r.content)
        attendees = self.__parse_csv("attendees.csv")

        return attendees

class FormProtocol(EventProtocol):
    """Protocol implementation for handling form-related events"""
    
    def __init__(self, platform:BasePlatform) -> None:
        self.platform = platform
    
    def handleEvent(self, form:Form):
        self.platform.event = form
        self.platform.ping()

