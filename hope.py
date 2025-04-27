import os
import json
import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web

init(autoreset=True)
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

# 🟢 Web server
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

# 🚀 Corrected Auto Sender (Send to all groups each time)
async def auto_pro_sender(client, forwards_per_day=100):
    session_id = client.session.filename.split('/')[-1]

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

    try:
        groups = [d for d in await client.get_dialogs() if d.is_group]
        if not groups:
            print(Fore.RED + "No groups found.")
            return
        print(Fore.CYAN + f"Found {len(groups)} groups.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving groups: {e}")
        return

    # Calculate 100 random times inside 24 hours
    seconds_in_day = 24 * 60 * 60
    scheduled_times = sorted(random.sample(range(seconds_in_day), forwards_per_day))

    start_time = asyncio.get_event_loop().time()
    
    print(Fore.CYAN + "Starting 24/7 random sender...")

    for scheduled_delay in scheduled_times:
        now = asyncio.get_event_loop().time()
        wait_time = (start_time + scheduled_delay) - now
        if wait_time > 0:
            print(Fore.CYAN + f"Waiting {round(wait_time)} seconds before next send...")
            await asyncio.sleep(wait_time)
        
        # Pick 1 random message (from last 2)
        selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])

        print(Fore.CYAN + f"Sending message to all groups...")

        for group in groups:
            try:
                await client.forward_messages(entity=group.id, messages=selected_msg.id, from_peer="me")
                print(Fore.GREEN + f"Sent to {group.name or group.id}")
                await asyncio.sleep(random.randint(2, 5))  # small delay between groups to be more human-like
            except Exception as e:
                print(Fore.RED + f"Error sending to {group.name or group.id}: {e}")

    print(Fore.CYAN + "Completed all scheduled sends for today.")

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

    while True:
        await auto_pro_sender(client, forwards_per_day=100)
        print(Fore.CYAN + "Sleeping for 24 hours before next schedule...")
        await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
import os
import json
import asyncio
import random
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web

init(autoreset=True)
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

# 🟢 Web server
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

# 🚀 Corrected Auto Sender (Send to all groups each time)
async def auto_pro_sender(client, forwards_per_day=100):
    session_id = client.session.filename.split('/')[-1]

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

    try:
        groups = [d for d in await client.get_dialogs() if d.is_group]
        if not groups:
            print(Fore.RED + "No groups found.")
            return
        print(Fore.CYAN + f"Found {len(groups)} groups.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving groups: {e}")
        return

    # Calculate 100 random times inside 24 hours
    seconds_in_day = 24 * 60 * 60
    scheduled_times = sorted(random.sample(range(seconds_in_day), forwards_per_day))

    start_time = asyncio.get_event_loop().time()
    
    print(Fore.CYAN + "Starting 24/7 random sender...")

    for scheduled_delay in scheduled_times:
        now = asyncio.get_event_loop().time()
        wait_time = (start_time + scheduled_delay) - now
        if wait_time > 0:
            print(Fore.CYAN + f"Waiting {round(wait_time)} seconds before next send...")
            await asyncio.sleep(wait_time)
        
        # Pick 1 random message (from last 2)
        selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])

        print(Fore.CYAN + f"Sending message to all groups...")

        for group in groups:
            try:
                await client.forward_messages(entity=group.id, messages=selected_msg.id, from_peer="me")
                print(Fore.GREEN + f"Sent to {group.name or group.id}")
                await asyncio.sleep(random.randint(2, 5))  # small delay between groups to be more human-like
            except Exception as e:
                print(Fore.RED + f"Error sending to {group.name or group.id}: {e}")

    print(Fore.CYAN + "Completed all scheduled sends for today.")

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

    while True:
        await auto_pro_sender(client, forwards_per_day=100)
        print(Fore.CYAN + "Sleeping for 24 hours before next schedule...")
        await asyncio.sleep(24 * 60 * 60)  # Sleep for 24 hours

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
