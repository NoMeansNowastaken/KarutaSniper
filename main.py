import asyncio
import json
import os
import random
import re
import sys
from datetime import datetime
from os import listdir, get_terminal_size
from os.path import isfile, join

import discord
import pytesseract
import requests
from colorama import Fore, init

from lib import api
from lib.ocr import *

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
path_to_ocr = "temp"
v = "v2.2.1"
if "v" in v:
    beta = False
    update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/master/version.txt"
else:
    beta = True
    update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/beta/version.txt"
with open("config.json") as f:
    config = json.load(f)

if os.name == 'nt':
    title = True
else:
    title = False

token = config["token"]
channels = config["channels"]
accuracy = float(config["accuracy"])
blaccuracy = float(config["blaccuracy"])
loghits = config["log_hits"]
logcollection = config["log_collection"]
timestamp = config["timestamp"]
update = config["update_check"]
autodrop = config["autodrop"]
debug = config["debug"]
cprint = config["check_print"]
autofarm = config["autofarm"]
christmas = config["christmas"]
tofu_enabled = config["tofu"]["enabled"]
verbose = config["very_verbose"]
if autofarm:
    resourcechannel = config["resourcechannel"]
if cprint:
    pn = int(config["print_number"])
if autodrop:
    autodropchannel = config["autodropchannel"]
    dropdelay = config["dropdelay"]
    randmin = int(config["randmin"])
    randmax = int(config["randmax"])
if tofu_enabled:
    tofu_config = config["tofu"]
    tofu_channels = tofu_config["channels"]
    shouldsummon = tofu_config["summon"]
    tcc = tofu_config["tcc"]
    if shouldsummon:
        summonchannel = tofu_config["summon_channel"]
        tofu_delay = tofu_config["dropdelay"]
        tofu_min = tofu_config["randmin"]
        tofu_max = tofu_config["randmax"]
        grandom = tofu_config["grab_random"]
    tofu_cprint = tofu_config["check_print"]


