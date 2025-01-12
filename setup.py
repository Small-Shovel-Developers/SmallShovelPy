from setuptools import setup, find_packages
import json

# Metadata
with open('SmallShovelPy/metadata.json', 'r') as file:
    metadata = json.load(file)

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="SmallShovelPy",
    version = metadata["__version__"],
    author = metadata["__author__"],
    author_email="seth@smallshovel.com",
    description="Small Shovel's custom library for building and scheduling data pipelines",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Small-Shovel-Developers/SmallShovelPy",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
