from setuptools import setup, find_packages

setup(
    name="hapi",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer",
        "rich",
        "sqlalchemy",
    ],
    entry_points={
        "console_scripts": [
            "hapi=src.main:app",
        ],
    },
)