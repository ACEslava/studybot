# studybot
A general purpose bot for the study group discord

Running the Bot
----
Note: All commands are for a Linux-based environment
Ensure you are running python 3.10 or greater
Initialize your virtual environment
```
python -m virtualenv .venv
source .venv/bin/activate
```

Install dependencies
```
python -m pip install .
```

Run the bot
```
python -m launcher.py
```

Contributing
----
All code should be formatted and linted with

* [black](https://github.com/psf/black)
* [isort](https://pycqa.github.io/isort/)
* [flake8](https://flake8.pycqa.org/en/latest/)

You can install [pre-commit](https://pre-commit.com/) which will do this for you when you try and commit.

Note: flake8 E203 can be ignored, line lengths set to 88

<br/><br/>

To start contributing, read through the [contributing doc](docs/contributing.md).

You should also review [Understanding the bot](docs/understanding_the_bot.md).
