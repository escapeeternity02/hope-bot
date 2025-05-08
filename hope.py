import os
import json
import asyncio
import random
from aiohttp import web
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from telethon.network import MTProtoProxy

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
    cooldown_range = (70 * 60, 80 * 60)  # 70 to 80 minutes in seconds
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
                        group_last_saved_sent[group_id] = now
                        group_last_saved_sent[f"{group_id}_cooldown"] = random.randint(*cooldown_range)
                        print(Fore.GREEN + f"[Saved] Sent to {group.name or group.id}")

                    delay = random.uniform(min_delay, max_delay)
                    print(Fore.YELLOW + f"Waiting {int(delay)}s before next group...")
                    await asyncio.sleep(delay)

                except Exception as e:
                    print(Fore.RED + f"Error sending to {group.name or group.id}: {e}")
                    await asyncio.sleep(5)

        except Exception as e:
            print(Fore.RED + f"Error in auto_pro_sender: {e}")
            print(Fore.YELLOW + "Retrying in 30 seconds...")
            await asyncio.sleep(30)

# Main entry point
async def main():
    display_banner()

    session_name = "session1"
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")

    if not os.path.exists(path):
        print(Fore.RED + f"Credentials file {path} not found.")
        return

    with open(path, "r") as f:
        credentials = json.load(f)

    # Use built-in MTProto proxy (replace with your actual proxy details if necessary)
    proxy = credentials.get("proxy") or ('185.213.20.244', 443, 'f1ec0625459f73cd22d1895ce895c1df')  # Example proxy
    proxy_args = (proxy[0], proxy[1], proxy[2]) if proxy else None

    # Create a proxy object to set up the MTProto proxy correctly
    proxy = MTProtoProxy(host=proxy_args[0], port=proxy_args[1], secret=proxy_args[2])

    while True:
        try:
            client = TelegramClient(
                os.path.join(CREDENTIALS_FOLDER, session_name),
                credentials["api_id"],
                credentials["api_hash"],
                proxy=proxy
            )

            await client.connect()
            if not await client.is_user_authorized():
                print(Fore.RED + "Session not authorized.")
                return

            @client.on(events.NewMessage(incoming=True))
            async def handler(event):
                if event.is_private and not event.out:
                    try:
                        await event.reply("This is AdBot Account. If you want anything then contact @EscapeEternity!")
                        print(Fore.BLUE + f"Auto-replied to {event.sender_id}")
                    except Exception as e:
                        print(Fore.RED + f"Failed to reply to {event.sender_id}: {e}")

            print(Fore.GREEN + "Starting message sender...")

            await asyncio.gather(
                start_web_server(),
                auto_pro_sender(client),
                casual_behavior()
            )

        except Exception as e:
            print(Fore.RED + f"Error in main loop: {e}")
            print(Fore.YELLOW + "Reconnecting in 30 seconds...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
