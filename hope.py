import os
import json
import asyncio
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web
import random

# Initialize colorama for colorful outputs
init(autoreset=True)

# Folder for saving session credentials
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

# Display banner
def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

# Tiny web server to keep Render alive
async def start_web_server():
    async def handle(request):
        return web.Response(text="Service is running!")

    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    print(Fore.YELLOW + "Web server started to keep Render service alive.")

# The sender function with anti-ban delay between groups
async def auto_pro_sender(client, delay_after_all_groups):
    session_id = client.session.filename.split('/')[-1]
    num_messages = 1
    per_group_delay = 1  # base delay between each group (anti-ban)

    while True:
        try:
            # Get saved messages
            history = await client(GetHistoryRequest(
                peer="me",
                limit=num_messages,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))
            if not history.messages:
                print(Fore.RED + f"No messages found in Saved Messages for session {session_id}.")
                await asyncio.sleep(60)
                continue

            saved_messages = history.messages
            print(Fore.CYAN + f"{len(saved_messages)} saved messages retrieved for session {session_id}.\n")

            groups = sorted([d for d in await client.get_dialogs() if d.is_group],
                            key=lambda g: g.name.lower() if g.name else "")

            repeat = 1
            while True:
                print(Fore.CYAN + f"\nStarting repetition {repeat} (Unlimited mode)")
                for group in groups:
                    for msg in saved_messages:
                        try:
                            await client.forward_messages(group.id, msg.id, "me")
                            print(Fore.GREEN + f"Message sent to group: {group.name or group.id}")
                            await asyncio.sleep(per_group_delay + random.uniform(0.3, 0.7))  # anti-ban sleep
                        except Exception as e:
                            print(Fore.RED + f"Error forwarding to {group.name or group.id}: {e}")

                print(Fore.CYAN + f"\nCompleted repetition {repeat}. Waiting {delay_after_all_groups} seconds...")
                await asyncio.sleep(delay_after_all_groups)

                if repeat % 5 == 0:
                    print(Fore.YELLOW + f"Reached {repeat} repetitions. Pausing for 35 minutes...")
                    await asyncio.sleep(35 * 60)  # 35 minutes

                repeat += 1

        except Exception as e:
            print(Fore.RED + f"Error in auto_pro_sender: {e}")
            print(Fore.YELLOW + "Retrying in 30 seconds...")
            await asyncio.sleep(30)

# Main function with auto-reconnect
async def main():
    display_banner()

    session_name = "session1"
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")

    if not os.path.exists(path):
        print(Fore.RED + f"Credentials file {path} not found. Please upload session1.json in 'sessions' folder.")
        return

    with open(path, "r") as f:
        credentials = json.load(f)

    while True:
        try:
            client = TelegramClient(os.path.join(CREDENTIALS_FOLDER, session_name),
                                    credentials["api_id"], credentials["api_hash"])
            await client.connect()

            if not await client.is_user_authorized():
                print(Fore.RED + "Session not authorized. Please upload a working session file (.session).")
                return

            print(Fore.GREEN + "Starting Auto Pro Sender mode with unlimited repetitions and 1050s delay.")

            await asyncio.gather(
                start_web_server(),
                auto_pro_sender(client, delay_after_all_groups=1050)
            )
        except Exception as e:
            print(Fore.RED + f"Error in main loop: {e}")
            print(Fore.YELLOW + "Reconnecting in 30 seconds...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
