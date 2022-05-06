from setuptools import setup


def get_requirements():
    with open("requirements.txt") as f:
        return list(f.read().splitlines())


def get_dependency_links():
    with open("requirements.txt") as f:
        return list(f.read().splitlines())


packages = [
    "bot",
    "bot.cogs",
]

setup(
    name="studybot",
    author="ACEslava",
    version="0.1.0.0",
    packages=packages,
    install_requires=get_requirements(),
    dependency_links=get_dependency_links(),
    python_requires=">=3.9.0",
)
