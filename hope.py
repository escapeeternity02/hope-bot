import os
import json
import asyncio
import random
from aiohttp import web
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet

# Initialize terminal colors
init(autoreset=True)

# Create sessions folder if not exists
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

# Display banner
def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

# Keep service alive (for platforms like Render)
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

# Background task: print casual messages every 15–20 mins
async def casual_behavior():
    casual_lines = [
        "Stretching my circuits a bit...",
        "Still here. Just observing quietly 🤖",
        "Bots need breaks too... kidding!",
        "Time flies when you're auto-posting!",
        "Looking around... all clear 👀",
        "Hope no one suspects I'm a bot... 😉",
        "Keeping it casual, staying cool 😎"
    ]
    while True:
        wait_minutes = random.randint(15, 20)
        await asyncio.sleep(wait_minutes * 60)
        print(Fore.MAGENTA + "[Casual] " + random.choice(casual_lines))

# Core message sender
async def auto_pro_sender(client):
    session_id = client.session.filename.split('/')[-1]
    min_delay = 5
    max_delay = 10
    cooldown_range = (70 * 60, 80 * 60)  # 1 hr 10 mins to 1 hr 20 mins
    group_last_saved_sent = {}

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer="me", limit=1,
                offset_date=None, offset_id=0,
                max_id=0, min_id=0,
                add_offset=0, hash=0))
            if not history.messages:
                print(Fore.RED + f"No messages in Saved Messages for {session_id}.")
                await asyncio.sleep(60)
                continue

            saved_messages = history.messages
            print(Fore.CYAN + f"{len(saved_messages)} saved message(s) loaded.\n")

            groups = sorted(
                [d for d in await client.get_dialogs() if d.is_group],
                key=lambda g: g.name.lower() if g.name else ""
            )

            now = asyncio.get_event_loop().time()

            for group in groups:
                try:
                    group_id = group.id
                    last_sent = group_last_saved_sent.get(group_id, 0)
                    cooldown_seconds = group_last_saved_sent.get(f"{group_id}_cooldown", 0)

                    if now - last_sent >= cooldown_seconds:
                        msg = saved_messages[0]
                        await client.forward_messages(group_id, msg.id, "me")
                        group_last_saved_sent[group]()_
