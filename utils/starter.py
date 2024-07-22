import random
from aiohttp import ClientError
import aiohttp
from utils.dejendog import DejenDog
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.telegram import Accounts
import asyncio
import json

max_retries = config.MAX_RETRIES
retry_delay = config.DELAY_BETWEEN_RETRIES


async def upgrade(dejendog, thread, account):
    while True:
        try:
            await dejendog.information()
            await dejendog.bar_amount()

            level, lvlupcost, balance, boxs, box_price = await dejendog.box_mall()
            if level is not False and lvlupcost is not False and balance is not False:
                if level < config.MAX_LVL:
                    if balance > lvlupcost:
                        for attempt in range(max_retries):
                            upgrade = await dejendog.upgrade_lvl()
                            if upgrade is True:
                                logger.success(f"Thread {thread} | {account} | Successfully upgraded to {level + 1} lvl!")
                                await asyncio.sleep(random.uniform(config.SLEEP_BETWEEN_UPGRADES[0], config.SLEEP_BETWEEN_UPGRADES[1]))
                                break
                            else:
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                                    logger.error(f"Thread {thread} | {account} | Failed to upgrade. Try again..")
                                else:
                                    logger.error(f"Thread {thread} | {account} | Failed to upgrade.")
                                    break
                else:
                    return True
            else:
                logger.error(f"Thread {thread} | {account} | Failed to get info about upgrade level")
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(120)


async def do_tasks(dejendog, thread, account):
    while True:
        try:
            tasks = await dejendog.get_tasks()
            for task in tasks:
                if (task['taskId'] == 50 or task['taskId'] == 51 or task['taskId'] == 52 or
                        task['taskId'] == 53 or task['taskId'] == 54):
                    logger.success(f"Thread {thread} | {account} | All tasks have been completed!")
                    return True
                for attempt in range(max_retries):
                    if task['finished'] is None or task['finished'] is False:
                        do_task = await dejendog.do_task(task['taskId'])
                        if do_task is True:
                            logger.success(f"Thread {thread} | {account} | Task successfully done! +{task['reward']} coins")
                            await asyncio.sleep(random.uniform(config.SLEEP_BETWEEN_TASKS[0], config.SLEEP_BETWEEN_TASKS[1]))
                            break
                        else:
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                logger.error(f"Thread {thread} | {account} | Task was failed. Try again..")
                            else:
                                logger.error(f"Thread {thread} | {account} | Task was failed.")
                                break
                    else:
                        continue
            await asyncio.sleep(random.uniform(config.SLEEP_BETWEEN_TASKS_CHECK[0], config.SLEEP_BETWEEN_TASKS_CHECK[1]))
        except Exception as e:
            logger.error(e)


async def collect(dejendog, thread, account):
    randint1 = config.TAPS_COUNT[0]
    randint2 = config.TAPS_COUNT[1]
    while True:
        try:
            await dejendog.bar_amount()

            level = dejendog.level()
            now_energy = dejendog.now_energy()
            max_energy = dejendog.max_energy()

            amount = random.randint(randint1, randint2)

            if level >= 50:
                if now_energy + 100 < max_energy:
                    for attempt in range(max_retries):
                        tapping, collected = await dejendog.collect(amount=0)
                        if tapping is True:
                            logger.success(f"Thread {thread} | {account} | Successfully collected {collected} gold!")
                            await asyncio.sleep(config.SLEEP_BETWEEN_TAPS_SESSIONS)
                            break
                        else:
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                logger.error(f"Thread {thread} | {account} | Failed to tap. Try again..")
                            else:
                                logger.error(f"Thread {thread} | {account} | Failed to tap.")
                                break
                else:
                    await asyncio.sleep(random.randint(15, 30))
            else:
                if now_energy - amount * level > 0:
                    for attempt in range(max_retries):
                        tapping, collected = await dejendog.collect(amount=amount)
                        if tapping is True:
                            logger.success(f"Thread {thread} | {account} | Successfully tapped {collected} gold!")
                            await asyncio.sleep(config.SLEEP_BETWEEN_TAPS_SESSIONS)
                            break
                        else:
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                                logger.error(f"Thread {thread} | {account} | Failed to tap. Try again..")
                            else:
                                logger.error(f"Thread {thread} | {account} | Failed to tap.")
                                break
                else:
                    await asyncio.sleep(random.randint(15, 30))
        except Exception as e:
            logger.error(f"Thread {thread} | {account} | {e}")
            await asyncio.sleep(40)


