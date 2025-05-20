import os
import time
import logging
from cover.cover import Cover
from cover.form import Form
from platforms.discord import Discord
from cover.event import EventForm

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
    
    # Form and webhook configuration
    form_url = "https://svcover.nl/sign_up/501/entries"
    form_name = "Cover Form 501"
    webhook_url = "https://discord.com/api/webhooks/1374263596099440772/3jhvb1RgMzB7A2hzpoLK4IlVFG8aqxGXFXai9LMDOK6Kqo9q3jIrlC0j7iM5u5W5vwsL"
    
    # First create the event form
    event_form = EventForm(form_name, form_url, cover)
    
    # Initialize Discord platform with the event form
    discord_platform = Discord(form_name, form_url, webhook_url, event_form)
    
    # Create form with the platform
    form = Form(
        name=form_name,
        url=form_url,
        cover=cover,
        platforms=[discord_platform]
    )

    # Main loop - check for updates regularly
    logger.info("Starting Cover Form Bot")
    logger.info(f"Monitoring form at {form_url}")
    
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
        # You might want to add some retry logic here

if __name__ == "__main__":
    main()