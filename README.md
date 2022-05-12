# KarutaSniper
A bot to automate collecting cards for the discord game Karuta

# Installation

1. Download repo
2. Install requirements
3. Install pytesseract

# How use

Run main.py, Characters and Animes to sniper are in keywords

# Changelog

b0.1
- added ocr
- added levenshtein
- attempted to fix reacting at the right moment

b0.2
- added reporting to console if grabbing the card was successful
- improved levenshtein for less falses
- added more debug info
- added more supported ocr characters

b0.2.1
- added timestamps

b0.3
- added cooldown support
- removed useless try statement

b0.3.1
- fixed cooldowns to not break everything

b0.3.2
- fixed triple reactions

b0.3.3
- fixed typo
- fixed stackoverflow error
- fixed reactions not working due to me being stupid
- fixed cooldowns being longer than it should be

b0.3.4
- Bugfix: the obtained card in the console will now be what was obtained

b0.3.5
- added obtaining cards to log

b0.3.6
- added more configurability
- began adding integration for 4 card drops


## Todo

- better window title
- revamp ui
- add support for card drops with 4 cards (more complicated than it looks or im just stupid)
- code cleanup

# Credits

- [RiccardoLunardi](https://github.com/riccardolunardi/KarutaBotHack) for the code written in ocr.py