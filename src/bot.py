import os
import logging
import asyncio
from discord.ext import commands
import discord 

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_cogs():
    cog_directory = "cogs"
    for filename in os.listdir(cog_directory):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"{cog_directory}.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)  # Await load_extension
                logging.info(f"Loaded cog: {cog_name}")
            except Exception as e:
                logging.error(f"Failed to load cog {cog_name}: {e}")

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("Bot is ready.")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

# Run the bot
if __name__ == "__main__":
    asyncio.run(main())
