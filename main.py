import asyncio
import json
import random
import re
from datetime import datetime
from os import listdir, get_terminal_size
from os.path import isfile, join
from subprocess import Popen

import discord
import pytesseract
import requests
from PIL import Image
from colorama import Fore, init

import api
from ocr import get_card, get_bottom, get_top, get_print, filelength

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
path_to_ocr = "temp"
v = "b2.0"
if "v" in v:
    update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/master/version.txt"
else:
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
cprint = config["check_print"]
if cprint:
    pn = int(config["print_number"])
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
        self.current_card = None
        self.ready = False
        self.react = True
        self.timer = 0
        self.url = None
        self.missed = 0
        self.collected = 0
        self.cardnum = 0
        self.buttons = None

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
        for line in thing.split("\n"):
            print(line.center(get_terminal_size().columns))
        print(Fore.LIGHTMAGENTA_EX + "─" * get_terminal_size().columns)
        tprint(
            f"{Fore.BLUE}Logged in as {Fore.RED}{self.user.name}#{self.user.discriminator} {Fore.GREEN}({self.user.id}){Fore.RESET}"
        )
        latest_ver = update_check().strip()
        if latest_ver != v:
            tprint(
                f"{Fore.RED}You are on version {v}, while the latest version is {latest_ver}"
            )
        tprint(f"{Fore.LIGHTRED_EX}Public Announcement: Scorpion#0001 is a skid who is selling this for money dont trust him lmao")
        dprint(f"discord.py-self version {discord.__version__}")
        dprint(f"Tesseract version {pytesseract.get_tesseract_version()}")
        await self.update_files()
        self.ready = True
        asyncio.get_event_loop().create_task(self.cooldown())
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\animes.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\characters.txt"))
        asyncio.get_event_loop().create_task(
            self.filewatch("keywords\\aniblacklist.txt")
        )
        asyncio.get_event_loop().create_task(
            self.filewatch("keywords\\charblacklist.txt")
        )
        if autodrop:
            asyncio.get_event_loop().create_task(self.autodrop())

    async def on_message(self, message):
        if (
                not self.ready
                or str(message.author.id) != "646937666251915264"
                or str(message.channel.id) not in channels
        ):
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
                    get_top(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\top{a + 1}.png",
                    )
                    get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png",
                    )
                    if cprint:
                        get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png",
                        )
            else:
                self.cardnum = 4
                for a in range(4):
                    get_card(f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a)

                for a in range(4):
                    get_top(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\top{a + 1}.png",
                    )
                    get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png",
                    )
                    if cprint:
                        get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png",
                        )

            onlyfiles = [
                ff for ff in listdir("temp\\char") if isfile(join("temp\\char", ff))
            ]
            # print("File trovati: ", onlyfiles)
            custom_config = (
                r"--psm 7 --oem 3 -c "
                r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                r'@&0123456789/:- " '
            )

            def check(reaction, user):
                # dprint(f"rmid - {reaction.message.id} | mid - {message.id}")
                return reaction.message.id == message.id

            def mcheck(before, after):
                if before.id == message.id:
                    self.buttons = after.components[0].children
                    return True
                else:
                    return False

            for img in onlyfiles:
                if "4" in img and self.cardnum != 4:
                    continue
                char = pytesseract.image_to_string(
                    Image.open(path_to_ocr + "\\char\\" + img),
                    lang="eng",
                    config=custom_config,
                ).strip()
                for a in self.chars:
                    if (
                            api.isSomething(char, a, accuracy)
                            and char not in self.charblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{char}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Character: {char} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Character: {char} - {self.url}\n")
                        if img == "top1.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[0].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "1️⃣")
                        elif img == "top2.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[1]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[1].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "2️⃣")
                        elif img == "top3.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[2]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[2].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "3️⃣")
                        elif img == "top4.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[3]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[3].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "4️⃣")
                for a in self.animes:
                    if (
                            api.isSomething(char, a, accuracy)
                            and char not in self.aniblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Anime: {char} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Anime: {char} - {self.url}\n")
                        if img == "bottom1.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[0].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "1️⃣")
                        elif img == "bottom2.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[1]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[1].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "2️⃣")
                        elif img == "bottom3.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[2]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[2].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "3️⃣")
                        elif img == "bottom4.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[3]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[3].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "4️⃣")
                if cprint and "print" in img:
                    if char == "":
                        return
                    try:
                        num = int(re.sub("\D", "", re.sub("-.*\d|-", "", char)))
                    except ValueError:
                        num = 999999
                        dprint(f"ValueError - current string: {char}")
                    # dprint(char + " - " + str(num))
                    if (
                            num <= pn
                            and num not in self.aniblacklist
                            and char not in self.charblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Print #: {Fore.MAGENTA}{num}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.current_card = char
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Print Number: {char} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Print Number: {char} - {self.url}\n")
                        if img == "print1.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[0].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "1️⃣")
                        elif img == "print2.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[1]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[1].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "2️⃣")
                        elif img == "print3.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[2]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[2].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "3️⃣")
                        elif img == "print4.png":
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[3]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[3].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.react_add(reaction, "4️⃣")
        if re.search(
                f"<@{str(self.user.id)}> took the \*\*.*\*\* card `.*`!|<@{str(self.user.id)}> fought off .* and took the \*\*.*\*\* card `.*`!",
                message.content,
        ):
            a = re.search(
                f"<@{str(self.user.id)}>.*took the \*\*(.*)\*\* card `(.*)`!",
                message.content,
            )
            self.timer += 540
            self.missed -= 1
            self.collected += 1
            tprint(
                f"{Fore.BLUE}Obtained Card: {Fore.LIGHTMAGENTA_EX}{a.group(1)}{Fore.RESET}"
            )
            if logcollection:
                with open("log.txt", "a") as ff:
                    if timestamp:
                        ff.write(
                            f"{current_time()} - Card: {a.group(1)} - {self.url}\n"
                        )
                    else:
                        ff.write(f"Card: {a.group(1)} - {self.url}\n")

    async def react_add(self, reaction, emoji):
        reaction, _ = reaction
        try:
            await asyncio.sleep(random.uniform(0.3, 1.3))
            await reaction.message.add_reaction(emoji)
        except discord.errors.Forbidden:
            return
        if self.react:
            self.timer += 60
            self.missed += 1
        dprint(f"{Fore.BLUE}Reacted with {emoji} successfully{Fore.RESET}")
        self.react = False

    async def cooldown(self):
        for a in range(10000000):
            if self.timer > 0:
                self.timer -= 1
                await asyncio.sleep(1)
                Popen(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                    f"cooldown for {self.timer} seconds",
                    shell=True,
                )
            else:
                await asyncio.sleep(1)
                Popen(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Ready",
                    shell=True,
                )

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
            f"{Fore.MAGENTA}Loaded {len(self.animes)} animes, {len(self.aniblacklist)} blacklisted animes, {len(self.chars)} characters, {len(self.charblacklist)} blacklisted characters"
        )

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
    if data == 648044573536550922:
        dprint(f"{Fore.LIGHTGREEN_EX}Button Detected - karuta-main-1")
        return True
    elif data == 776520559621570621:
        dprint(f"{Fore.LIGHTGREEN_EX}Button Detected - karuta-main-2")
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
    inp = input(
        f"{Fore.RED}No token found, would you like to find tokens from your pc? (y/n): {Fore.RESET}"
    )
    if inp == "y":
        tokens = api.get_tokens(False)
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
