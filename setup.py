"""
Setup script for building Hardsubber macOS app
"""
from setuptools import setup

APP = ['hardsubber.py']
DATA_FILES = [('', ['SFArabicMPV-Bold.ttf'])]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['tkinter'],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'Hardsubber',
        'CFBundleDisplayName': 'Hardsubber',
        'CFBundleIdentifier': 'com.hardsubber.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    name='Hardsubber',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
