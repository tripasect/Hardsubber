# -*- mode: python ; coding: utf-8 -*-
import os

# Get all dylib files from Frameworks directory
frameworks_dir = 'Frameworks'
binaries = []

# Add ffmpeg and ffprobe executables
binaries.append((os.path.join(frameworks_dir, 'ffmpeg'), '.'))
binaries.append((os.path.join(frameworks_dir, 'ffprobe'), '.'))

# Add all dylib files
for file in os.listdir(frameworks_dir):
    if file.endswith('.dylib'):
        binaries.append((os.path.join(frameworks_dir, file), '.'))

block_cipher = None

a = Analysis(
    ['hardsubber.py'],
    pathex=[],
    binaries=binaries,
    datas=[('SFArabicMPV-Bold.ttf', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Hardsubber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Hardsubber',
)

app = BUNDLE(
    coll,
    name='Hardsubber.app',
    icon='icon.icns',
    bundle_identifier='com.hardsubber.app',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleShortVersionString': '1.2.0',
        'CFBundleVersion': '1.2.0',
    },
)
