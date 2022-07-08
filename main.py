import asyncio
import json
import random
import re
from datetime import datetime
from os import listdir, get_terminal_size
from subprocess import Popen
from os.path import isfile, join
import discord
import pytesseract
import requests
from PIL import Image
from colorama import Fore, init
import api
from ocr import get_card, get_bottom, get_top, filelength

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
path_to_ocr = "temp"
v = "b1.2.1"
update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/beta/version.txt"
with open("config.json") as f:
    config = json.load(f)

token = config["token"]
channels = config["channels"]
accuracy = float(config["accuracy"])
loghits = config["log_hits"]
logcollection = config["log_collection"]
timestamp = config["timestamp"]
update = config["update_check"]
autodrop = config["autodrop"]
debug = config["debug"]
if autodrop:
    autodropchannel = config["autodropchannel"]
    dropdelay = config["dropdelay"]
    randmin = int(config["randmin"])
    randmax = int(config["randmax"])


class Main(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.charblacklist = None
        self.aniblacklist = None
        self.animes = None
        self.chars = None
        self.messageid = None
        self.important = None
        self.current_card = None
        self.ready = False
        self.react = True
        self.timer = 0
        self.url = None
        self.missed = 0
        self.collected = 0
        self.cardnum = 0

    async def on_ready(self):
        Popen("cls", shell=True)
        await asyncio.sleep(0.5)
        thing = f"""{Fore.LIGHTMAGENTA_EX}
 ____  __.                    __             _________      .__                     
|    |/ _|____ _______ __ ___/  |______     /   _____/ ____ |__|_____   ___________ 
|      < \__  \\\\_  __ \  |  \   __\__  \    \_____  \ /    \|  \____ \_/ __ \_  __ \\
|    |  \ / __ \|  | \/  |  /|  |  / __ \_  /        \   |  \  |  |_> >  ___/|  | \/
|____|__ (____  /__|  |____/ |__| (____  / /_______  /___|  /__|   __/ \___  >__|   
        \/    \/                       \/          \/     \/   |__|        \/       
"""
        for line in thing.split('\n'):
            print(line.center(get_terminal_size().columns))
        print(Fore.LIGHTMAGENTA_EX + "─" * get_terminal_size().columns)
        tprint(
            f'{Fore.BLUE}Logged in as {Fore.RED}{self.user.name}#{self.user.discriminator} {Fore.GREEN}({self.user.id}){Fore.RESET}')
        latest_ver = update_check()
        if latest_ver != v:
            tprint(f"{Fore.RED}You are on version {v}, while the latest version is {latest_ver}")
        dprint(f"discord.py-self version {discord.__version__}")
        await self.update_files()
        self.ready = True
        asyncio.get_event_loop().create_task(self.cooldown())
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\animes.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\characters.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\aniblacklist.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\charblacklist.txt"))
        if autodrop:
            asyncio.get_event_loop().create_task(self.autodrop())

    async def on_message(self, message):
        if not self.ready or str(message.author.id) != '646937666251915264' or str(message.channel.id) not in channels:
            return

        if re.search(match, message.content):
            if self.timer != 0:
                return

            with open("temp\\card.webp", "wb") as file:
                file.write(requests.get(message.attachments[0].url).content)
            if filelength("temp\\card.webp") == 836:
                self.cardnum = 3
                for a in range(3):
                    get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)

                for a in range(3):
                    get_top(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\top{a + 1}.png")
                    get_bottom(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\bottom{a + 1}.png")
            else:
                self.cardnum = 4
                for a in range(4):
                    get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)

                for a in range(4):
                    get_top(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\top{a + 1}.png")
                    get_bottom(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\bottom{a + 1}.png")

            onlyfiles = [ff for ff in listdir("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char") if
                         isfile(join("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char", ff))]
            # print("File trovati: ", onlyfiles)
            custom_config = r'--psm 7 --oem 3 -c ' \
                            r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' \
                            r'@&0123456789/:- " '
            for img in onlyfiles:
                if "4" in img and self.cardnum != 4:
                    continue
                char = pytesseract.image_to_string(Image.open(path_to_ocr + '\\char\\' + img), lang='eng',
                                                   config=custom_config).strip()
                if message.components:
                    buttons = message.components[0].children
                else:
                    buttons = []
                for a in self.chars:
                    if api.isSomething(char, a, accuracy) and char not in self.charblacklist:
                        tprint(f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{char}{Fore.RESET}")
                        cid = message.channel.id
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(f"{current_time()} - Character: {char} - {self.url}\n")
                                else:
                                    ff.write(f"Character: {char} - {self.url}\n")
                        if img == "top1.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await asyncio.sleep(1)
                                await buttons[0].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 1
                        elif img == "top2.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[1]}")
                                await buttons[1].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 2
                        elif img == "top3.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[2]}")
                                await buttons[2].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 3
                        elif img == "top4.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[3]}")
                                await buttons[3].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 4
                for a in self.animes:
                    if api.isSomething(char, a, accuracy) and char not in self.aniblacklist:
                        tprint(f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char}{Fore.RESET}")
                        cid = message.channel.id
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(f"{current_time()} - Anime: {char} - {self.url}\n")
                                else:
                                    ff.write(f"Anime: {char} - {self.url}\n")
                        if img == "bottom1.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await buttons[0].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 1
                        elif img == "bottom2.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[1]}")
                                await buttons[1].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 2
                        elif img == "bottom3.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[2]}")
                                await buttons[2].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 3
                        elif img == "bottom4.png":
                            if isbutton(cid):
                                dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[3]}")
                                await buttons[3].click()
                                await self.afterclick()
                            else:
                                self.messageid = message.id
                                self.important = 4
        if re.search(
                f'<@{str(self.user.id)}> took the \*\*.*\*\* card `.*`!|<@{str(self.user.id)}> fought off .* and took the \*\*.*\*\* card `.*`!',
                message.content):
            a = re.search(f'<@{str(self.user.id)}>.*took the \*\*(.*)\*\* card `(.*)`!', message.content)
            self.timer += 540
            self.missed -= 1
            self.collected += 1
            tprint(f"{Fore.BLUE}Obtained Card: {Fore.LIGHTMAGENTA_EX}{a.group(1)}{Fore.RESET}")
            if logcollection:
                with open("log.txt", "a") as ff:
                    if timestamp:
                        ff.write(f"{current_time()} - Card: {a.group(1)} - {self.url}\n")
                    else:
                        ff.write(f"Card: {a.group(1)} - {self.url}\n")

    async def on_reaction_add(self, reaction, user):
        if str(user.id) == '646937666251915264':
            if reaction.message.id == self.messageid:
                try:
                    if self.important == 1:
                        await reaction.message.add_reaction("1️⃣")
                    elif self.important == 2:
                        await reaction.message.add_reaction("2️⃣")
                    elif self.important == 3:
                        await reaction.message.add_reaction("3️⃣")
                    elif self.important == 4:
                        await reaction.message.add_reaction("4️⃣")
                except discord.errors.Forbidden:
                    return
                if self.react:
                    self.timer += 60
                    self.missed += 1
                dprint(f"{Fore.BLUE}Reacted with {Fore.LIGHTMAGENTA_EX}{self.important} successfully{Fore.RESET}")
                self.react = False

    async def cooldown(self):
        for a in range(10000000):
            if self.timer > 0:
                self.timer -= 1
                await asyncio.sleep(1)
                Popen(f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                      f"cooldown for {self.timer} seconds", shell=True)
            else:
                await asyncio.sleep(1)
                Popen(f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Ready", shell=True)

    async def update_files(self):
        with open("keywords\\characters.txt") as ff:
            self.chars = ff.read().splitlines()

        with open("keywords\\animes.txt") as ff:
            self.animes = ff.read().splitlines()

        with open("keywords\\aniblacklist.txt") as ff:
            self.aniblacklist = ff.read().splitlines()

        with open("keywords\\charblacklist.txt") as ff:
            self.charblacklist = ff.read().splitlines()
        tprint(
            f"{Fore.MAGENTA}Loaded {len(self.animes)} animes, {len(self.aniblacklist)} blacklisted animes, {len(self.chars)} characters, {len(self.charblacklist)} blacklisted characters")

    async def filewatch(self, path):
        bruh = api.FileWatch(path)
        while True:
            await asyncio.sleep(1)
            if bruh.watch():
                await self.update_files()

    async def autodrop(self):
        channel = self.get_channel(autodropchannel)
        while True:
            await asyncio.sleep(dropdelay + random.randint(randmin, randmax))
            if self.timer == 0:
                async with channel.typing():
                    await asyncio.sleep(random.uniform(0.2, 1))
                await channel.send("kd")
                tprint(f"{Fore.LIGHTWHITE_EX}Auto Dropped Cards")
            else:
                await asyncio.sleep(self.timer + random.randint(10, 60))
                async with channel.typing():
                    await asyncio.sleep(random.uniform(0.2, 1))
                await channel.send("kd")
                tprint(f"{Fore.LIGHTWHITE_EX}Auto Dropped Cards")

    async def afterclick(self):
        dprint(f"Clicked on Button")
        self.timer += 60
        self.missed += 1
        self.react = False


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def isbutton(data):
    if data in [776520559621570621, 648044573536550922]:
        dprint(f"{Fore.LIGHTGREEN_EX}Button Detected - {data}")
        return True
    else:
        dprint(f"{Fore.RED}Not a button channel - {data}")
        return False


def tprint(message):
    if timestamp:
        print(f"{Fore.LIGHTBLUE_EX}{current_time()} - {Fore.RESET}{message}")
    else:
        print(message)


def dprint(message):
    if debug:
        tprint(f"{Fore.LIGHTRED_EX}Debug{Fore.BLUE} - {message}")


def update_check():
    return requests.get(url=update_url).text


if token == "":
    inp = input(f"{Fore.RED}No token found, would you like to find tokens from your pc? (y/n): {Fore.RESET}")
    if inp == "y":
        tokens = api.get_tokens()
        for i in tokens:
            print(f"{Fore.LIGHTBLUE_EX}{i}{Fore.RESET}")
        exit()

client = Main()
tprint(f"{Fore.GREEN}Starting Bot{Fore.RESET}")
try:
    client.run(token)
except KeyboardInterrupt:
    tprint(f"{Fore.RED}Ctrl-C detected\nExiting...{Fore.RESET}")
    client.close()
    exit()
