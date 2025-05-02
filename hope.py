repeat = 1
while True:
    print(Fore.CYAN + f"\nStarting repetition {repeat} (Unlimited mode)")
    for group in groups:
        for msg in saved_messages:
            try:
                await client.forward_messages(group.id, msg.id, "me")
                print(Fore.GREEN + f"Message sent to group: {group.name or group.id}")
                await asyncio.sleep(per_group_delay + random.uniform(0.3, 0.7))  # anti-ban sleep
            except Exception as e:
                print(Fore.RED + f"Error forwarding to {group.name or group.id}: {e}")

    print(Fore.CYAN + f"\nCompleted repetition {repeat}. Waiting {delay_after_all_groups} seconds...")
    await asyncio.sleep(delay_after_all_groups)

    # Add delay after every 5 repetitions
    if repeat % 5 == 0:
        print(Fore.YELLOW + f"Reached {repeat} repetitions. Pausing for 35 minutes...")
        await asyncio.sleep(35 * 60)  # 35 minutes

    repeat += 1
