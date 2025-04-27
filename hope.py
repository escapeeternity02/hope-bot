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

# 🚀 Forward messages randomly across 24 hours
async def auto_pro_sender(client, forwards_count, total_duration_sec):
    session_id = client.session.filename.split('/')[-1]

    try:
        history = await client(GetHistoryRequest("me", limit=forwards_count, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0, hash=0))
        saved_messages = history.messages or []
        if not saved_messages:
            print(Fore.RED + f"No messages in Saved Messages for session {session_id}.")
            return
        print(Fore.CYAN + f"{len(saved_messages)} saved messages retrieved for session {session_id}.")
    except Exception as e:
        print(Fore.RED + f"Error retrieving messages: {e}")
        return

    # Calculate random intervals for forwards
    interval_max = total_duration_sec // forwards_count  # Max time between forwards (in seconds)
    print(Fore.CYAN + f"\nStarting message forwarding, {forwards_count} forwards in {total_duration_sec // 3600} hours...")

    # Create list of random intervals to distribute forwards
    random_intervals = [random.randint(0, interval_max) for _ in range(forwards_count)]
    random_intervals.sort()  # Sort intervals to simulate random times

    try:
        groups = sorted([d for d in await client.get_dialogs() if d.is_group], key=lambda g: g.name.lower() if g.name else "")
        while True:  # Keep the loop running indefinitely
            for interval in random_intervals:
                # Randomly select the message to send from the last 1 or 2 messages
                selected_msg = random.choice([saved_messages[-1], saved_messages[-2]])  # Randomly select 1 or 2 most recent messages

                for group in groups:
                    try:
                        await client.forward_messages(group.id, selected_msg.id, "me")
                        print(Fore.GREEN + f"Sent message to group: {group.name or group.id}")
                    except Exception as e:
                        print(Fore.RED + f"Error forwarding to {group.name or group.id}: {e}")
                
                print(Fore.CYAN + f"Waiting {interval} seconds before next forward...")
                await asyncio.sleep(interval)  # Random sleep interval
            # After one full round of forwards, wait a longer time (for the next round)
            print(Fore.CYAN + f"Completed a round of {forwards_count} forwards. Waiting for the next round...")
            await asyncio.sleep(total_duration_sec - sum(random_intervals))  # Wait for the remaining time in the 24 hours
    except Exception as e:
        print(Fore.RED + f"Unexpected error during message forwarding: {e}")

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

    # Set 100 forwards within a 24-hour period (86400 seconds)
    await auto_pro_sender(client, forwards_count=100, total_duration_sec=86400)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(Fore.RED + f"Fatal error: {e}")
