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

## Known Issues

- print numbers unstable


## Installation

1. Download repo
2. Run install.bat (if on windows)
3. If that doesnt work or you are on a different os follow the instructions below
4. Install requirements
5. Install [discord.py-self](https://github.com/dolfies/discord.py-self) from repo (you need version 2 or higher)
6. Install tesseract-ocr (and add to path)
   1. If on windows prebuilt binaries can be found at https://github.com/UB-Mannheim/tesseract/wiki

## How to use

Run main.py, Characters and Animes to snipe are in keywords


Note that sometimes the ocr can misread names and pick up cards you dont want. This is especially true for reading print numbers, so expect falses until it is improved

## Changelog

### b1.2.3

- added support for print numbers

### b2.0

- fixed weird newline that was appearing
- reactions work again
- tried to make print have less falses, but theres no general cropping solution
- buttons now work

### v2.0rc0

- code looks better now
- removed useless shit
- just making sure there arent any bugs

### v2.0
- well i merged the wrong way so update ig


## TODO

- support for bots similar to karuta (like SOFI); this might never happen/take a long time to be implemented
- improve stuff/fix code
- improve print numbers
- first run setup

## Credits

- [RiccardoLunardi](https://github.com/riccardolunardi/KarutaBotHack) for the code written in ocr.py

## Disclaimer

This is for educational purposes only blah blah blah, I don't condone breaking discord's TOS or karuta's, it is not my fault if you get banned from karuta or discord.

Also dont be that guy who clones this repo and then updates config.json with his token which basically gives anyone access to his account (yes someone did this)

## Contact Me
This is my current discord tag, and only public way to contact me (besides github)

Discord: ```NoMeansNo#5750```
Beware of a guy named Scorpion08#0001 (1017838925752049776) he is just reselling my code for profit, unfortunately I dont know more because he immediately blocked me.
