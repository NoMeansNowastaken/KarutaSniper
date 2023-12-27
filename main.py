import asyncio
import json
import random
import re
import sys
from datetime import datetime
from os import listdir, get_terminal_size
from os.path import isfile, join
from subprocess import Popen

import discord
import pytesseract
import requests
from colorama import Fore, init

from lib import api
from lib.ocr import *

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
tofu_match = r"(<@(\d*)> is summoning 2 cards!)|(Server activity has summoned)"
path_to_ocr = "temp"
v = "v2.1.3"
if "v" in v:
    beta = False
    update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/master/version.txt"
else:
    beta = True
    update_url = "https://raw.githubusercontent.com/NoMeansNowastaken/KarutaSniper/beta/version.txt"
with open("config.json") as f:
    config = json.load(f)

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
        self.react = True
        self.timer = 0
        self.url = None
        self.missed = 0
        self.collected = 0
        self.cardnum = 0
        self.buttons = None
        if tofu_enabled:
            self.tofutimer = 0
            self.tofu_current_card = None
            self.tofureact = True
            self.tofuurl = None
            self.tofubuttons = None
        if autofarm:
            self.button = None

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
        if str(reaction.emoji) == "🎀":
            await asyncio.sleep(random.uniform(0.1, 0.74))
            await reaction.message.add_reaction(reaction.emoji)

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
            return reaction.message.id == message.id and str(reaction) == "🎀"

        if isbutton(cid) and christmas:
            if message.components:
                buttons = message.components[0].children
                if len(buttons) == 4 and buttons[3].emoji == "🎀":
                    await self.wait_for("message_edit", check=mcheck)
                    await buttons[3].click()
                    tprint("Clicked on a ribbon")
        elif christmas:
            reaction = await self.wait_for(
                "reaction_add", check=check
            )
            await self.react_add(reaction, "🎀")
            tprint("Clicked on a ribbon")

        if re.search("(A wishlisted card is dropping!)", message.content):
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
                        f"{path_to_ocr}\\char\\top{a + 1}.png",
                    )
                    await get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png",
                    )
                    if cprint:
                        await get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png",
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
                        f"{path_to_ocr}\\char\\top{a + 1}.png",
                    )
                    await get_bottom(
                        f"{path_to_ocr}\\card{a + 1}.png",
                        f"{path_to_ocr}\\char\\bottom{a + 1}.png",
                    )
                    if cprint:
                        await get_print(
                            f"{path_to_ocr}\\card{a + 1}.png",
                            f"{path_to_ocr}\\char\\print{a + 1}.png",
                        )

            onlyfiles = [
                ff for ff in listdir("temp\\char") if isfile(join("temp\\char", ff))
            ]
            # print("File trovati: ", onlyfiles)
            custom_config = (
                r"--psm 6 --oem 3 -c "
                r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                r'@&0123456789/:- " '
            )

            for img in onlyfiles:
                if "4" in img and self.cardnum != 4:
                    continue
                charchar = (
                    pytesseract.image_to_string(
                        Image.open(
                            path_to_ocr
                            + "\\char\\top"
                            + re.sub(r"\D", "", img)
                            + ".png"
                        ),
                        lang="eng",
                        config=custom_config,
                    )
                    .strip()
                    .replace("\n", " ")
                )
                char = (
                    pytesseract.image_to_string(
                        Image.open(
                            path_to_ocr
                            + "\\char\\bottom"
                            + re.sub(r"\D", "", img)
                            + ".png"
                        ),
                        lang="eng",
                        config=custom_config,
                    )
                    .strip()
                    .replace("\n", " ")
                )
                for a in self.chars:
                    if "top" not in img:
                        break
                    if (
                            api.isSomething(charchar, a, accuracy)
                            and not api.isSomething(charchar, self.charblacklist, accuracy)
                            and not api.isSomething(char, self.aniblacklist, blaccuracy)
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{charchar} {Fore.LIGHTMAGENTA_EX}from {Fore.LIGHTBLUE_EX}{char}{Fore.RESET}"
                        )
                        self.current_card = charchar
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Character: {charchar} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Character: {charchar} - {self.url}\n")
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
                for a in self.animes:  # TODO: fix this shit its so poorly coded no need to read anime titles twice
                    if "bottom" not in img:
                        break
                    if (
                            api.isSomething(char, a, accuracy)
                            and not api.isSomething(charchar, self.charblacklist, accuracy)
                            and not api.isSomething(char, self.aniblacklist, accuracy)
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char} {Fore.LIGHTMAGENTA_EX}| {Fore.LIGHTBLUE_EX}{charchar}{Fore.RESET} "
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
                    custom_config = (
                        r'--psm 8 --oem 3 -c tessedit_char_whitelist="0123456789"'
                    )
                    coolthing = pytesseract.image_to_string(
                        Image.open(path_to_ocr + f"\\char\\{img}"),
                        lang="eng",
                        config=custom_config,
                    ).strip()
                    if coolthing == "":
                        return
                    try:
                        num = int(re.sub("\D", "", re.sub("-.*\d|-", "", coolthing)))
                    except ValueError:
                        num = 999999
                        dprint(f"ValueError - current string: {coolthing}")
                    # dprint(char + " - " + str(num))
                    if (
                            num <= pn
                            and char not in self.aniblacklist
                            and charchar not in self.charblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Print # {Fore.MAGENTA}{num}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.current_card = charchar
                        self.react = True
                        self.url = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Print Number: {coolthing} - {self.url}\n"
                                    )
                                else:
                                    ff.write(
                                        f"Print Number: {coolthing} - {self.url}\n"
                                    )
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

    async def tofu(self, message):
        cid = message.channel.id
        if cid not in tofu_channels:
            return

        cool = re.search(tofu_match, message.content)
        if cool:
            if self.tofutimer != 0:
                return

            with open("temp\\tofu\\card.webp", "wb") as file:
                file.write(requests.get(message.attachments[0].url).content)
            if filelength("temp\\tofu\\card.webp") == 940:
                for a in range(2):
                    await tofu_get_card(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png", "temp\\tofu\\card.webp", a
                    )

                for a in range(2):
                    await tofu_get_top(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                        f"{path_to_ocr}\\tofu\\char\\top{a + 1}.png",
                    )
                    await tofu_get_bottom(
                        f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                        f"{path_to_ocr}\\tofu\\char\\bottom{a + 1}.png",
                    )
                    if tofu_cprint:
                        await get_print(
                            f"{path_to_ocr}\\tofu\\card{a + 1}.png",
                            f"{path_to_ocr}\\tofu\\char\\print{a + 1}.png",
                        )

            onlyfiles = [
                ff for ff in listdir("temp\\tofu\\char") if isfile(join("temp\\tofu\\char", ff))
            ]
            custom_config = (
                r"--psm 6 --oem 3 -c "
                r'tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                r'@&0123456789/:- " '
            )

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
                charchar = (
                    pytesseract.image_to_string(
                        Image.open(
                            path_to_ocr
                            + "\\tofu\\char\\top"
                            + re.sub(r"\D", "", img)
                            + ".png"
                        ),
                        lang="eng",
                        config=custom_config,
                    )
                    .strip()
                    .replace("\n", " ")
                )
                char = (
                    pytesseract.image_to_string(
                        Image.open(
                            path_to_ocr
                            + "\\tofu\\char\\bottom"
                            + re.sub(r"\D", "", img)
                            + ".png"
                        ),
                        lang="eng",
                        config=custom_config,
                    )
                    .strip()
                    .replace("\n", " ")
                )
                for a in self.chars:
                    if "top" not in img:
                        break
                    if (
                            api.isSomething(charchar, a, accuracy)
                            and not api.isSomething(charchar, self.charblacklist, accuracy)
                            and not api.isSomething(char, self.aniblacklist, blaccuracy)
                    ):
                        tprint(
                            f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{charchar} {Fore.LIGHTMAGENTA_EX}from {Fore.LIGHTBLUE_EX}{char}{Fore.RESET}"
                        )
                        self.tofu_current_card = charchar
                        self.tofureact = True
                        self.tofuurl = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Tofu Character: {charchar} - {self.url}\n"
                                    )
                                else:
                                    ff.write(f"Tofu Character: {charchar} - {self.url}\n")
                        if img == "top1.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[0].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "1️⃣")
                        elif img == "top2.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[1].click()
                                await self.afterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "2️⃣")
                for a in self.animes:  # TODO: fix this shit its so poorly coded no need to read anime titles twice
                    if "bottom" not in img:
                        break
                    if (
                            api.isSomething(char, a, accuracy)
                            and not api.isSomething(charchar, self.charblacklist, accuracy)
                            and not api.isSomething(char, self.aniblacklist, accuracy)
                    ):
                        tprint(
                            f"{Fore.GREEN}[Tofu] Found Anime: {Fore.MAGENTA}{char} {Fore.LIGHTMAGENTA_EX}| {Fore.LIGHTBLUE_EX}{charchar}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.tofu_current_card = char
                        self.tofureact = True
                        self.tofuurl = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Tofu Anime: {char} - {self.tofuurl}\n"
                                    )
                                else:
                                    ff.write(f"Tofu Anime: {char} - {self.tofuurl}\n")
                        if img == "bottom1.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[0].click()
                                await self.tofuafterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "1️⃣")
                        elif img == "bottom2.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[1].click()
                                await self.tofuafterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "2️⃣")
                if cprint and "print" in img:
                    custom_config = (
                        r'--psm 8 --oem 3 -c tessedit_char_whitelist="0123456789"'
                    )
                    coolthing = pytesseract.image_to_string(
                        Image.open(path_to_ocr + f"\\char\\{img}"),
                        lang="eng",
                        config=custom_config,
                    ).strip()
                    if coolthing == "":
                        return
                    try:
                        num = int(re.sub("\D", "", re.sub("-.*\d|-", "", coolthing)))
                    except ValueError:
                        num = 999999
                        dprint(f"ValueError - current string: {coolthing}")
                    # dprint(char + " - " + str(num))
                    if (
                            num <= pn
                            and char not in self.aniblacklist
                            and charchar not in self.charblacklist
                    ):
                        tprint(
                            f"{Fore.GREEN}[Tofu] Found Print # {Fore.MAGENTA}{num}{Fore.RESET}"
                        )
                        cid = message.channel.id
                        self.tofu_current_card = charchar
                        self.tofureact = True
                        self.tofuurl = message.attachments[0].url
                        if loghits:
                            with open("log.txt", "a") as ff:
                                if timestamp:
                                    ff.write(
                                        f"{current_time()} - Tofu Print Number: {coolthing} - {self.tofuurl}\n"
                                    )
                                else:
                                    ff.write(
                                        f"Tofu Print Number: {coolthing} - {self.tofuurl}\n"
                                    )
                        if img == "print1.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[0].click()
                                await self.tofuafterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "1️⃣")
                        elif img == "print2.png":
                            if isbutton(cid):
                                await self.wait_for("message_edit", check=mcheck)
                                await self.tofubuttons[1].click()
                                await self.tofuafterclick()
                            else:
                                reaction = await self.wait_for(
                                    "reaction_add", check=check
                                )
                                await self.tofu_react_add(reaction, "2️⃣")
                if cool.group(2) == self.user.id and not self.tofureact:
                    self.tofureact = True
                    self.tofuurl = ""
                    tprint(f"{Fore.LIGHTMAGENTA_EX}[Tofu] No cards found, defaulting to random")
                    if isbutton(cid):
                        await self.wait_for("message_edit", check=mcheck)
                        await self.tofubuttons[3].click()
                        await self.tofuafterclick()
                    else:
                        reaction = await self.wait_for(
                            "reaction_add", check=check
                        )
                        await self.tofu_react_add(reaction, "❓")
        if re.search(
                f"<@{str(self.user.id)} grabbed .* |<@{str(self.user.id)}> fought off .* ",
                message.content,
        ):
            a = re.search(
                f"<@{str(self.user.id)}> .*:(.*):.*#(.*) ·.*· (.*)",
                message.content,
            )
            self.tofutimer += 540
            self.missed -= 1
            self.collected += 1
            tprint(
                f"{Fore.BLUE}[Tofu] Obtained Card: {Fore.LIGHTMAGENTA_EX}{a.group(3)} | Print #{a.group(2)} | "
                f"Condition: {a.group(1)}{Fore.RESET} "
            )
            if logcollection:
                with open("log.txt", "a") as ff:
                    if timestamp:
                        ff.write(
                            f"{current_time()} - Tofu Card: {a.group(3)} - {self.tofuurl}\n"
                        )
                    else:
                        ff.write(f"Tofu Card: {a.group(3)} - {self.tofuurl}\n")

    async def react_add(self, reaction, emoji):
        reaction, _ = reaction
        try:
            dprint(f"{Fore.BLUE}Attempting to react")
            await asyncio.sleep(random.uniform(0.25, 0.97))
            await reaction.message.add_reaction(emoji)
        except discord.errors.Forbidden as oopsie:
            dprint(f"{Fore.RED}Fuck:\n{oopsie}")
            return
        if self.react:
            self.timer += 60
            self.missed += 1
        dprint(f"{Fore.BLUE}Reacted with {emoji} successfully{Fore.RESET}")
        self.react = False

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
            if self.timer > 0:
                self.timer -= 1
                if self.tofutimer > 0:
                    Popen(
                        f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                        f"cooldown for {self.timer} seconds | Tofu on cooldown for {self.tofutimer} seconds",
                        shell=True,
                    )
                else:
                    Popen(
                        f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                        f"cooldown for {self.timer} seconds",
                        shell=True,
                    )
            elif self.tofutimer > 0:
                self.tofutimer -= 1
                Popen(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - On "
                    f"Tofu on cooldown for {self.tofutimer} seconds",
                    shell=True,
                )
            else:
                Popen(
                    f"title Karuta Sniper {v} - Collected {self.collected} cards - Missed {self.missed} cards - Ready",
                    shell=True,
                )
            await asyncio.sleep(1)

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

    async def configwatch(self, path):
        bruh = api.FileWatch(path)
        while True:
            await asyncio.sleep(1)
            if bruh.watch():
                with open("config.json") as ff:
                    pass  # TODO: stuff

    async def autofarm(self):
        channel = self.get_channel(resourcechannel)
        while True:
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("kw")
            async for message in channel.history(limit=1):
                print(message.content)
                if "you do not have" in message.content:
                    print("Autofarm - You dont have a permit")
                else:
                    matches = re.search(r"(\d+) hours", message.content)
                    match1 = re.search(r"(\d+) hour", message.content)
                    match0 = re.search(r"(\d+) minute", message.content)
                    if matches:
                        hours = int(match1.group(1))
                        print(f"Autofarm - Waiting for {hours} hours to work again")
                        await asyncio.sleep(hours * 3600 + 5)
                    elif match1:
                        hours = int(match1.group(1))
                        print(f"Autofarm - Waiting for {hours} hour to work again")
                        await asyncio.sleep(hours * 3600 + 5)
                    elif match0:
                        minutes = int(match0.group(1))
                        print(f"Autofarm - Waiting for {minutes} minutes to work again")
                        await asyncio.sleep(minutes * 3600 + 5)
                    else:
                        print("Autofarm - Processing...")
                if message is not None:
                    reply = await self.wait_for(
                        "message", check=lambda m: m.author.id == 646937666251915264
                    )
                    if reply:
                        await self.autofindresource()
                        await reply.components[0].children[1].click()
                        print("Autofarm - Worked successfully!")
                        await asyncio.sleep(12 * 3600 + 5)  # 12 hours

    async def autofindresource(self):
        channel = self.get_channel(
            resourcechannel
        )  # your work/auto check for resource channel
        async with channel.typing():
            await asyncio.sleep(random.uniform(0.2, 1))
        await channel.send("kn")
        reply = await client.wait_for(
            "message", check=lambda m: m.author.id == 646937666251915264
        )
        a = re.compile(
            "`(\w+)` · \*\*(\d+)%\*\* tax · \*\*(\d+)(%\*\* power · \*\*(\d+)|\*)",
            re.MULTILINE,
        ).findall(reply.embeds[0].to_dict()["description"].replace(",", ""))
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
            while not self.timer == 0:
                pass
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("kd")
            tprint(f"{Fore.LIGHTWHITE_EX}Auto Dropped Cards")

    async def summon(self):
        channel = self.get_channel(summonchannel)
        while True:
            await asyncio.sleep(tofu_delay + random.randint(tofu_min, tofu_max))
            while not self.tofutimer == 0:
                pass
            async with channel.typing():
                await asyncio.sleep(random.uniform(0.2, 1))
            await channel.send("ts")
            tprint(f"{Fore.LIGHTWHITE_EX}Summoned Cards")

    async def afterclick(self):
        dprint(f"Clicked on Button")
        self.timer += 60
        self.missed += 1
        self.react = False

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
