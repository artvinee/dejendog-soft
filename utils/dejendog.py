import random
import time
from datetime import datetime
from utils.core import logger, lang_code_by_phone
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent


class DejenDog:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"http://{proxy}" if proxy is not None else None

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPE,
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code=lang_code_by_phone(phone_number)
        )

        self.bearer = None
        self.auth = None
        self.info = None
        self.bar = None

        headers = {'User-Agent': UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True,
                                             connector=aiohttp.TCPConnector(verify_ssl=False))

    async def logout(self):
        await self.session.close()

    async def stats(self):
        try:
            await self.login()

            level, lvlupcost, balance, boxs, box_price = await self.box_mall()

            await self.logout()
            await self.client.connect()
            me = await self.client.get_me()

            phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
            await self.client.disconnect()

            proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

            return [phone_number, name, balance, boxs, level, proxy]
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(60)

    @staticmethod
    def iso_to_unix_time(iso_time: str):
        return int(datetime.fromisoformat(iso_time.replace("Z", "+00:00")).timestamp()) + 1

    @staticmethod
    def current_time():
        return int(time.time())

    async def information(self):
        try:
            resp = await self.session.get('https://api.djdog.io/pet/information', proxy=self.proxy, headers=self.auth)

            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success':
                    self.info = r['data']
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(20)

    async def adopt(self):
        try:
            await self.information()

            if self.info['adopted'] is False:
                resp = await self.session.post('https://api.djdog.io/pet/adopt', proxy=self.proxy, headers=self.auth)
                if resp.status == 200:
                    r = await resp.json()
                    if r['returnCode'] == 200 and r['returnDesc'] == 'success' and r['data'] is True:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return None
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(60)

    async def collect(self, amount):
        try:
            await self.bar_amount()

            resp = await self.session.post(f'https://api.djdog.io/pet/collect?clicks={amount}', proxy=self.proxy,
                                           headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success':
                    collected = r['data']['amount']
                    return True, collected
                else:
                    return False, None
            else:
                return False, None
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(20)

    async def bar_amount(self):
        try:
            resp = await self.session.get('https://api.djdog.io/pet/barAmount', proxy=self.proxy,
                                          headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success':
                    self.bar = r['data']
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(20)

    def balance(self):
        return self.bar['goldAmount']

    def max_energy(self):
        return int(self.bar['barGoldLimit'])

    def now_energy(self):
        return self.bar['availableAmount']

    def level(self):
        return self.bar['level']

    async def get_tasks(self):
        try:
            resp = await self.session.get(f'https://api.djdog.io/task/list', proxy=self.proxy, headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success' and r['data'] is not False:
                    return r['data']['taskDetails']
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(30)

    async def do_task(self, task_id):
        try:
            resp = await self.session.post(f'https://api.djdog.io/task/finish?taskIds={task_id}', proxy=self.proxy,
                                           headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success' and r['data'] is not False:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(10)

    async def box_mall(self):
        try:
            resp = await self.session.get('https://api.djdog.io/pet/boxMall', proxy=self.proxy,
                                          headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success':
                    level = r['data']['level']
                    lvlupcost = r['data']['levelUpAmount']
                    balance = r['data']['goldAmount']
                    boxs = r['data']['boxAmount']
                    box_price = r['data']['boxPrice']
                    return level, lvlupcost, balance, boxs, box_price
                else:
                    return False, False, False, False, False
            else:
                return False, False, False, False, False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(5)

    async def upgrade_lvl(self):
        try:
            resp = await self.session.post('https://api.djdog.io/pet/levelUp/0', proxy=self.proxy,
                                          headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success' and r['data'] is True:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(5)

    async def buy_box(self):
        try:
            resp = await self.session.post('https://api.djdog.io/pet/exchangeBox/0', proxy=self.proxy,
                                           headers=self.auth)
            if resp.status == 200:
                r = await resp.json()
                if r['returnCode'] == 200 and r['returnDesc'] == 'success' and r['data'] is True:
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(5)

    async def login(self):
        try:
            await asyncio.sleep(random.uniform(5, 10))
            get_tg_web_data = await self.get_tg_web_data()
            await asyncio.sleep(random.randint(2, 3))

            if get_tg_web_data is None:
                logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
                await self.logout()
                return None
            else:
                resp = await self.session.get(f'https://api.djdog.io/telegram/login?{get_tg_web_data}', proxy=self.proxy)
                if resp.status == 200:
                    r = await resp.json()
                    if r['returnCode'] == 200 and r['returnDesc'] == 'success':
                        self.bearer = r['data']['accessToken']
                        self.auth = {
                            'Authorization': str(self.bearer)
                        }
                        return True
                    else:
                        return False
                else:
                    return False

        except Exception as e:
            logger.error(e)
            await asyncio.sleep(60)

    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            await self.client.send_message('DejenDogBot', f'/start {config.REF_CODE}')

            cnt = 0
            chat_links = [
                'dejennews',
                'HashKeyChain',
                'hashkeyhsk',
                'hashkeyglobal_announcement',
                'TonAppsHub',
                'DejenRefer',
                'HashKey_Global',
                'DejenDog'
            ]

            for link in chat_links:
                try:
                    if cnt == 2:
                        cnt = 0
                        await asyncio.sleep(5)
                    await self.client.join_chat(link)
                    cnt += 1
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.error(f"Thread {self.thread} | {self.account} | Не удалось присоединиться к {link}: {e}")

            await asyncio.sleep(2)

            web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('DejenDogBot'),
                bot=await self.client.resolve_peer('DejenDogBot'),
                platform='android',
                from_bot_menu=True,
                url='https://djdog.io'
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"
        except Exception as e:
            logger.error(e)
            await asyncio.sleep(60)
