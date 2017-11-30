from setuptools import setup

setup(
    # Application name:
    name = "soundboard",

    # Version number:
    version = "0.1.0",

    # Application author details:
    author = "Brahm Lower",
    author_email = "bplower@gmail.com",

    # License
    license = "",

    # Package directory
    package_dir = {'soundboard': 'src'},

    # Packages
    packages = ["soundboard"],

    package_data = {
        "soundboard": [
            "static/index.html",
            "static/site.css",
            "static/site.js"
        ]
    },

    # Description:
    description = "A simple webapp for creating and quickly playing short soundclips",

    # Dependant packages:
    install_requires = [
        "Flask",
        "docopt"
    ],

    entry_points={
        'console_scripts': ['soundboard = soundboard:main']
    }
)
