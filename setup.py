from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['source'],
    'plist': {
        'CFBundleName': "Procrast",
        'CFBundleDisplayName': "Procrast",
        'CFBundleGetInfoString': "Procrast",
        'CFBundleIdentifier': "com.relativecompanies.procrast",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"Copyright © 2023, Relative Companies LLC, All Rights Reserved"
    },
    'iconfile': 'assets/dice.png',
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)