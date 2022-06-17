import asyncio
import json
import re
import time
from datetime import datetime
from os import listdir, system, get_terminal_size, stat
from os.path import isfile, join
import discord
import pytesseract
import requests
from PIL import Image
from colorama import Fore, init
import api
from ocr import get_card, get_bottom, get_top

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
path_to_ocr = "temp"
v = "v1.0.1"
update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/master/version.txt"
with open("config.json") as f:
    config = json.load(f)
    token = config["token"]
    channels = config["channels"]
    accuracy = float(config["accuracy"])
    loghits = config["log_hits"]
    logcollection = config["log_collection"]
    timestamp = config["timestamp"]
    update = config["update_check"]


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

    async def on_ready(self):
        system("cls")
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
        await self.update_files()
        self.ready = True
        asyncio.get_event_loop().create_task(self.cooldown())
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\animes.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\characters.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\aniblacklist.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\charblacklist.txt"))

    async def on_message(self, message):
        if not self.ready:
            return

        if str(message.author.id) != '646937666251915264':
            return

        if str(message.channel.id) not in channels:
            return

        # print(message.content)

        if re.search(match, message.content):
            if self.timer != 0:
                return

            with open("temp\\card.webp", "wb") as file:
                file.write(requests.get(message.attachments[0].url).content)
            for a in range(0, 3):
                get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)
                get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)
                get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)

            for a in range(0, 3):
                get_top(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\top{a + 1}.png")
                get_bottom(f"{path_to_ocr}\\card{a + 1}.png", f"{path_to_ocr}\\char\\bottom{a + 1}.png")

            onlyfiles = [ff for ff in listdir("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char") if
                         isfile(join("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char", ff))]
            # print("File trovati: ", onlyfiles)
            custom_config = r'--psm 6 --oem 3 -c ' \
                            r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' \
                            r'@&0123456789/:- " '
            for img in onlyfiles:
                char = pytesseract.image_to_string(Image.open(path_to_ocr + '\\char\\' + img), lang='eng',
                                                   config=custom_config).strip()
                for a in self.chars:
                    if api.isSomething(char, a, accuracy) and char not in self.charblacklist:
                        tprint(f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{char}{Fore.RESET}")
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                ff.write(f"{current_time()} - Character: {char} - {self.url}\n")
                        if img == "top1.png":
                            self.messageid = message.id
                            self.important = 1
                        elif img == "top2.png":
                            self.messageid = message.id
                            self.important = 2
                        elif img == "top3.png":
                            self.messageid = message.id
                            self.important = 3
                for a in self.animes:
                    if api.isSomething(char, a, accuracy) and char not in self.aniblacklist:
                        tprint(f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char}{Fore.RESET}")
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                ff.write(f"{current_time()} - Anime: {char} - {self.url}\n")
                        if img == "bottom1.png":
                            self.messageid = message.id
                            self.important = 1
                        elif img == "bottom2.png":
                            self.messageid = message.id
                            self.important = 2
                        elif img == "bottom3.png":
                            self.messageid = message.id
                            self.important = 3
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
                    ff.write(f"{current_time()} - Card: {a.group(1)} - {self.url}\n")

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
                    # elif self.important == 4:
                    #     await reaction.message.add_reaction("4️⃣")
                except discord.errors.Forbidden:
                    return
                if self.react:
                    self.timer += 60
                    self.missed += 1
                self.react = False

    async def cooldown(self):
        for a in range(10000000):
            if self.timer > 0:
                self.timer -= 1
                await asyncio.sleep(1)
                system(f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                       f"Cooldown: {self.timer} seconds")
            else:
                await asyncio.sleep(1)
                system(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Ready")

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


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def tprint(message):
    if timestamp:
        print(f"{Fore.LIGHTBLUE_EX}{current_time()} - {Fore.RESET}{message}")
    else:
        print(message)


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
tprint(f"{Fore.GREEN}Starting Bot - This might take up to a minute{Fore.RESET}")
client.run(token)
