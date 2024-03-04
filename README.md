# KarutaSniper
A bot to automate collecting cards for the discord game Karuta

# Stuff in readme

1. [Known Issues](#known-issues)
2. [Installation](#installation)
3. [Use](#how-use)
4. [Feature Explanation](#feature-explanation)
5. [Changelog](#changelog)
6. [Todo](#todo)
7. [Credits](#credits)
8. [Disclaimer](#disclaimer)
9. [Contact Me](#contact-me)

## Known Issues

- print numbers and autofarm might be buggy
- i fucked detection up; it might detect the same a few times


## Installation

1. Download repo
2. Run install.bat (if on windows) - its a file in the zip folder
3. If that doesnt work or you are on a different os follow the instructions below
4. Install requirements
5. Install tesseract-ocr (and add to path)
   1. If on windows prebuilt binaries can be found at https://github.com/UB-Mannheim/tesseract/wiki

## How to use

Run main.py, Characters and Animes to snipe are in keywords


Note that sometimes the ocr can misread names and pick up cards you dont want. This is especially true for reading print numbers, so expect falses until it is improved

If you see something like H1 in the update notice, you should probably update as it stands for hotfix and usually fixes
major bugs


## Feature Explanation

I wont explain features that explain themselves

- DropDelay - How long to wait in between autodrops (in seconds)
- Randmin + randmax - Extra delay added to dropdelay to look less robotic
- Log Hits - Log everytime it finds a card to log.txt along with the card image
- Log Collection - Log every card it collects as well as the image
- Check Print - Collect cards based on their print number (set by print_number)
- Accuracy - Ocr (computer reading text) is not always accurate, so this will allow some misread characters, but at the cost of some false hits. Increase this for less falses, but also less forgiveness (and vice versa)
- Blaccuracy - accuracy but for matches with **only** aniblacklist


## Changelog

## v2.3

- buttons fixed
- less laggy
- removed christmas event

## v2.3.1

- minor changes
- blessing support

## v2.3.2

- minor changes
- fix retardation

## TODO

- support for bots similar to karuta (like SOFI, Mudae, ~~Tofu~~); this might never happen/take a long time to be implemented
- improve print numbers
- improve ocr
- make it less buggy (especially tofu)
- first run setup

## Credits

- [RiccardoLunardi](https://github.com/riccardolunardi/KarutaBotHack) for the code written in ocr.py
- Vu for the autofarm code

## Disclaimer

This is for educational purposes only blah blah blah, I don't condone breaking discord's TOS or karuta's, it is not my fault if you get banned from karuta or discord.

Also dont be that guy who clones this repo and then updates config.json with his token which basically gives anyone access to his account (yes someone did this)

## Contact Me
This is my current discord tag, and only public way to contact me (besides github)

Discord: ```NoMeansNo#5750```

Just Please use your brain when communicating, [don't start by saying hi and waiting for a response](https://nohello.net)
