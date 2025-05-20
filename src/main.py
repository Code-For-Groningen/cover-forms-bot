import os
import time
import logging
from cover.cover import Cover
from cover.form import Form
from platforms.discord import Discord

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Discord webhook configuration
    webhook_url = "https://discord.com/api/webhooks/1374263596099440772/3jhvb1RgMzB7A2hzpoLK4IlVFG8aqxGXFXai9LMDOK6Kqo9q3jIrlC0j7iM5u5W5vwsL"
    discord_platform = Discord("Cover Form Bot", webhook_url)
    
    # You should set these environment variables securely
    # Get Cover credentials from environment variables
    cover_email = os.getenv("COVER_EMAIL")
    cover_password = os.getenv("COVER_PASSWORD")
    
    if not cover_email or not cover_password:
        logger.error("Cover credentials not found in environment variables. Please set COVER_EMAIL and COVER_PASSWORD.")
        return
    
    # Initialize Cover client
    cover = Cover(username=cover_email, password=cover_password)
    
    # Create form with the specific URL
    form_url = "https://svcover.nl/sign_up/501/entries"
    form = Form(
        name="Cover Form 501",
        url=form_url,
        cover=cover,
        platforms=[discord_platform]
    )
    
    # Main loop - check for updates every 5 minutes
    logger.info("Starting Cover Form Bot")
    logger.info(f"Monitoring form at {form_url}")
    
    try:
        while True:
            logger.info("Checking for new form entries...")
            form.run()
            logger.info("OK, waiting")
            time.sleep(20)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == "__main__":
    main()