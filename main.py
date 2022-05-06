import asyncio
from os import listdir, system
from os.path import isfile, join
import discord
import re
import pytesseract
from PIL import Image
import requests
import json
from datetime import datetime
from ocr import get_card, get_bottom, get_top
from colorama import Fore, init
import api

init(convert=True)
match = "(is dropping 3 cards!)|(I'm dropping 3 cards since this server is currently active!)"
path_to_ocr = "temp"
v = "b0.3.4"
with open("config.json") as f:
    config = json.load(f)
    token = config["token"]
    channels = config["channels"]

with open("keywords\\characters.txt") as f:
    chars = f.read().splitlines()

with open("keywords\\animes.txt") as f:
    animes = f.read().splitlines()


class Main(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messageid = None
        self.important = None
        self.current_card = None
        self.ready = False
        self.react = True
        self.timer = 0

    async def on_ready(self):
        system("cls")
        tprint(
            f'{Fore.BLUE}Logged in as {Fore.RED}{self.user.name}#{self.user.discriminator} ({self.user.id}){Fore.RESET}')
        self.ready = True
        asyncio.get_event_loop().create_task(self.cooldown())

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
            for i in range(0, 3):
                get_card(f"{path_to_ocr}\\card{i + 1}.png", "temp\\card.webp", i)
                get_card(f"{path_to_ocr}\\card{i + 1}.png", "temp\\card.webp", i)
                get_card(f"{path_to_ocr}\\card{i + 1}.png", "temp\\card.webp", i)

            for i in range(0, 3):
                get_top(f"{path_to_ocr}\\card{i + 1}.png", f"{path_to_ocr}\\char\\top{i + 1}.png")
                get_bottom(f"{path_to_ocr}\\card{i + 1}.png", f"{path_to_ocr}\\char\\bottom{i + 1}.png")

            onlyfiles = [f for f in listdir("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char") if
                         isfile(join("C:\\users\\user\\pycharmprojects\\karuta bot\\temp\\char", f))]
            # print("File trovati: ", onlyfiles)
            custom_config = r'--psm 6 --oem 3 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@&0123456789/:- "'
            for img in onlyfiles:
                char = pytesseract.image_to_string(Image.open(path_to_ocr + '\\char\\' + img), lang='eng',
                                                   config=custom_config).strip()
                for i in chars:
                    if api.isSomething(char, i):
                        tprint(f"{Fore.GREEN}Found Character: {Fore.MAGENTA}{char}{Fore.RESET}")
                        self.current_card = char
                        self.react = True
                        with open("log.txt", "a") as f:
                            f.write(f"{current_time()} - Character: {char} - {message.attachments[0].url}\n")
                        if img == "top1.png":
                            self.messageid = message.id
                            self.important = 1
                            # await message.add_reaction("1️⃣")
                        elif img == "top2.png":
                            self.messageid = message.id
                            self.important = 2
                            # await message.add_reaction("2️⃣")
                        elif img == "top3.png":
                            self.messageid = message.id
                            self.important = 3
                            # await message.add_reaction("3️⃣")
                for i in animes:
                    if api.isSomething(char, i):
                        tprint(f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char}{Fore.RESET}")
                        self.current_card = char
                        self.react = True
                        with open("log.txt", "a") as f:
                            f.write(f"{current_time()} - Anime: {char} - {message.attachments[0].url}\n")
                        if img == "bottom1.png":
                            self.messageid = message.id
                            self.important = 1
                            # await message.add_reaction("1️⃣")
                        elif img == "bottom2.png":
                            self.messageid = message.id
                            self.important = 2
                            # await message.add_reaction("2️⃣")
                        elif img == "bottom3.png":
                            self.messageid = message.id
                            self.important = 3
                            # await message.add_reaction("3️⃣")
        if re.search(
                f'<@{str(self.user.id)}> took the \*\*.*\*\* card `.*`!|<@{str(self.user.id)}> fought off .* and took the \*\*.*\*\* card `.*`!',
                message.content):
            a = re.search(f'<@{str(self.user.id)}>.*took the \*\*(.*)\*\* card `(.*)`!', message.content)
            self.timer += 540
            tprint(f"{Fore.BLUE}Obtained Card: {Fore.MAGENTA}{a.group(1)}{Fore.RESET}")

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
                except discord.errors.Forbidden:
                    return
                if self.react:
                    self.timer += 60
                self.react = False

    async def cooldown(self):
        for i in range(10000000):
            if self.timer > 0:
                self.timer -= 1
                await asyncio.sleep(1)
                system(f"title Karuta Sniper {v} - On cooldown for {self.timer} seconds")
            else:
                await asyncio.sleep(1)
                system(f"title Karuta Sniper {v} - Waiting for next card")


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def tprint(message):
    print(f"{Fore.LIGHTBLUE_EX}{current_time()} - {Fore.RESET}{message}")


client = Main()
tprint(f"{Fore.GREEN}Starting Bot{Fore.RESET}")
client.run(token)
