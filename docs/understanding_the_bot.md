# Understanding the bot

The layout and design of the bot might initially be confusing. This document aims to provide insight into the flow and layout of the bot.

## The launcher

[launcher.py](../bot/launcher.py)

```
bot
└──launcher.py
```

The launcher serves as a small python file to launch and run the bot.

The only code that should exist in this file is anything that needs to be done prior to launching the bot.

## The bot

[studybot.py](../bot/studybot.py)

```
bot
 └──studybot.py
```

studybot.py is the heart of the bot

Any code in this file should only look to setup the bot. This can include initial database actions, syncing slash commands, or simple [event handling](https://discordpy.readthedocs.io/en/latest/api.html#event-reference).

## The cogs

```
bot
 ├──cogs
 │   ├── onhandling.py
 │   └── utilities.py
```
### Utilities

[utilities.py](../bot/cogs/utilities.py)

Utilities should contain slash commands that don't make sense to create a cog for. If you don't feel a command should be placed in a specific cog (new or current) then it can be placed here.

### Onhandling

[onhandling.py](../bot/cogs/onhandling.py)

Onhandling should contain code related to [events](https://discordpy.readthedocs.io/en/latest/api.html#event-reference). It might make sense to add onhandling listeners in other files, but any most onhandling should be placed here.

### SearchEngines

[searchengines.py](../bot/cogs/searchengines.py)

SearchEngines should contain any search-related functionality (aka the original SearchIO commands).

### Fun

[fun.py](../bot/cogs/fun.py)

Fun should contain miscellaneous, fun commands that wouldn't be relevant in other cogs.

## The functions

```
bot
 ├──functions
 │   ├── loading_message.py
 │   └── multi_page.py
```

The functions folder should contain major functions that are needed by other parts of the bot (e.g. the loading message, multi paged embeds). Each function MUST contain a numpy-formatted docstring detailing a summary, arguments, and returns for the function. A template is provided here:
```
"""summary

Parameters
----------
arg1 : str
    description
arg2 : float
    description

Returns
-------
int
    description
"""
```
