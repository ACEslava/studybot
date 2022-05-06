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

<!-- ### Onhandling

[onhandling.py](../cogs/onhandling.py)

Onhandling should contain code related to [events](https://discordpy.readthedocs.io/en/latest/api.html#event-reference). It might make sense to add onhandling listeners in other files, but any most onhandling should be placed here. Very simple onhandling can be placed in [studybot.py](../studybot.py). -->

### Utilities

[utilities.py](../bot/cogs/utilities.py)

Utilities should contain slash commands that don't make sense to create a cog for. If you don't feel a command should be placed in a specific cog (new or current) then it can be placed here.