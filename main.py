from os import listdir, system
from os.path import isfile, join
import discord
import re
import pytesseract
from PIL import Image
import requests
import json
from datetime import datetime
from time import sleep
from ocr import get_card, get_bottom, get_top
from colorama import Fore, init
import api

init(convert=True)
match = "(is dropping [3-4] cards!)|(I'm dropping [3-4] cards since this server is currently active!)"
path_to_ocr = "temp"
v = "b0.2.1"
global timer
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

    async def on_ready(self):
        system("cls")
        tprint(f'{Fore.BLUE}Logged in as {Fore.RED}{self.user.name} ({self.user.id}){Fore.RESET}')
        system(f"title Karuta Sniper - {v}")

    async def on_message(self, message):
        if str(message.author.id) != '646937666251915264':
            return

        if str(message.channel.id) not in channels:
            return

        # print(message.content)

        if re.search(match, message.content):
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
                        with open("log.txt", "a") as f:
                            f.write(f"{current_time()} - Character: {char} - {message.attachments[0].url}\n")
                        sleep(1)
                        try:
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
                        except discord.errors.Forbidden:
                            tprint(f"{Fore.RED}Failed to react{Fore.RESET}")
                for i in animes:
                    if api.isSomething(char, i):
                        tprint(f"{Fore.GREEN}Found Anime: {Fore.MAGENTA}{char}{Fore.RESET}")
                        self.current_card = char
                        with open("log.txt", "a") as f:
                            f.write(f"{current_time()} - Anime: {char} - {message.attachments[0].url}\n")
                        sleep(1)
                        try:
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
                        except discord.errors.Forbidden:
                            tprint(f"{Fore.RED}Failed to react{Fore.RESET}")
        if re.search(
                f'<@{self.user.id}> took the \*\*.*\*\* card `.*`!|<@{self.user.id}> fought off .* and took the \*\*.*\*\* card `.*`!',
                message.content):
            a = re.search(r'\*\*(.*)\*\* card `(.*)`!', message.content)
            tprint(f"{Fore.BLUE}Obtained Card: {Fore.MAGENTA}{a.group(1)}{Fore.RESET}")

    async def on_reaction_add(self, reaction, user):
        if user != '646937666251915264':
            if reaction.message.id == self.messageid:
                try:
                    if self.important == 1:
                        await reaction.message.add_reaction("1️⃣")
                    elif self.important == 2:
                        await reaction.message.add_reaction("2️⃣")
                    elif self.important == 3:
                        await reaction.message.add_reaction("3️⃣")
                except discord.errors.Forbidden as e:
                    tprint(f"{Fore.RED}Error: Failed to react\nStacktrace: {e}{Fore.RESET}")


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def tprint(message):
    print(f"{Fore.LIGHTBLUE_EX}{current_time()} - {Fore.RESET}{message}")


client = Main()
tprint(f"{Fore.GREEN}Starting Bot{Fore.RESET}")
client.run(token)