async def adopt(dejendog, thread, account):
    try:
        for attempt in range(max_retries):
            adopting = await dejendog.adopt()
            if adopting is None:
                return True
            elif adopting is True:
                logger.success(f"Thread {thread} | {account} | Successfully adopted pet!")
                return True
            else:
                if attempt < max_retries - 1:
                    logger.error(f"Thread {thread} | {account} | Failed to adopt pet. Try again..")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Thread {thread} | {account} | Failed to adopt pet.")
                    return False
    except Exception as e:
        logger.error(e)
        await asyncio.sleep(20)


async def buy_boxes(dejendog, thread, account):
    while True:
        try:
            level, lvlupcost, balance, boxs, box_price = await dejendog.box_mall()
            if level is not False and lvlupcost is not False and balance is not False:
                if boxs < config.AMOUNT_OF_BOXES:
                    if balance > box_price:
                        for attempt in range(max_retries):
                            buy = await dejendog.buy_box()
                            if buy is True:
                                logger.success(f"Thread {thread} | {account} | Successfully bought box for {box_price}. Total: {boxs + 1}")
                                await asyncio.sleep(config.SLEEP_BETWEEN_BUY_BOXES)
                                break
                            else:
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                                    logger.error(f"Thread {thread} | {account} | Failed to upgrade. Try again..")
                                else:
                                    logger.error(f"Thread {thread} | {account} | Failed to upgrade.")
                                    break
                elif boxs == config.AMOUNT_OF_BOXES:
                    return True
            else:
                logger.error(f"Thread {thread} | {account} | Failed to get info about upgrade level")
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(120)


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    dejendog = DejenDog(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    if await dejendog.login():
        await adopt(dejendog, thread, account)
        if config.BUY_BOXES is True:
            tasks = [
                collect(dejendog, thread, account),
                do_tasks(dejendog, thread, account),
                upgrade(dejendog, thread, account),
                buy_boxes(dejendog, thread, account)
            ]
        else:
            tasks = [
                collect(dejendog, thread, account),
                do_tasks(dejendog, thread, account),
                upgrade(dejendog, thread, account)
            ]

        await asyncio.gather(*tasks)
    else:
        await dejendog.logout()


async def stats():
    try:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(
                DejenDog(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

        data = await asyncio.gather(*tasks)

        path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
        columns = ['Phone number', 'Name', 'Balance', 'Boxs', 'Level', 'Proxy (login:password@ip:port)']

        df = pd.DataFrame(data, columns=columns)
        df.to_csv(path, index=False, encoding='utf-8-sig')

        logger.success(f"Saved statistics to {path}")
    except Exception as e:
        logger.error(e)


async def check_proxy(proxy: str) -> bool:
    proxy_auth = None
    if '@' in proxy:
        proxy_parts = proxy.split('@')
        proxy_auth = proxy_parts[0]
        proxy_url = proxy_parts[1]
    else:
        proxy_url = proxy

    proxy_url = f"http://{proxy_url}"

    proxy_auth = aiohttp.BasicAuth(*proxy_auth.split(':')) if proxy_auth else None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://example.com/', proxy=proxy_url, proxy_auth=proxy_auth,
                                   timeout=10) as response:
                if response.status == 200:
                    return True
                else:
                    return False
        except (ClientError, asyncio.TimeoutError):
            return False


def parse_proxies_from_file(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    proxies = []
    for account in data:
        if 'proxy' in account:
            proxies.append(account['proxy'])

    return proxies
