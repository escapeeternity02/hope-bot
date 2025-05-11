import os
import json
import asyncio
from telethon import TelegramClient, events, errors
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style, init
import pyfiglet
from aiohttp import web
import random

init(autoreset=True)

CREDENTIALS_FOLDER = "sessions"
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)

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
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    await site.start()
    print(Fore.YELLOW + "Web server started to keep Render service alive.")

message_templates = [
    "Hey {name}, how's it {feeling}?",
    "What’s up {name}?",
    "Anyone {status} today?",
    "Just {action}!",
    "Hope you're all {feeling}!",
    "Yo {name} 👋",
    "Haha, what's {topic}?",
    "Vibes check! 😎",
    "How's everyone {feeling}?",
    "Any {news} today?"
]

words = {
    "name": ["everyone", "all", "people", "friends", "fam", "guys"],
    "feeling": ["going", "rolling", "feeling", "doing"],
    "status": ["online", "awake", "around", "active"],
    "action": ["checking in", "dropping by", "saying hey", "here for a bit"],
    "topic": ["happening", "poppin", "going on", "new"],
    "news": ["updates", "news", "plans", "messages"]
}

def get_random_casual_message(used_messages):
    while True:
        template = random.choice(message_templates)
        message = template.format(
            name=random.choice(words["name"]),
            feeling=random.choice(words["feeling"]),
            status=random.choice(words["status"]),
            action=random.choice(words["action"]),
            topic=random.choice(words["topic"]),
            news=random.choice(words["news"])
        )
        if message not in used_messages:
            used_messages.add(message)
            return message

async def auto_pro_sender(client):
    session_id = client.session.filename.split('/')[-1]
    num_messages = 1
    min_delay = 4
    max_delay = 8
    used_casuals = set()

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer="me", limit=num_messages,
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

            while True:
                print(Fore.CYAN + f"\nStarting another round (no delay after full cycle)")
                for group in groups:
                    try:
                        msg = saved_messages[0]
                        await client.forward_messages(group.id, msg.id, "me")
                        print(Fore.GREEN + f"Forwarded saved message to: {group.name or group.id}")

                        if random.randint(1, 100) <= random.randint(10, 15):
                            text = get_random_casual_message(used_casuals)
                            await client.send_message(group.id, text)
                            print(Fore.MAGENTA + f"[Casual] Sent '{text}' to {group.name or group.id}")

                        delay = random.uniform(min_delay, max_delay)
                        print(Fore.YELLOW + f"Waiting {int(delay)}s before next group...")
                        await asyncio.sleep(delay)

                    except errors.FloodWaitError as e:
                        print(Fore.RED + f"FloodWaitError: Waiting {e.seconds}s")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        print(Fore.RED + f"Error sending to {group.name or group.id}: {e}")

        except Exception as e:
            print(Fore.RED + f"Error in auto_pro_sender: {e}")
            await asyncio.sleep(30)

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

            # DM auto-reply
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
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
