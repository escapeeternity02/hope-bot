import os
import time
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

# Your Ad Logs group ID
AD_LOGS_LINK = "https://t.me/+nTWD1SFf-NEwNjJl"

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

# Smart Sleep with heartbeat
async def smart_sleep(total_seconds):
    interval = 30  # 30 sec heartbeat
    elapsed = 0
    while elapsed < total_seconds:
        await asyncio.sleep(min(interval, total_seconds - elapsed))
        print(Fore.YELLOW + f"❤️ Heartbeat: still alive... ({elapsed}/{total_seconds} sec)")
        elapsed += interval

# 🚀 Forward messages randomly across 24 hours
async def auto_pro_sender(client, forwards_count, total_duration_sec):
    session_id = client.session.filename.split('/')[-1]

    try:
        history = await client(GetHistoryRequest("me", limit=5, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        saved_messages = history.messages or []
        if len(saved_messages) < 2:
            print(Fore.RED + f"❌ Need at least 2 messages in Saved Messages.")
            return
        print(Fore.CYAN + f"{len(saved_messages)} saved messages retrieved.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving messages: {e}")
        return

    # Get groups
    try:
        groups = sorted([d for d in await client.get_dialogs() if d.is_group], key=lambda g: g.name.lower() if g.name else "")
        if not groups:
            print(Fore.RED + "❌ No groups found!")
            return
        print(Fore.GREEN + f"✅ Found {len(groups)} groups.")
    except Exception as e:
        print(Fore.RED + f"Error fetching groups: {e}")
        return

    while True:
        try:
            print(Fore.CYAN + f"🔄 New round starting...")
            log_text = f"🔄 New Round Started:\n"

            # Randomly select saved msg (last 1 or last 2)
            selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])
            log_text += f"Selected Msg ID: {selected_msg.id}\n\n"

            for group in groups:
                try:
                    await client.forward_messages(group.id, selected_msg.id, "me")
                    print(Fore.GREEN + f"✅ Sent to group: {group.name or group.id}")
                    log_text += f"✅ {group.name}\n"
                except Exception as e:
                    error_msg = f"❌ Error sending to {group.name or group.id}: {str(e)}"
                    print(Fore.RED + error_msg)
                    log_text += error_msg + "\n"

            # Send logs to "Ad Logs" group
            try:
                await client.send_message(AD_LOGS_LINK, log_text)
                print(Fore.GREEN + "✅ Log sent to Ad Logs group.")
            except Exception as e:
                print(Fore.RED + f"❌ Error sending log to Ad Logs: {e}")

            # Random wait
            wait_time = random.randint(int(total_duration_sec*0.7)//forwards_count, int(total_duration_sec*1.2)//forwards_count)
            print(Fore.CYAN + f"⏳ Waiting {wait_time} seconds before next round...")
            await smart_sleep(wait_time)

        except Exception as e:
            print(Fore.RED + f"Unexpected error: {e}")
            await smart_sleep(60)

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

    await auto_pro_sender(client, forwards_count=100, total_duration_sec=86400)  # 24 hours

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
