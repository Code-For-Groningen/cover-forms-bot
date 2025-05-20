import os
import time
import logging
from cover.cover import Cover
from cover.form import Form
from platforms.discord import Discord
from platforms.wapp import Wapp
from cover.event import EventForm

# Example values:
FORM_URL = "https://svcover.nl/sign_up/501/entries"
FORM_NAME = "Cover Form 501"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1374263596099440772/3jhvb1RgMzB7A2hzpoLK4IlVFG8aqxGXFXai9LMDOK6Kqo9q3jIrlC0j7iM5u5W5vwsL"
WHATSAPP_GROUP_ID = "group asdf"


# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Get Cover credentials from environment variables
    cover_email = os.getenv("COVER_EMAIL")
    cover_password = os.getenv("COVER_PASSWORD")
    
    # Initialize Cover client
    cover = Cover(username=cover_email, password=cover_password)
    
    # Use global constants for form and webhook configuration
    event_form = EventForm(FORM_NAME, FORM_URL, cover)
    
    discord_platform = Discord(FORM_NAME, FORM_URL, DISCORD_WEBHOOK_URL, event_form)
    whatsapp_platform = Wapp(FORM_NAME, FORM_URL, WHATSAPP_GROUP_ID, event_form, os.getenv("WAPP_PID"))
    
    form = Form(
        name=FORM_NAME,
        url=FORM_URL,
        cover=cover,
        platforms=[discord_platform, whatsapp_platform]
    )

    # Main loop - check for updates regularly
    logger.info("Starting Cover Form Bot")
    logger.info(f"Monitoring form at {FORM_URL}")
    
    try:
        while True:
            logger.info("Checking for new form entries...")
            form.run()
            logger.info("Check complete, waiting for next cycle")
            time.sleep(20)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()