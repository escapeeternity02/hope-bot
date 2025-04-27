import os
import json
import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web

init(autoreset=True)
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

# Link of Ad Logs group
AD_LOGS_GROUP = "https://t.me/+nTWD1SFf-NEwNjJl"

def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

async def start_web_server():
    async def handle(request):
        return web.Response(text="Service is running!")
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(Fore.YELLOW + f"Web server running on port {port}")

async def auto_sender(client):
    session_id = client.session.filename.split('/')[-1]

    # Load last 2 saved messages
    try:
        history = await client(GetHistoryRequest(
            peer="me",
            limit=2,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        saved_messages = history.messages or []
        if len(saved_messages) < 2:
            print(Fore.RED + f"Need at least 2 saved messages in 'Saved Messages'. Found {len(saved_messages)}.")
            return
        print(Fore.CYAN + "Loaded last 2 messages from Saved Messages.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving messages: {e}")
        return

    # Load all groups
    try:
        groups = [d for d in await client.get_dialogs() if d.is_group]
        if not groups:
            print(Fore.RED + "No groups found.")
            return
        print(Fore.CYAN + f"Found {len(groups)} groups.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving groups: {e}")
        return

    # Load Ad Logs group entity
    try:
        ad_logs_entity = await client.get_entity(AD_LOGS_GROUP)
        print(Fore.GREEN + "Connected to Ad Logs group.")
    except Exception as e:
        print(Fore.RED + f"Error finding Ad Logs group: {e}")
        return

    # Main loop
    while True:
        selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])

        log_messages = []  # Collect logs here to send after round

        print(Fore.CYAN + f"Sending selected message to all groups...")

        for group in groups:
            try:
                await client.forward_messages(entity=group.id, messages=selected_msg.id, from_peer="me")
                log = f"✅ Sent to: {group.name or group.id}"
                print(Fore.GREEN + log)
                log_messages.append(log)
                await asyncio.sleep(random.uniform(0.5, 1.5))  # FAST sending, little sleep
            except FloodWaitError as e:
                wait_time = e.seconds + 5
                print(Fore.RED + f"FloodWaitError! Sleeping for {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                log = f"❌ Error sending to {group.name or group.id}: {str(e)}"
                print(Fore.RED + log)
                log_messages.append(log)

        # After sending to all groups -> send logs to Ad Logs group
        full_log = "\n".join(log_messages)
        try:
            await client.send_message(ad_logs_entity, f"📋 **Ad Log Report:**\n\n{full_log}")
            print(Fore.GREEN + "✅ Logs sent to Ad Logs group.")
        except Exception as e:
            print(Fore.RED + f"Error sending logs to Ad Logs group: {e}")

        # Random wait before next round: 10 to 20 minutes
        wait_seconds = random.randint(600, 1200)
        print(Fore.CYAN + f"Waiting {wait_seconds // 60} minutes before next round...")
        await asyncio.sleep(wait_seconds)

async def main():
    display_banner()
    session_name = "session1"
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")

    if not os.path.exists(path):
        print(Fore.RED + f"{path} not found. Upload session1.json to 'sessions' folder.")
        return

    with open(path, "r") as f:
        credentials = json.load(f)

    client = TelegramClient(os.path.join(CREDENTIALS_FOLDER, session_name),
                            credentials["api_id"], credentials["api_hash"])
    await client.start()

    print(Fore.GREEN + "Client authorized. Starting sender + web server...")

    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    await auto_sender(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
