import os
import time
import json
import asyncio
import random
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web

init(autoreset=True)
CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

# Ad Logs group link
AD_LOGS_LINK = "https://t.me/+nTWD1SFf-NEwNjJl"

def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapeEternity\n")

# 🟢 Web server
async def start_web_server():
    async def handle(request):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return web.Response(text=f"Service Running: {now}")
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(Fore.YELLOW + f"🌐 Web server running on port {port}")

# ❤️ Smart Sleep with heartbeat every 30 sec
async def smart_sleep(total_seconds):
    interval = 30
    elapsed = 0
    while elapsed < total_seconds:
        await asyncio.sleep(min(interval, total_seconds - elapsed))
        elapsed += interval
        now = datetime.utcnow().strftime("%H:%M:%S")
        print(Fore.MAGENTA + f"❤️ [{now}] Heartbeat alive... ({elapsed}/{total_seconds} sec)")

# 🚀 Forward saved messages to groups
async def auto_pro_sender(client):
    session_id = client.session.filename.split('/')[-1]

    try:
        history = await client(GetHistoryRequest("me", limit=5, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        saved_messages = history.messages or []
        if len(saved_messages) < 2:
            print(Fore.RED + "❌ Need at least 2 messages in Saved Messages.")
            return
        print(Fore.CYAN + f"💾 {len(saved_messages)} saved messages retrieved.")
    except Exception as e:
        print(Fore.RED + f"❌ Error retrieving messages: {e}")
        return

    try:
        groups = sorted([d for d in await client.get_dialogs() if d.is_group], key=lambda g: g.name.lower() if g.name else "")
        if not groups:
            print(Fore.RED + "❌ No groups found!")
            return
        print(Fore.GREEN + f"✅ {len(groups)} groups found.")
    except Exception as e:
        print(Fore.RED + f"❌ Error fetching groups: {e}")
        return

    while True:
        try:
            now = datetime.utcnow().strftime("%H:%M:%S")
            print(Fore.CYAN + f"🔄 [{now}] New round starting...")
            log_lines = [f"🔄 [{now}] New Round Started:\n"]

            selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])
            log_lines.append(f"📨 Selected Msg ID: {selected_msg.id}\n")

            for group in groups:
                try:
                    await client.forward_messages(group.id, selected_msg.id, "me")
                    print(Fore.GREEN + f"🟢 Sent to: {group.name or group.id}")
                    log_lines.append(f"🟢 {group.name}")
                except Exception as e:
                    error_msg = f"🔴 Error sending to {group.name or group.id}: {str(e)}"
                    print(Fore.RED + error_msg)
                    log_lines.append(error_msg)

            # Send logs to Ad Logs group
            full_log = "\n".join(log_lines)
            for i in range(0, len(full_log), 4000):  # Telegram limit safe split
                await client.send_message(AD_LOGS_LINK, full_log[i:i+4000])

            print(Fore.GREEN + "✅ Log sent to Ad Logs group.")

            # Sleep random between 12-26 min
            wait_time = random.randint(12 * 60, 26 * 60)
            next_time = (datetime.utcnow() + timedelta(seconds=wait_time)).strftime("%H:%M:%S")
            print(Fore.CYAN + f"⏳ Waiting {wait_time//60} minutes (until {next_time}) before next round...")
            await smart_sleep(wait_time)

        except Exception as e:
            print(Fore.RED + f"❗ Unexpected error: {e}")
            await smart_sleep(60)

async def main():
    display_banner()
    session_name = "session1"
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")

    if not os.path.exists(path):
        print(Fore.RED + f"❌ {path} not found. Upload session1.json to 'sessions' folder.")
        return

    with open(path, "r") as f:
        credentials = json.load(f)

    client = TelegramClient(os.path.join(CREDENTIALS_FOLDER, session_name),
                            credentials["api_id"], credentials["api_hash"])
    await client.start()

    print(Fore.GREEN + "✅ Client authorized. Starting sender + web server...")

    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())

    await auto_pro_sender(client)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"❌ Fatal error: {e}")