class Main(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.charblacklist = None
        self.aniblacklist = None
        self.animes = None
        self.chars = None
        self.messageid = None
        self.current_card = None
        self.ready = False
        self.timer = 0
        self.url = None
        self.missed = 0
        self.collected = 0
        self.cardnum = 0
        self.buttons = None
        self.tofutimer = 0
        if tofu_enabled:
            self.tofu_current_card = None
            self.tofureact = False
            self.tofuurl = None
            self.tofubuttons = None
            self.tcc = tcc
        if autofarm:
            self.button = None

    async def on_ready(self):
        if title:
            await asyncio.create_subprocess_shell("cls")
        else:
            await asyncio.create_subprocess_shell("clear")
        await asyncio.sleep(0.5)
        thing = f"""{Fore.LIGHTMAGENTA_EX}
 ____  __.                    __             _________      .__                     
|    |/ _|____ _______ __ ___/  |______     /   _____/ ____ |__|_____   ___________ 
|      < \__  \\\\_  __ \  |  \   __\__  \    \_____  \ /    \|  \____ \_/ __ \_  __ \\
|    |  \ / __ \|  | \/  |  /|  |  / __ \_  /        \   |  \  |  |_> >  ___/|  | \/
|____|__ (____  /__|  |____/ |__| (____  / /_______  /___|  /__|   __/ \___  >__|   
        \/    \/                       \/          \/     \/   |__|        \/       
"""
        if sys.gettrace() is None:
            for line in thing.split("\n"):
                print(line.center(get_terminal_size().columns))
            print(Fore.LIGHTMAGENTA_EX + "─" * get_terminal_size().columns)
        tprint(
            f"{Fore.BLUE}Logged in as {Fore.RED}{self.user.name}#{self.user.discriminator} {Fore.GREEN}({self.user.id}){Fore.RESET} "
        )
        latest_ver = update_check().strip()
        if latest_ver != v:
            tprint(
                f"{Fore.RED}You are on version {v}, while the latest version is {latest_ver}"
            )
        if not christmas:
            tprint(f"{Fore.GREEN}Note: Christmas event off by default, set christmas to true in config if you want "
                   f"it to grab bows (experimental feature, use at your own risk)")
        dprint(f"discord.py-self version {discord.__version__}")
        dprint(f"Tesseract version {pytesseract.get_tesseract_version()}")
        if beta:
            tprint(f"{Fore.RED}[!] You are on the beta branch, please report all actual issues to the github repo")
        await self.update_files()
        dprint(f"Tofu Status: {tofu_enabled}")
        asyncio.get_event_loop().create_task(self.cooldown())
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\animes.txt"))
        asyncio.get_event_loop().create_task(self.filewatch("keywords\\characters.txt"))
        asyncio.get_event_loop().create_task(
            self.filewatch("keywords\\aniblacklist.txt")
        )
        asyncio.get_event_loop().create_task(
            self.configwatch("config.json")
        )
        asyncio.get_event_loop().create_task(
            self.filewatch("keywords\\charblacklist.txt")
        )
        if autodrop:
            asyncio.get_event_loop().create_task(self.autodrop())
        if tofu_enabled:
            if shouldsummon:
                asyncio.get_event_loop().create_task(self.summon())
        self.ready = True

    async def on_reaction_add(self, reaction, user):
        if not self.ready or user.id != 646937666251915264 or reaction.message.channel.id not in channels:
            return
        if str(reaction.emoji) == "🎀" and christmas:
            dprint("Ribbon Detected")
            await asyncio.sleep(random.uniform(0.1, 0.74))
            await reaction.message.add_reaction(reaction.emoji)
            tprint("Clicked on a ribbon")

    async def on_message(self, message):
        cid = message.channel.id
        if self.ready and tofu_enabled and message.author.id == 792827809797898240:
            await asyncio.get_event_loop().create_task(self.tofu(message))
            return
        if (
                not self.ready
                or message.author.id != 646937666251915264
                or cid not in channels
        ):
            return

        def mcheck(before, after):
            if before.id == message.id:
                dprint("Message edit found")
                try:
                    self.buttons = after.components[0].children
                    return True
                except IndexError:
                    dprint(f"Fuck - {after.components}")
            else:
                return False

        def check(reaction, user):
            return reaction.message.id == message.id

        if isbutton(cid) and christmas:
            if message.components:
                buttons = message.components[0].children
                if len(buttons) == 4 and buttons[3].emoji == "🎀":
                    dprint("Ribbon Detected")
                    await self.wait_for("message_edit", check=mcheck)
                    await buttons[3].click()
                    tprint("Clicked on a ribbon")

        if re.search("A wishlisted card is dropping!", message.content):
            dprint("Whishlisted card detected")  # TODO: guess which card is the wishlisted one

        if re.search(match, message.content):
            if self.timer != 0:
                return

            with open("temp\\card.webp", "wb") as file:
                file.write(requests.get(message.attachments[0].url).content)
            if filelength("temp\\card.webp") == 836:
                self.cardnum = 3
                for a in range(3):
                    await get_card(
                        f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a
                    )

                for a in range(3):
                    await get_top(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\top{a + 1}.png"
                    )
                    await get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png"
                    )
                    if cprint:
                        await get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png"
                        )
            else:
                self.cardnum = 4
                for a in range(4):
                    await get_card(
                        f"{path_to_ocr}\\card{a + 1}.png", "temp\\card.webp", a
                    )

                for a in range(4):
                    await get_top(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\top{a + 1}.png"
                    )
                    await get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png"
                    )
                    if cprint:
                        await get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png"
                        )

            onlyfiles = [
                ff for ff in listdir("temp\\char") if isfile(join("temp\\char", ff))
            ]
            charlist = []
            anilist = []
            printlist = []
            for img in onlyfiles:
                if "4" in img and self.cardnum != 4:
                    continue
                if "top" in img:
                    custom_config = (
                        r"--psm 6 --oem 3 -c "
                        r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                        r'@&0123456789/:- " '
                    )
                    charlist.append(
                        pytesseract.image_to_string(
                            Image.open(
                                path_to_ocr
                                + "\\char\\top"
                                + re.sub(r"\D", "", img)
                                + ".png"
                            ),
                            lang="eng",
                            config=custom_config
                        )
                        .strip()
                        .replace("\n", " ")
                    )
                elif "bottom" in img:
                    custom_config = (
                        r"--psm 6 --oem 3 -c "
                        r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                        r'@&0123456789/:- " '
                    )
                    anilist.append(
                        pytesseract.image_to_string(
                            Image.open(
                                path_to_ocr
                                + "\\char\\bottom"
                                + re.sub(r"\D", "", img)
                                + ".png"
                            ),
                            lang="eng",
                            config=custom_config
                        )
                        .strip()
                        .replace("\n", " ")
                    )
                elif cprint and "print" in img:
                    custom_config = (
                        r'--psm 7 --oem 3 -c tessedit_char_whitelist="0123456789 "'
                    )
                    printlist.append(
                        pytesseract.image_to_string(
                            Image.open(path_to_ocr + f"\\char\\{img}"),
                            lang="eng",
                            config=custom_config
                        ).strip()
                    )
            vprint(f"Anilist: {anilist}")
            vprint(f"Charlist: {charlist}")
            vprint(f"Printlist: {printlist}")

            def emoji(i):
                match i:
                    case 0:
                        return "1️⃣"
                    case 1:
                        return "2️⃣"
                    case 2:
                        return "3️⃣"
                    case 3:
                        return "4️⃣"

            for i, character in enumerate(charlist):
                if (
                        api.isSomething(character, self.chars, accuracy)
                        and not api.isSomething(character, self.charblacklist, accuracy)
                        and not api.isSomething(anilist[i], self.aniblacklist, blaccuracy)
                ):
                    tprint(
                        f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{character} {Fore.LIGHTMAGENTA_EX}from {Fore.LIGHTBLUE_EX}{anilist[i]}{Fore.RESET}"
                    )
                    self.url = message.attachments[0].url
                    if loghits:
                        with open("log.txt", "a") as ff:
                            if timestamp:
                                ff.write(
                                    f"{current_time()} - Character: {character} - {self.url}\n"
                                )
                            else:
                                ff.write(f"Character: {character} - {self.url}\n")
                    if isbutton(cid):
                        # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                        await self.wait_for("message_edit", check=mcheck)
                        await self.buttons[i].click()
                        await self.afterclick()
                    else:
                        reaction = await self.wait_for(
                            "reaction_add", check=check
                        )
                        await self.react_add(reaction, emoji(i))
            for i, anime in enumerate(anilist):
                if (
                        api.isSomething(anime, self.animes, accuracy)
                        and not api.isSomething(charlist[i], self.charblacklist, accuracy)
                        and not api.isSomething(anime, self.aniblacklist, blaccuracy)
                ):
                    tprint(
                        f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{anime} {Fore.LIGHTMAGENTA_EX}| {Fore.LIGHTBLUE_EX}{charlist[i]}{Fore.RESET}"
                    )
                    self.url = message.attachments[0].url
                    if loghits:
                        with open("log.txt", "a") as ff:
                            if timestamp:
                                ff.write(
                                    f"{current_time()} - Anime: {anime} - {self.url}\n"
                                )
                            else:
                                ff.write(f"Anime: {anime} - {self.url}\n")
                    if isbutton(cid):
                        # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                        await self.wait_for("message_edit", check=mcheck)
                        await self.buttons[i].click()
                        await self.afterclick()
                    else:
                        reaction = await self.wait_for(
                            "reaction_add", check=check
                        )
                        await self.react_add(reaction, emoji(i))
            if cprint:
                for i, prin in enumerate(printlist):
                    try:
                        prin = int(re.sub(" \d$| ", "", prin))
                    except ValueError:
                        prin = 999999
                        dprint(f"ValueError - current string: {prin}")
                    if (
                            prin <= pn
                            and anilist[i] not in self.aniblacklist
                            and charlist[i] not in self.charblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Print # {Fore.MAGENTA}{prin}{Fore.RESET}"
                        )
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Print Number {prin} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Print Number {prin} - {self.url}\n")
                        if isbutton(cid):
                            # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                            await self.wait_for("message_edit", check=mcheck)
                            await self.buttons[i].click()
                            await self.afterclick()
                        else:
                            reaction = await self.wait_for(
                                "reaction_add", check=check
                            )
                            await self.react_add(reaction, emoji(i))
        elif re.search(
                f"<@{str(self.user.id)}> took the \*\*.*\*\* card `.*`!|<@{str(self.user.id)}> fought off .* and took the \*\*.*\*\* card `.*`!",
                message.content
        ):
            a = re.search(
                f"<@{str(self.user.id)}>.*took the \*\*(.*)\*\* card `(.*)`!",
                message.content
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

    async def tofu(self, message):
        cid = message.channel.id
        if cid not in tofu_channels:
            return

        tofu_match = r"(<@(\d*)> is summoning 2 cards!)|(Server activity has summoned)"
        cool = re.search(tofu_match, message.content)
        if cool:
            if self.tofutimer != 0:
                return

            with open("temp\\tofu\\card.webp", "wb") as file:
                file.write(requests.get(message.attachments[0].url).content)
            if filelength("temp\\tofu\\card.webp") == 940:
                for a in range(2):
                    await tofu_get_card(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png", "temp\\tofu\\card.webp", a)

                for a in range(2):
                    await tofu_get_top(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                        f"{path_to_ocr}\\tofu\\char\\top{a + 1}.png")
                    await tofu_get_bottom(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                        f"{path_to_ocr}\\tofu\\char\\bottom{a + 1}.png")
                    if tofu_cprint:
                        await tofu_get_print(
                            f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                            f"{path_to_ocr}\\tofu\\char\\print{a + 1}.png")

            onlyfiles = [
                ff for ff in listdir("temp\\tofu\\char") if isfile(join("temp\\tofu\\char", ff))
            ]
            anilist = []
            charlist = []
            printlist = []
            def check(reaction, user):
                return reaction.message.id == message.id

            def mcheck(before, after):
                if before.id == message.id:
                    dprint("Message edit found")
                    try:
                        self.tofubuttons = after.components[0].children
                        return True
                    except IndexError:
                        pass  # i think its a library issue
                else:
                    return False

            for img in onlyfiles:
                if "top" in img:
                    charlist.append(
                        pytesseract.image_to_string(
                            Image.open(
                                path_to_ocr
                                + "\\tofu\\char\\top"
                                + re.sub(r"\D", "", img)
                                + ".png"
                            ),
                            lang="eng",
                            config=self.tcc
                        )
                        .strip()
                        .replace("\n", " ")
                    )
                elif "bottom" in img:
                    anilist.append(
                        pytesseract.image_to_string(
                            Image.open(
                                path_to_ocr
                                + "\\tofu\\char\\bottom"
                                + re.sub(r"\D", "", img)
                                + ".png"
                            ),
                            lang="eng",
                            config=self.tcc
                        )
                        .strip()
                        .replace("\n", " ")
                    )
                elif tofu_cprint and "print" in img:
                    custom_config = (
                        r'--psm 8 --oem 3 -c tessedit_char_whitelist="0123456789"'
                    )
                    printlist.append(
                        pytesseract.image_to_string(
                            Image.open(path_to_ocr + f"\\tofu\\char\\{img}"),
                            lang="eng",
                            config=custom_config
                        ).strip()
                    )
            vprint(f"Tofu Anilist: {anilist}")
            vprint(f"Tofu Charlist: {charlist}")
            vprint(f"Tofu Printlist: {printlist}")

            def emoji(i):
                match i:
                    case 0:
                        return "1️⃣"
                    case 1:
                        return "2️⃣"
                    case 2:
                        return "3️⃣"
                    case 3:
                        return "4️⃣"

            for i, character in enumerate(charlist):
                if (
                        api.isSomething(character, self.chars, accuracy)
                        and not api.isSomething(character, self.charblacklist, accuracy)
                        and not api.isSomething(anilist[i], self.aniblacklist, blaccuracy)
                ):
                    tprint(
                        f"{Fore.GREEN}[Tofu] Found Character: {Fore.MAGENTA}{character} {Fore.LIGHTMAGENTA_EX}from {Fore.LIGHTBLUE_EX}{anilist[i]}{Fore.RESET}"
                    )
                    self.tofuurl = message.attachments[0].url
                    if loghits:
                        with open("log.txt", "a") as ff:
                            if timestamp:
                                ff.write(
                                    f"{current_time()} - [Tofu] Character: {character} - {self.url}\n"
                                )
                            else:
                                ff.write(f"[Tofu] Character: {character} - {self.url}\n")
                    if isbutton(cid):
                        # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                        await self.wait_for("message_edit", check=mcheck)
                        await self.buttons[i].click()
                        await self.tofuafterclick()
                    else:
                        reaction = await self.wait_for(
                            "reaction_add", check=check
                        )
                        await self.tofu_react_add(reaction, emoji(i))
            for i, anime in enumerate(anilist):
                if (
                        api.isSomething(anime, self.animes, accuracy)
                        and not api.isSomething(charlist[i], self.charblacklist, accuracy)
                        and not api.isSomething(anime, self.aniblacklist, blaccuracy)
                ):
                    tprint(
                        f"{Fore.GREEN}[Tofu] Found Anime: {Fore.MAGENTA}{anime} {Fore.LIGHTMAGENTA_EX}| {Fore.LIGHTBLUE_EX}{charlist[i]}{Fore.RESET}"
                    )
                    self.url = message.attachments[0].url
                    if loghits:
                        with open("log.txt", "a") as ff:
                            if timestamp:
                                ff.write(
                                    f"{current_time()} - [Tofu] Anime: {anime} - {self.url}\n"
                                )
                            else:
                                ff.write(f"[Tofu] Anime: {anime} - {self.url}\n")
                    if isbutton(cid):
                        # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                        await self.wait_for("message_edit", check=mcheck)
                        await self.buttons[i].click()
                        await self.tofuafterclick()
                    else:
                        reaction = await self.wait_for(
                            "reaction_add", check=check
                        )
                        await self.tofu_react_add(reaction, emoji(i))
                if tofu_cprint:
                    for i, prin in enumerate(printlist):
                        try:
                            prin = int(prin)
                        except ValueError:
                            if prin != "":
                                dprint(f"[Tofu] ValueError - current string: {prin}")
                            prin = 999999
                        if (
                                prin <= pn
                                and anilist[i] not in self.aniblacklist
                                and charlist[i] not in self.charblacklist
                        ):
                            tprint(
                                f"{Fore.GREEN}[Tofu] Found Print # {Fore.MAGENTA}{prin}{Fore.RESET}"
                            )
                            self.tofuurl = message.attachments[0].url
                            if loghits:
                                with open("log.txt", "a") as ff:
                                    if timestamp:
                                        ff.write(
                                            f"{current_time()} - [Tofu] Print Number {prin} - {self.url}\n"
                                        )
                                    else:
                                        ff.write(f"[Tofu] Print Number {prin} - {self.url}\n")
                            if isbutton(cid):
                                # dprint(f"{Fore.LIGHTRED_EX}Button Data: {buttons[0]}")
                                await self.wait_for("message_edit", check=mcheck)
                                await self.buttons[i].click()
                                await self.tofuafterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, emoji(i))
            if cool.group(2) == str(self.user.id) and grandom and not self.tofureact:
                self.tofureact = True
                self.tofuurl = ""
                tprint(f"{Fore.LIGHTMAGENTA_EX}[Tofu] No cards found, defaulting to random")
                if isbutton(cid):
                    await self.wait_for("message_edit", check=mcheck)
                    await self.tofubuttons[3].click()
                    await self.tofuafterclick()
                else:
                    self.missed += 1
                    reaction = await self.wait_for(
                        "reaction_add", check=check)
                    await self.tofu_react_add(reaction, "❓")
        elif re.search(
                f"<@{str(self.user.id)}> grabbed a \*\*Fusion",
                message.content):
            self.tofutimer += 540
            self.missed -= 1
            self.collected += 1
            tprint(
                f"{Fore.BLUE}[Tofu] Obtained Fusion Token{Fore.RESET}"
            )
            if logcollection:
                with open("log.txt", "a") as ff:
                    if timestamp:
                        ff.write(
                            f"{current_time()} - Fusion Token - {self.tofuurl}\n"
                        )
                    else:
                        ff.write(f"Fusion Token - {self.tofuurl}\n")
        elif re.search(
                f"<@{str(self.user.id)}> grabbed .* |<@{str(self.user.id)}> fought off .* ",
                message.content):
            a = re.search(
                f"<@{str(self.user.id)}> .*:(.*):.*#(.*)` · (.*) · \*\*(.*)\*\*",
                message.content)
            self.tofutimer += 540
            self.missed -= 1
            self.collected += 1
            tprint(
                f"{Fore.BLUE}[Tofu] Obtained Card: {Fore.LIGHTMAGENTA_EX}{a.group(4)} from {a.group(3)} | Print #{a.group(2)} | "
                f"Condition: {a.group(1)}{Fore.RESET} ")
            if logcollection:
                with open("log.txt", "a") as ff:
                    if timestamp:
                        ff.write(
                            f"{current_time()} - Tofu Card: {a.group(4)} from {a.group(3)} - {self.tofuurl}\n"
                        )
                    else:
                        ff.write(f"Tofu Card: {a.group(4)} from {a.group(3)}- {self.tofuurl}\n")

    async def react_add(self, reaction, emoji):
        reaction, _ = reaction
        try:
            dprint(f"{Fore.BLUE}Attempting to react")
            await asyncio.sleep(random.uniform(0.55, 1.08))
            await reaction.message.add_reaction(emoji)
        except discord.errors.Forbidden as oopsie:
            dprint(f"{Fore.RED}Fuck:\n{oopsie}")
            return
        self.timer += 60
        self.missed += 1
        dprint(f"{Fore.BLUE}Reacted with {emoji} successfully{Fore.RESET}")

    async def tofu_react_add(self, reaction, emoji):
        reaction, _ = reaction
        try:
            dprint(f"{Fore.BLUE}[Tofu] Attempting to react")
            await asyncio.sleep(random.uniform(0.25, 0.97))
            await reaction.message.add_reaction(emoji)
        except discord.errors.Forbidden as oopsie:
            dprint(f"{Fore.RED}Fuck:\n{oopsie}")
            return
        if self.tofureact:
            self.tofutimer += 60
            self.missed += 1
        dprint(f"{Fore.BLUE}Reacted with {emoji} successfully{Fore.RESET}")
        self.tofureact = False

    async def cooldown(self):
        while True:
            await asyncio.sleep(1)
            if self.timer > 0:
                self.timer -= 1
                if self.tofutimer > 0:
                    self.tofutimer -= 1
                    if title:
                        await asyncio.create_subprocess_shell(
                            f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                            f"cooldown for {self.timer} seconds - Tofu on cooldown for {self.tofutimer} seconds"
                        )
                elif title:
                    await asyncio.create_subprocess_shell(
                        f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                        f"cooldown for {self.timer} seconds"
                    )
            elif self.tofutimer > 0:
                self.tofutimer -= 1
                if title:
                    await asyncio.create_subprocess_shell(
                        f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Tof"
                        f"u on cooldown for {self.tofutimer} seconds"
                    )
            elif title:
                await asyncio.create_subprocess_shell(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Ready"
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
            f"{Fore.MAGENTA}Loaded {len(self.animes)} animes, {len(self.aniblacklist)} blacklisted animes, "
            f"{len(self.chars)} characters, {len(self.charblacklist)} blacklisted characters")

    async def filewatch(self, path):
        bruh = api.FileWatch(path)
        dprint(f"Filewatch activated for {path}")
        while True:
            await asyncio.sleep(2)
            if bruh.watch():
                await self.update_files()

    async def configwatch(self, path):
        bruh = api.FileWatch(path)
        while True:
            await asyncio.sleep(1)
            if bruh.watch():
                with open("config.json") as ff:
                    config = json.load(ff)
                    global accuracy
                    accuracy = float(config["accuracy"])
                    self.tcc = config["tofu"]["tcc"]
                    dprint(f"Updated tcc to {self.tcc}")

    async def autofarm(self):
        channel = self.get_channel(resourcechannel)
        while True:
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("kw")
            async for message in channel.history(limit=1):
                dprint(message.content)
                if "you do not have" in message.content:
                    tprint("Autofarm - You dont have a permit")
                else:
                    matches = re.search(r"(\d+) hours", message.content)
                    match1 = re.search(r"(\d+) hour", message.content)
                    match0 = re.search(r"(\d+) minute", message.content)
                    if matches:
                        hours = int(match1.group(1))
                        tprint(f"Autofarm - Waiting for {hours} hours to work again")
                        await asyncio.sleep(hours * 3600 + 5)
                    elif match1:
                        hours = int(match1.group(1))
                        tprint(f"Autofarm - Waiting for {hours} hour to work again")
                        await asyncio.sleep(hours * 3600 + 5)
                    elif match0:
                        minutes = int(match0.group(1))
                        tprint(f"Autofarm - Waiting for {minutes} minutes to work again")
                        await asyncio.sleep(minutes * 3600 + 5)
                    else:
                        tprint("Autofarm - Processing...")
                if message is not None:
                    reply = await self.wait_for(
                        "message", check=lambda m: m.author.id == 646937666251915264
                    )
                    if reply:
                        await self.autofindresource()
                        await reply.components[0].children[1].click()
                        tprint("Autofarm - Worked successfully!")
                        await asyncio.sleep(12 * 3600 + 5)  # 12 hours

    async def autofindresource(self):
        channel = self.get_channel(resourcechannel)  # your work/auto check for resource channel
        async with channel.typing():
            await asyncio.sleep(random.uniform(0.2, 1))
        await channel.send("kn")
        reply = await client.wait_for(
            "message", check=lambda m: m.author.id == 646937666251915264)
        a = re.compile(
            "`(\w+)` · \*\*(\d+)%\*\* tax · \*\*(\d+)(%\*\* power · \*\*(\d+)|\*)",
            re.MULTILINE).findall(reply.embeds[0].to_dict()["description"].replace(",", ""))
        top = 0
        material = None
        for interest in a:
            if not interest.count("") == 1:
                if int(interest[4]) > top:
                    top = int(interest[4])
                    material = interest[0]

            else:
                top = int(interest[2])
                material = interest[0]
        async with channel.typing():
            await asyncio.sleep(random.uniform(0.9, 1.7))
        await channel.send(f"kjn abcde {material}")

    async def autodrop(self):
        channel = self.get_channel(autodropchannel)
        while True:
            await asyncio.sleep(dropdelay + random.randint(randmin, randmax))
            if self.timer != 0:
                await asyncio.sleep(self.timer)
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("kd")
            tprint(f"{Fore.LIGHTWHITE_EX}Auto Dropped Cards")

    async def summon(self):
        channel = self.get_channel(summonchannel)
        while True:
            await asyncio.sleep(tofu_delay + random.randint(tofu_min, tofu_max))
            if self.tofutimer != 0:
                await asyncio.sleep(self.tofutimer)
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("ts")
            tprint(f"{Fore.LIGHTWHITE_EX}Summoned Cards")

    async def afterclick(self):
        dprint(f"Clicked on Button")
        self.timer += 60
        self.missed += 1

    async def tofuafterclick(self):
        dprint(f"Clicked on Button")
        self.tofutimer += 60
        self.missed += 1
        self.tofureact = False


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def isbutton(data):
    if data in [648044573536550922, 776520559621570621, 858004885809922078, 857978372688445481]:
        return True
    else:
        return False


def tprint(message):
    if timestamp:
        print(f"{Fore.LIGHTBLUE_EX}{current_time()} | {Fore.RESET}{message}")
    else:
        print(message)


def dprint(message):
    if debug:
        tprint(f"{Fore.LIGHTRED_EX}Debug{Fore.BLUE} - {message}")


def vprint(message):
    if verbose:
        tprint(f"{Fore.CYAN}{message}{Fore.WHITE}")

def update_check():
    return requests.get(url=update_url).text


if token == "":
    inp = input(
        f"{Fore.RED}No token found, would you like to find tokens from your pc? (y/n): {Fore.RESET}"
    )
    if inp == "y":
        token = api.get_tokens(False)
        input("Press any key to exit...")

client = Main()
tprint(f"{Fore.GREEN}Starting Bot{Fore.RESET}")
try:
    client.run(token)
except KeyboardInterrupt:
    tprint(f"{Fore.RED}Ctrl-C detected\nExiting...{Fore.RESET}")
    client.close()
    exit()
