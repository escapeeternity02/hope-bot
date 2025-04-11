import os
import time
import json
import asyncio
import random
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama for colorful outputs
init(autoreset=True)

# Folder for saving session credentials
CREDENTIALS_FOLDER = "sessions"

# Create the sessions folder if it doesn't exist
if not os.path.exists(CREDENTIALS_FOLDER):
    os.mkdir(CREDENTIALS_FOLDER)


# Function to save session credentials
def save_credentials(session_name, credentials):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, "w") as f:
        json.dump(credentials, f)


# Function to load session credentials
def load_credentials(session_name):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


# Function to display banner
def display_banner():
    banner = pyfiglet.figlet_format("ESCAPExETERNITY")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @EscapEternity\n")


# Function for Auto Pro Sender
async def auto_pro_sender(client, repetitions, delay_after_all_groups):
    session_id = client.session.filename.split('/')[-1]  # Get session ID
    num_messages = int(input(Fore.MAGENTA + "How many saved messages to forward (1-3)? "))
    if num_messages < 1 or num_messages > 3:
        print(Fore.RED + "Invalid number. Using 1 message.")
        num_messages = 1
        
    try:
        history = await client(
            GetHistoryRequest(
                peer="me",  # 'me' represents the "Saved Messages" chat
                limit=num_messages,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))
        if history.messages:
            saved_messages = history.messages
            print(
                Fore.CYAN +
                f"{len(saved_messages)} saved messages retrieved for session {session_id}. Forwarding...\n"
            )
        else:
            print(
                Fore.RED +
                f"No messages found in Saved Messages for session {session_id}."
            )
            return
    except Exception as e:
        print(
            Fore.RED +
            f"Failed to retrieve the last saved message for session {session_id}: {e}"
        )
        return

    groups = sorted([d for d in await client.get_dialogs() if d.is_group],
                    key=lambda g: g.name.lower() if g.name else "")

    repeat = 1
    while True:  # Run indefinitely
        print(Fore.CYAN + f"\nStarting repetition {repeat} of {repetitions}")

        # Create tasks for all groups
        tasks = []
        for group in groups:
            for msg in saved_messages:
                tasks.append(
                    asyncio.create_task(
                        client.forward_messages(group.id, msg.id, "me")))

        # Send all messages simultaneously
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Print results with counter
        successful = 0
        for group, result in zip(groups, results):
            if isinstance(result, Exception):
                print(
                    Fore.RED +
                    f"Error forwarding message to {group.name or group.id} using session {session_id}: {result}"
                )
            else:
                successful += 1
                print(
                    Fore.GREEN +
                    f"Message successfully forwarded to group: {group.name or group.id} using session {session_id}"
                )

        print(
            Fore.CYAN +
            f"\nCompleted repetition {repeat}. Successfully sent to {successful}/{len(groups)} groups"
        )
        print(
            Fore.YELLOW +
            f"Waiting {delay_after_all_groups} seconds before next repetition..."
        )
        
        # Break delay into smaller chunks and check connection
        chunk_size = 30  # Check connection every 30 seconds
        chunks = int(delay_after_all_groups / chunk_size)
        remainder = delay_after_all_groups % chunk_size
        
        for _ in range(chunks):
            await asyncio.sleep(chunk_size)
            try:
                if not client.is_connected():
                    await client.connect()
            except Exception as e:
                print(Fore.RED + f"Connection check failed: {e}")
                try:
                    await client.connect()
                except Exception as e:
                    print(Fore.RED + f"Reconnection attempt failed: {e}")
                    return  # Exit if reconnection fails
                
        if remainder:
            await asyncio.sleep(remainder)
            
        repeat += 1


# Function for Pro Leave Groups
async def pro_leave_groups(client):
    predefined_message = (
        "For buying OTT platforms, auto-forwarding scripts, telegram otp, or other digital/social media services, "
        "please contact @EscapeEternity.")

    groups = sorted([d for d in await client.get_dialogs() if d.is_group],
                    key=lambda g: g.name.lower() if g.name else "")
    for group in groups:
        try:
            print(Fore.BLUE + f"Testing group: {group.name or group.id}")
            await client.send_message(group.id, predefined_message)
            print(
                Fore.GREEN +
                f"Test message sent successfully to group: {group.name or group.id}"
            )
        except Exception as e:
            print(
                Fore.RED +
                f"Failed to send test message to {group.name or group.id}: {e}"
            )
            try:
                await client(LeaveChannelRequest(group.id))
                print(Fore.LIGHTMAGENTA_EX +
                      f"Left group: {group.name or group.id}")
            except Exception as leave_error:
                print(
                    Fore.RED +
                    f"Failed to leave group: {group.name or group.id}: {leave_error}"
                )
        time.sleep(1)


# Main function to run tasks concurrently
async def run_tasks(clients, option, repetitions, delay_after_all_groups):
    tasks = []
    for client in clients:
        if option == 1:
            tasks.append(
                auto_pro_sender(client, repetitions, delay_after_all_groups))
        elif option == 2:
            tasks.append(pro_leave_groups(client))
    await asyncio.gather(*tasks)


# Main logic
async def main():
    display_banner()

    num_sessions = int(
        input(Fore.MAGENTA + "How many sessions would you like to log in? "))
    clients = []

    for i in range(1, num_sessions + 1):
        session_name = f"session{i}"
        credentials = load_credentials(session_name)

        if credentials:
            print(Fore.GREEN + f"\nUsing saved credentials for session {i}.")
            api_id = credentials["api_id"]
            api_hash = credentials["api_hash"]
            phone_number = credentials["phone_number"]
        else:
            print(Fore.YELLOW + f"\nEnter details for account {i}:")
            api_id = int(input(Fore.CYAN + f"Enter API ID for session {i}: "))
            api_hash = input(Fore.CYAN + f"Enter API hash for session {i}: ")
            phone_number = input(
                Fore.CYAN +
                f"Enter phone number for session {i} (with country code): ")

            credentials = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone_number": phone_number,
            }
            save_credentials(session_name, credentials)

        client = TelegramClient(os.path.join(CREDENTIALS_FOLDER, session_name),
                                api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            code = input(f'Enter the code received for {phone_number}: ')
            try:
                await client.sign_in(phone_number, code)
            except errors.SessionPasswordNeededError:
                password = input(
                    Fore.YELLOW +
                    'Two-step verification is enabled. Please enter your password: '
                )
                await client.sign_in(password=password)

        clients.append(client)

    print(Fore.MAGENTA + "\nChoose an option:")
    print(Fore.YELLOW +
          "1. Auto Pro Sender (Forward last saved message to all groups)")
    print(
        Fore.YELLOW +
        "2. Pro Leave Groups (Send predefined message and leave groups where sending fails)"
    )

    option = int(input(Fore.CYAN + "Enter your choice: "))
    repetitions, delay_after_all_groups = 0, 0

    if option == 1:
        repetitions = int(
            input(Fore.MAGENTA +
                  "How many times should the message be sent to all groups? "))
        delay_after_all_groups = float(
            input(Fore.MAGENTA +
                  "Enter delay (in seconds) after all groups are processed: "))
        print(Fore.GREEN + "Starting Auto Pro Sender...")
    elif option == 2:
        print(Fore.GREEN + "Starting Pro Leave Groups...")
    else:
        print(Fore.RED + "Invalid option selected.")
        return

    await run_tasks(clients, option, repetitions, delay_after_all_groups)

    for client in clients:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
