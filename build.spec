# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_window.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web_server.py', '.'),
        ('templates', 'templates'),
        ('locales', 'locales'),
        ('common', 'common'),
        ('config.json', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'jinja2',
        'pydantic',
        'httpx',
        'vdf',
        'asyncio',
        'webview',
        'pythonnet',
        'clr',
        'clr_loader',
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
