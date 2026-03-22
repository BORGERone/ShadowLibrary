# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web_server.py', '.'),
        ('run_server.py', '.'),
        ('templates', 'templates'),
        ('locales', 'locales'),
        ('common', 'common'),
        ('icon.ico', '.'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'jinja2',
        'pydantic',
        'httpx',
        'vdf',
        'json',
        'asyncio',
        'multiprocessing',
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ShadowLibrary',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
