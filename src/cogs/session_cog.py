import os
import requests
from discord.ext import commands
from bs4 import BeautifulSoup
import logging

class SessionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "https://svcover.nl/login?referrer=/"
        self.username = os.getenv("COVER_EMAIL")
        self.password = os.getenv("COVER_PASSWORD")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        self.session = requests.Session()
        self.logged_in = False
        self.login()

    def login(self):
        r = self.session.get(self.url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        token_input = soup.find("input", {"name": "form[_token]"})
        if not token_input:
            raise ValueError("No csrf.")
        token = token_input.get("value")

        payload = {
            "form[email]": self.username,
            "form[password]": self.password,
            "form[remember]": "1",
            "form[submit]": "",
            "form[referrer]": "/",
            "form[_token]": token
        }
        

        login_resp = self.session.post(self.url, data=payload, headers={"User-Agent": self.user_agent})
        login_resp.raise_for_status()
        if "Log out" not in login_resp.text:
            raise ValueError("Login failed. Check credentials or if the site structure has changed.")

        self.logged_in = True
        logging.info("[SessionCog] Logged in to Cover successfully.")

    def get_session(self):
        if not self.logged_in:
            self.login()
        return self.session

    def invalidate_session(self):
        self.logged_in = False

async def setup(bot):
    await bot.add_cog(SessionCog(bot))
