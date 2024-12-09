import os
import json
import logging
import csv
from io import StringIO
from discord.ext import commands, tasks
from discord import Embed, Color
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urlparse
import random


class Attendee(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polling_interval = int(os.getenv("POLL_INTERVAL", 600))
        self.channel_id = int(os.getenv("COVER_CHANNEL_ID"))
        self.observed_form = None
        self.previous_csv_content = None
        self.polling_task = None
        self.event_pages = {}  # form_id -> [event_page, event_image]

    def cog_unload(self):
        if self.polling_task:
            self.polling_task.cancel()

    async def session_ready(self):
        await self.bot.wait_until_ready()
        session_cog = self.bot.get_cog("SessionCog")
        if session_cog is None:
            raise ValueError("SessionCog not found. Ensure it is loaded.")
        return session_cog

    async def find_event_image(self, event_url):
        session_cog = await self.session_ready()
        session = session_cog.get_session()

        response = session.get(event_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # header class event-header -> img
        header = soup.find("header", class_="event-header")
        if header:
            img = header.find("img")
            if img:
                return img.get("src")
        return None

    @commands.command(name="observe")
    async def observe(self, ctx, *, search_string: str):

        session_cog = await self.session_ready()
        session = session_cog.get_session()

        response = session.get("https://svcover.nl/signup")
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tds = soup.find_all("td", class_="is-truncated")

        # Look for form name in table cells
        for td in tds:
            a_tag = td.find("a")
            if not a_tag:
                continue

            form_name = a_tag.get_text(strip=True)
            event_link = "https://svcover.nl" + a_tag["href"]
            if search_string.lower() in form_name.lower():
                row = td.find_parent("tr")
                controls = row.find("ul", class_="controls") if row else None
                if not controls:
                    continue
                # Find a link
                form_links = controls.find_all("a", href=True)
                form_id = None
                for link in form_links:
                    if (
                        "view=update_form" in link["href"]
                        or "view=list_entries" in link["href"]
                    ):
                        # get ?form=[123]
                        qs = parse_qs(urlparse(link["href"]).query)
                        if "form" in qs:
                            form_id = qs["form"][0]
                            break

                if form_id:
                    # 👀
                    self.observed_form = {"id": form_id, "name": form_name}
                    self.previous_csv_content = None
                    self.event_pages[form_id] = [
                        event_link,
                        await self.find_event_image(event_link),
                    ]

                    if not self.polling_task:
                        self.polling_task = self.poll.start()
                    await ctx.message.add_reaction("🆗")
                    await ctx.send(f"👀 [{form_name}]({event_link}) with ID: {form_id}")
                    logging.info(
                        f"[SignupDataCog] Now observing form: {form_name} (ID: {form_id})"
                    )
                    return

        await ctx.send(
            f"Couldn't find form: {search_string}, do you have access to it?"
        )
        logging.warning(f"[SignupDataCog] Form not found: {search_string}")

    def count_entries(self, csv_content):
        return len(list(csv.reader(StringIO(csv_content)))[1:])

    @tasks.loop(seconds=10)  # dw about this it will be overwritten
    async def poll(self):

        if not self.observed_form:
            if random.randint(1, 1_000_000) == 69:
                self.bot.get_channel(self.channel_id).send(
                    "@here Host an event already..."
                )
            return

        session_cog = await self.session_ready()
        session = session_cog.get_session()

        form_id = self.observed_form["id"]
        csv_url = f"https://svcover.nl/signup?view=export_entries&form={form_id}"

        try:
            response = session.get(csv_url)
            response.raise_for_status()

            current_csv_content = response.content.decode("utf-8")
            if (
                self.previous_csv_content
                and self.previous_csv_content != current_csv_content
            ):
                new_entries = self.get_csv_diff(
                    self.previous_csv_content, current_csv_content
                )
                if new_entries:
                    # message = f"@here, new attendee {self.observed_form['name']}:\n" + \
                    #         "\n".join(new_entries) + \
                    #         f"\nTotal: {self.count_entries(current_csv_content)}"
                    embed = Embed(
                        title="New Attendee",
                        description=f"in {self.observed_form['name']}",
                        color=Color.from_str("#F6921D"),
                    )
                    embed.set_author(
                        icon_url=os.getenv(
                            "EMBED_IMAGE",
                            "https://svcover.nl/images/favicon-270x270.png",
                        ),
                        name="🎉",
                    )

                    if metadata := self.event_pages.get(form_id):
                        embed.url = metadata[0]
                        embed.set_image(url=metadata[1])

                    embed.add_field(name="Attendee", value="\n".join(new_entries))
                    embed.add_field(
                        name="Total", value=self.count_entries(current_csv_content)
                    )
                    embed.set_footer(
                        text=f"Cover Bot will ping in {self.polling_interval} seconds"
                    )
                    await self.bot.get_channel(self.channel_id).send(embed=embed)
                else:
                    # Removed
                    logging.info(f"Attendee removed from {self.observed_form['name']}")
            self.previous_csv_content = current_csv_content

        except Exception as e:
            logging.error(f"[SignupDataCog] Error checking form updates: {e}")

    def get_csv_diff(self, old_csv, new_csv):
        old_data = list(csv.reader(StringIO(old_csv)))
        new_data = list(csv.reader(StringIO(new_csv)))

        diff = set(map(tuple, new_data[1:])) - set(map(tuple, old_data[1:]))
        return [", ".join(entry) for entry in diff]

    @poll.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()

    @commands.command(name="stop_observe")
    async def stop_observe(self, ctx):
        if self.polling_task:
            self.polling_task.cancel()
            self.polling_task = None
        observed_form_name = (
            self.observed_form["name"] if self.observed_form else "None"
        )
        self.observed_form = None
        self.previous_csv_content = None
        await ctx.send(f"Stopped observing form {observed_form_name}")


async def setup(bot):
    await bot.add_cog(Attendee(bot))
