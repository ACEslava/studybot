# Contribution workflow

## Step 1: Fork the repo

[Fork a repo](https://docs.github.com/en/get-started/quickstart/fork-a-repo)

## Step 2: Configure your environment

How you setup your environment is up to you. Its highly suggested to [create a virtual environment](https://realpython.com/python-virtual-environments-a-primer/) for development.

### Setting up the environment to run the bot.

* Install pre-commit hooks to your python environment `pip install pre-commit`
  * If you don't use pre-commit, ensure you apply [black](https://github.com/psf/black), [isort](https://pycqa.github.io/isort/), and [flake8](https://flake8.pycqa.org/en/latest/) when committing.

## Step 3: Prepare a PR

Ensure your code has been formatted with `black`, imports sorted with `isort`, and linted with `flake8`. **I will reject pull requests if you aren't doing this.**
If you think we should ignore a flake8 warning, please detail why in the PR.

Currently I'm not familiar enough with the PR process to really write much.