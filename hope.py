import os
import time
import json
import asyncio
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

# 🚀 Forward messages forever
async def auto_pro_sender(client, delay_after_all_groups):
    session_id = client.session.filename.split('/')[-1]
    repeat = 1

    try:
        history = await client(GetHistoryRequest("me", limit=1, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        saved_messages = history.messages or []
        if not saved_messages:
            print(Fore.RED + f"No messages in Saved Messages for session {session_id}.")
            return
        print(Fore.CYAN + f"{len(saved_messages)} saved messages retrieved for session {session_id}.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving messages: {e}")
        return

    while True:
        try:
            groups = sorted([d for d in await client.get_dialogs() if d.is_group], key=lambda g: g.name.lower() if g.name else "")
            print(Fore.CYAN + f"\nStarting repetition {repeat}")
            for group in groups:
                for msg in saved_messages:
                    try:
                        await client.forward_messages(group.id, msg.id, "me")
                        print(Fore.GREEN + f"Sent to group: {group.name or group.id}")
                    except Exception as e:
                        print(Fore.RED + f"Error forwarding to {group.name or group.id}: {e}")
            print(Fore.CYAN + f"Completed repetition {repeat}. Waiting {delay_after_all_groups} seconds...")
            repeat += 1
            await asyncio.sleep(delay_after_all_groups)
        except Exception as e:
            print(Fore.RED + f"Unexpected error during repetition: {e}")
            await asyncio.sleep(30)

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
    await auto_pro_sender(client, delay_after_all_groups=500)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
