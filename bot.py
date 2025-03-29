from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, hmac, base64, hashlib, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Optimai:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://njlfcjdojmopagogfpjgcbnpmiknapnd",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Optimai - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account
    
    def stable_stringify(self, data):
        if isinstance(data, dict):
            return "{" + ",".join(
                f'"{key}":{self.stable_stringify(value)}' for key, value in sorted(data.items())
            ) + "}"
        elif isinstance(data, list):
            return "[" + ",".join(self.stable_stringify(value) for value in data) + "]"
        else:
            return json.dumps(data, separators=(",", ":"))
    
    def device_info(self):
        device_info = {
            "cpu_cores":1,
            "memory_gb":0,
            "screen_width_px":375,
            "screen_height_px":600,
            "color_depth":30,
            "scale_factor":1,
            "browser_name":"chrome",
            "device_type":"extension",
            "language":"id-ID",
            "timezone":"Asia/Jakarta"
        }
        return device_info

    def generate_client_token(self):
        client_secret = "D1A167BD1346DDF2357DA5A2F2F2F"
        payload = {
            "client_app_id": "TLG_MINI_APP_V1",
            "timestamp": int(time.time() * 1000),
            "device_info": self.device_info()
        }
        
        payload_string = self.stable_stringify(payload)
        signature = hmac.new(client_secret.encode("utf-8"), payload_string.encode("utf-8"), hashlib.sha256).digest()
        
        token_payload = payload.copy()
        token_payload["signature"] = signature.hex()
        
        token_string = self.stable_stringify(token_payload)
        client_token = base64.b64encode(token_string.encode("utf-8")).decode("utf-8")
        return client_token

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def register_nodes(self, access_token: str, proxy=None, retries=5):
        url = "https://api.optimai.network/devices/register"
        data = json.dumps(self.device_info())
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "X-Client-Authentication": self.generate_client_token()
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(access_token, proxy, Fore.RED, f"Registering Nodes Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def perform_checkin(self, access_token: str, proxy=None, retries=5):
        url = "https://api.optimai.network/daily-tasks/check-in"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": "2",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(access_token, proxy, Fore.RED, f"Perform Chechk-In Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
            
    async def process_register_nodes(self, access_token: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
        nodes = None
        while nodes is None:
            nodes = await self.register_nodes(access_token, proxy)
            if not nodes:
                proxy = self.rotate_proxy_for_account(access_token) if use_proxy else None
                await asyncio.sleep(5)
                continue
            
            self.print_message(access_token, proxy, Fore.GREEN, "Registering Nodes Success")
            return nodes
            
    async def process_perform_checkin(self, access_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
            claim = await self.perform_checkin(access_token, proxy)
            if claim and claim.get("message") == "Check-in successful":
                reward = claim.get("reward")
                self.print_message(access_token, proxy, Fore.GREEN, 
                    "Check-In Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}+{reward} OPI{Style.RESET_ALL}"
                )
            elif claim and claim.get("message") == "Check-in already completed for today":
                self.print_message(access_token, proxy, Fore.YELLOW, "Already Check-In Today")
            
            await asyncio.sleep(12 * 60 * 60)
        
    async def connect_websocket(self, access_token: str, ws_token, use_proxy: bool):
        wss_url = f"wss://ws.optimai.network/?token={ws_token}"
        headers = {
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": "ws.optimai.network",
            "Origin": "chrome-extension://njlfcjdojmopagogfpjgcbnpmiknapnd",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-WebSocket-Key": "YlDqUSX4RQ86eTGWUR1Ynw===",
            "Sec-WebSocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
        }
        while True:
            proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=120))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:
                    while True:
                        try:
                            response = await wss.receive_json()
                            if response and response.get("type") == "conn_established":
                                self.print_message(access_token, proxy, Fore.GREEN, "Websocket Is Connected")
                            elif response and response.get("type") == "uptime_updated":
                                reward = response.get("data", {}).get("reward", 0)
                                self.print_message(access_token, proxy, Fore.GREEN, 
                                    "Uptime Updated "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT}+{reward:.5f} OPI{Style.RESET_ALL}"
                                )
                    
                        except Exception as e:
                            self.print_message(access_token, proxy, Fore.YELLOW, f"Websocket Connection Closed: {Fore.RED + Style.BRIGHT}{str(e)}")
                            await asyncio.sleep(5)
                            break

            except Exception as e:
                self.print_message(access_token, proxy, Fore.RED, f"Websocket Not Connected: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
                self.rotate_proxy_for_account(access_token) if use_proxy else None
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(access_token, proxy, Fore.YELLOW, "Websocket Closed")
                break
            finally:
                await session.close()
        
    async def process_accounts(self, access_token: str, use_proxy: bool):
        tasks = []
        tasks.append(asyncio.create_task(self.process_perform_checkin(access_token, use_proxy)))
        nodes = await self.process_register_nodes(access_token, use_proxy)
        if nodes:
            ws_token = nodes.get("ws_auth_token")
            tasks.append(asyncio.create_task(self.connect_websocket(access_token, ws_token, use_proxy)))
        await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            with open('tokens.txt', 'r') as file:
                access_tokens = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(access_tokens)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for access_token in access_tokens:
                    if access_token:
                        tasks.append(asyncio.create_task(self.process_accounts(access_token, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'tokens.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Optimai()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Optimai - BOT{Style.RESET_ALL}                                       "                              
        )