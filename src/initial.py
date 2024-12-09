import os
import subprocess
import getpass

if not os.path.exists("bot.py"):
    print("Please run this script from the src/ directory.")
    exit(1)

env_vars = {
    # key, (prompt, password?)
    "DISCORD_BOT_TOKEN": ("Discord bot token:", True),
    "COVER_EMAIL": ("Email (svcover.nl):", False),
    "COVER_PASSWORD": ("Password:", True),
    "COVER_CHANNEL_ID": ("Channel ID to post in:", False),
    "POLL_INTERVAL": ("Polling interval (seconds):", False),
    "EMBED_IMAGE": ("Embed image URL:", False),
}

env_values = {}
for var, prompt in env_vars.items():
    if prompt[1]:
        value = getpass.getpass(prompt[0])
    else:
        value = input(prompt[0]).strip()
    if not value and var == "POLL_INTERVAL":
        value = "600"
    env_values[var] = value

script_content = "#!/bin/bash\n"
for var, value in env_values.items():
    script_content += f'export {var}="{value}"\n'
script_content += "\npython3 bot.py\n"

script_path = "run_bot.sh"
with open(script_path, "w") as script_file:
    script_file.write(script_content)

os.chmod(script_path, 0o755)

print(f"\nSetup complete! The environment variables have been saved, and the bot can be run with:\n./{script_path}")
if input("\nDo you want to run the bot now? (y/N): ").strip().lower() in ["yes", "y"]:
    subprocess.run(["./" + script_path])
