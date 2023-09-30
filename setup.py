from setuptools import setup, find_packages

setup(
    name="asirk",
    version="0.1",
    packages=find_packages(),
    entry_points={"console_scripts": ["asirk=asirk.__main__:main"]},
)
