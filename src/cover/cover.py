import requests
import logging
import os

logging.basicConfig(level=logging.INFO)

class Cover:
    def __init__(self, **kwargs) -> None:
        self.username = os.getenv("COVER_EMAIL")
        self.password = os.getenv("COVER_PASSWORD")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        self.session = requests.Session()
        self.logged_in = False
        self.__log_in()

    def check_login(self) -> None:
        url = "https://svcover.nl/login"
        r = self.session.get(url)
        r.raise_for_status()
        if "Log out" in r.text:
            self.logged_in = True
            return True
        return False

    def __log_in(self):
        print("Logging in to Cover...")
        url = "https://svcover.nl/login"
        r = self.session.get(url)
        r.raise_for_status()

        # Find the CSRF token
        csrf_token_start = r.text.find('id="form__token" name="form[_token]"')
        if csrf_token_start == -1:
            raise ValueError("CSRF token field not found")
        value_attr_start = r.text.find('value="', csrf_token_start) + len('value="')
        csrf_token_end = r.text.find('" >', value_attr_start)
        csrf_token = r.text[value_attr_start:csrf_token_end]

        if not csrf_token:
            raise ValueError("CSRF token not found")

        payload = {
            "form[email]": self.username,
            "form[password]": self.password,
            "form[remember]": "1",
            "form[submit]": "",
            "form[referrer]": "/",
            "form[_token]": csrf_token,
        }

        login_resp = self.session.post(url + "?referrer=/", data=payload, headers={"User-Agent": self.user_agent})
        if not self.check_login():
            raise ValueError("Login failed. Check credentials or if the site structure has changed.")
        logging.info("Logged in to Cover successfully.")

    def get_session(self) -> requests.Session:
        """
        Returns the session object.
        """
        if not self.logged_in:
            raise ValueError("Not logged in. Call login() first.")
        return self.session
    
    def load(self) -> bool:
        """
        Load the events from the file.
        """
        ...
    