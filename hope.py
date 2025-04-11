from flask import Flask
import threading
import os
import time
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama for colorful outputs
init(autoreset=True)

# Folder for saving session credentials
CREDENTIALS_FOLDER = "sessions"

# Create the sessions folder if it doesn't exist
if not os.path.exists(CREDENTIALS_FOLDER):
    os.mkdir(CREDENTIALS_FOLDER)


# Function to display banner
def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")


# Function for Auto Pro Sender
async def auto_pro_sender(client, delay_after_all_groups):
    session_id = client.session.filename.split('/')[-1]  # Get session ID
    num_messages = 1  # Fixed to 1 saved message

    try:
        history = await client(
            GetHistoryRequest(
                peer="me",  # 'me' represents the "Saved Messages" chat
                limit=num_messages,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))
        if history.messages:
            saved_messages = history.messages
            print(
                Fore.CYAN +
                f"{len(saved_messages)} saved messages retrieved for session {session_id}. Forwarding...\n"
            )
        else:
            print(
                Fore.RED +
                f"No messages found in Saved Messages for session {session_id}."
            )
            return
    except Exception as e:
        print(
            Fore.RED +
            f"Failed to retrieve the last saved message for session {session_id}: {e}"
        )
        return

    groups = sorted([d for d in await client.get_dialogs() if d.is_group],
                    key=lambda g: g.name.lower() if g.name else "")

    repeat = 1
    while True:  # Run indefinitely
        print(Fore.CYAN + f"\nStarting repetition {repeat} (Unlimited mode)")

        for group in groups:
            for msg in saved_messages:
                try:
                    await client.forward_messages(group.id, msg.id, "me")
                    print(
                        Fore.GREEN +
                        f"Message sent to group: {group.name or group.id} using session {session_id}"
                    )
                except Exception as e:
                    print(
                        Fore.RED +
                        f"Error forwarding message to {group.name or group.id}: {e}"
                    )

        print(
            Fore.CYAN +
            f"\nCompleted repetition {repeat}. Waiting {delay_after_all_groups} seconds before next round..."
        )
        await asyncio.sleep(delay_after_all_groups)
        repeat += 1


# Start a tiny web server so Render doesn't kill the bot
app = Flask(__name__)

@app.route('/')
def home():
    return "Hope Bot is running!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# Start Flask server before main bot
threading.Thread(target=run).start()


# Main function
async def main():
    display_banner()

    session_name = "session1"
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")

    if not os.path.exists(path):
        print(Fore.RED + f"Credentials file {path} not found. Please upload session1.json in 'sessions' folder.")
        return

    with open(path, "r") as f:
        credentials = json.load(f)

    client = TelegramClient(os.path.join(CREDENTIALS_FOLDER, session_name),
                            credentials["api_id"], credentials["api_hash"])

    await client.connect()

    if not await client.is_user_authorized():
        print(Fore.RED + "Session not authorized. Please upload a working session file (.session).")
        return

    print(Fore.GREEN + "Starting Auto Pro Sender mode with unlimited repetitions and 500s delay.")

    await auto_pro_sender(client, delay_after_all_groups=500)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
