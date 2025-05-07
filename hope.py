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

# Casual message pool
human_messages_pool = [
    "Hey, how's it going?", "What’s up everyone?", "Anyone active here?",
    "Just checking in!", "Hope you're all good!", "Hello from the other side!",
    "Haha, what's happening?", "Good vibes only!", "How are you guys doing?",
    "Any updates today?"
]

def get_random_casual_message(used_messages):
    if len(used_messages) >= len(human_messages_pool):
        used_messages.clear()
    remaining = list(set(human_messages_pool) - used_messages)
    msg = random.choice(remaining)
    used_messages.add(msg)
    return msg

# Core message sender
async def auto_pro_sender(client):
    session_id = client.session.filename.split('/')[-1]
    used_casuals = set()

    min_delay = 30
    max_delay = 60
    cooldown_seconds = 45 * 60  # 45 minutes cooldown per group
    group_last_saved_sent = {}
    group_last_any_sent = {}

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer="me", limit=5,
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
                    last_saved = group_last_saved_sent.get(group_id, 0)
                    last_any = group_last_any_sent.get(group_id, 0)

                    # Send saved message every 45 min
                    if now - last_saved >= cooldown_seconds:
                        msg = random.choice(saved_messages)
                        await client.forward_messages(group_id, msg.id, "me")
                        group_last_saved_sent[group_id] = now
                        group_last_any_sent[group_id] = now
                        print(Fore.GREEN + f"[Saved] Sent to {group.name or group.id}")

                    # Optional casual message in between
                    elif now - last_any >= cooldown_seconds / 2:
                        if random.randint(1, 100) <= random.randint(15, 25):  # 15–25% chance
                            text = get_random_casual_message(used_casuals)
                            await client.send_message(group_id, text)
                            group_last_any_sent[group_id] = now
                            print(Fore.MAGENTA + f"[Casual] Sent '{text}' to {group.name or group.id}")

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

    proxy = credentials.get("proxy")
    proxy_args = tuple(proxy) if proxy else None

    while True:
        try:
            client = TelegramClient(
                os.path.join(CREDENTIALS_FOLDER, session_name),
                credentials["api_id"],
                credentials["api_hash"],
                proxy=proxy_args
            )

            await client.connect()
            if not await client.is_user_authorized():
                print(Fore.RED + "Session not authorized.")
                return

            # Auto-reply to incoming DMs
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
                auto_pro_sender(client)
            )
        except Exception as e:
            print(Fore.RED + f"Error in main loop: {e}")
            print(Fore.YELLOW + "Reconnecting in 30 seconds...")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
