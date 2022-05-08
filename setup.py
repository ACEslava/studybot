from setuptools import setup


def get_requirements():
    with open("requirements.txt") as f:
        requirements = list(
            filter(
                lambda x: not x.startswith("#") and not x.startswith("git+"),
                f.read().splitlines(),
            )
        )
    return requirements


def get_dependency_links():
    with open("requirements.txt") as f:
        links = list(
            filter(
                lambda x: not x.startswith("#") and x.startswith("git+"),
                f.read().splitlines(),
            )
        )
    return links


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
