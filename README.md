# KarutaSniper
A bot to automate collecting cards for the discord game Karuta


# Stuff in readme

1. [Known Issues](#known-issues)
2. [Installation](#installation)
3. [Use](#how-use)
4. [Changelog](#changelog)
5. [Todo](#todo)
6. [Credits](#credits)
7. [Disclaimer](#disclaimer)
8. [Contact Me](#contact-me)


## Known Issues

Buttons don't work


## Installation

1. Download repo
2. Install requirements
3. Install tesseract (and add to path--[See this](https://github.com/NoMeansNowastaken/KarutaSniper/issues/7))

## How use

Run main.py, Characters and Animes to snipe are in keywords

## Changelog

### b0.1
- added ocr
- added levenshtein
- attempted to fix reacting at the right moment

### b0.2
- added reporting to console if grabbing the card was successful
- improved levenshtein for less falses
- added more debug info
- added more supported ocr characters

### b0.2.1
- added timestamps

### b0.3
- added cooldown support
- removed useless try statement

### b0.3.1
- fixed cooldowns to not break everything

### b0.3.2
- fixed triple reactions

### b0.3.3
- fixed typo
- fixed stackoverflow error
- fixed reactions not working due to me being stupid
- fixed cooldowns being longer than it should be

### b0.3.4
- Bugfix: the obtained card in the console will now be what was obtained

### b0.3.5
- added obtaining cards to log

### b0.3.6
- added more configurability
- began adding integration for 4 card drops

### b0.3.7
- Hotfix: fixed float and str incompatibilities
- Hotfix: fixed variable name issue

### b0.3.8
- Hotfix: fixed logs causing errors

### b0.4
- made ui better
- token finder if no token detected
- better title
- partial stats (not permanent)

### b0.4.1
- fixed stuff not working
- fixed stats
- added more config stuff

### b0.4.2
- the logo thing is now centered

### b0.4.3
- added update checking (can be disabled in config)

### v1.0
- made ocr work a lot better (hopefully)
- a lot of changes to readme file

### v1.0.1
- added blacklist
- added updating card lists without needing to restart

### v1.1
- added support for card drops with 4 cards (idk why it took so long)
- added auto dropping cards

### v1.1.1

- Hotfix: forgot to activate the autodrop &#128128;

### v1.2

- added support for buttons


## TODO

- support for bots similar to karuta (like SOFI); this might never happen/take a long time to be implemented
- improve stuff

## Credits

- [RiccardoLunardi](https://github.com/riccardolunardi/KarutaBotHack) for the code written in ocr.py

## Disclaimer

This is for educational purposes only blah blah blah, I don't condone breaking discord's TOS or karuta's, it is not my fault if you get banned from karuta or discord.

Also dont be that guy who clones this repo and then updates config.json with his token which basically gives anyone access to his account (yes someone did this)

## Contact Me
This is my current discord tag, and only public way to contact me (besides github)

Discord: ```NoMeansNo#5750```
Beware of a guy named Scorpion08#0001 (1017838925752049776) he is just reselling my code for profit, unfortunately I dont know more because he immediately blocked me.
