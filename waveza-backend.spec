
# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(SPEC))
sys.path.insert(0, current_dir)

# PyInstaller analysis
a = Analysis(
    ['app.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('templates', 'templates'),
        ('mishwrites.db', '.'),  # Include database if it exists
        ('.env', '.'),  # Include environment file
    ],
    hiddenimports=[
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_migrate',
        'flask_cors',
        'werkzeug',
        'sqlalchemy',
        'cloudinary',
        'dotenv',
        'pywebpush',
        'beautifulsoup4',
        'bleach',
        'unidecode',
        'slugify',
        'load_dotenv',
        'psycopg2',
        'datetime',
        'uuid',
        'logging',
        'pathlib',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='waveza-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for production (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
