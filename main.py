from utils.core import create_sessions
from utils.telegram import Accounts
from utils.starter import start, stats, parse_proxies_from_file, check_proxy
import asyncio
import os


async def main():
    print("DejenDog soft by artvine.\n")
    action = int(input("Select action:\n1. Start soft\n2. Get statistics\n3. Create sessions\n"
                       "4. Check proxy from sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    if action == 3:
        await create_sessions()

    if action == 2:
        if not os.path.exists('statistics'): os.mkdir('statistics')
        await stats()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(start(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
            await asyncio.sleep(2)

        await asyncio.gather(*tasks)

    if action == 4:
        file_path = 'sessions/accounts.json'
        proxies = parse_proxies_from_file(file_path)

        for proxy in proxies:
            is_valid = await check_proxy(proxy)
            print(f"Proxy {proxy} is {'valid' if is_valid else 'invalid'}")


if __name__ == '__main__':
    asyncio.run(main())
