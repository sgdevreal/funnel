# setup.py
from setuptools import setup, find_packages

setup(
    name="your_library",
    version="0.1",
    description="A financial ticker and exchange scraper library",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)