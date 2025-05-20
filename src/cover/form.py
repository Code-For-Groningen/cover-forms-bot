from .cover import Cover
from platforms.base import BasePlatform
import csv
import os
import logging

class Form:
    def __init__(self, name: str, url: str, cover: Cover, platforms: list[BasePlatform]) -> None:
        self.name = name
        self.url = url # This HAS TO BE a form link NOT an event link
        self.cover = cover
        self.platforms = platforms
        self.attendees = self.__check_event()
        logging.debug(f"Attendees: {self.attendees}")

    def __parse_csv(self, filename: str) -> list[str]:
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

    def run(self) -> None:
        # check for difference in attendees
        new_attendees = self.__check_event()
        if new_attendees != self.attendees:
            self.attendees = new_attendees
            for platform in self.platforms:
                platform.send_message()

    def save(self) -> None:
        """
        Save the events to a file.
        """
        ...
