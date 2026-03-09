#!/usr/bin/env python3
"""
Build script to create a standalone executable of the Flask backend
for offline native app usage with Capacitor/Tauri.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False, e.stderr

def create_standalone_app():
    """Create a standalone executable of the Flask app using PyInstaller."""

    print("🚀 Building standalone Flask executable...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Create a temporary spec file for PyInstaller
    spec_content = '''
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
'''

    # Write the spec file
    spec_file = 'waveza-backend.spec'
    with open(spec_file, 'w') as f:
        f.write(spec_content)

    # Run PyInstaller
    cmd = f'pyinstaller --clean {spec_file}'
    success, output = run_command(cmd)

    if not success:
        print("❌ PyInstaller build failed!")
        return False

    # Clean up spec file
    os.remove(spec_file)

    # Check if executable was created
    exe_name = 'waveza-backend'
    if os.name == 'nt':  # Windows
        exe_name += '.exe'

    exe_path = Path('dist') / exe_name
    if exe_path.exists():
        print(f"✅ Standalone executable created: {exe_path}")

        # Copy to a known location for the native apps
        target_dir = Path('bundled-backend')
        target_dir.mkdir(exist_ok=True)

        shutil.copy2(exe_path, target_dir / exe_name)
        print(f"✅ Copied to: {target_dir / exe_name}")

        return True
    else:
        print("❌ Executable not found after build!")
        return False

def create_startup_script():
    """Create a script to start the bundled backend."""

    script_content = '''#!/bin/bash
# Startup script for bundled WaveZA backend

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine executable name based on platform
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    EXECUTABLE="waveza-backend.exe"
else
    EXECUTABLE="waveza-backend"
fi

EXECUTABLE_PATH="$SCRIPT_DIR/$EXECUTABLE"

# Check if executable exists
if [ ! -f "$EXECUTABLE_PATH" ]; then
    echo "Error: Backend executable not found at $EXECUTABLE_PATH"
    exit 1
fi

# Set environment variables
export FLASK_ENV=production
export DATABASE_URL="sqlite:///$SCRIPT_DIR/mishwrites.db"

# Start the backend server
echo "Starting WaveZA backend server..."
"$EXECUTABLE_PATH"
'''

    with open('bundled-backend/start-backend.sh', 'w') as f:
        f.write(script_content)

    # Make it executable
    os.chmod('bundled-backend/start-backend.sh', 0o755)

    print("✅ Startup script created")

def update_native_configs():
    """Update Capacitor and Tauri configs to include the bundled backend."""

    # For Capacitor - we need to copy the backend to the native projects
    capacitor_config = '''
{
  "appId": "com.waveza.app",
  "appName": "WaveZA",
  "bundledWebRuntime": false,
  "npmClient": "npm",
  "webDir": "build",
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 0
    }
  },
  "server": {
    "hostname": "localhost",
    "port": 5000
  }
}
'''

    # Update capacitor.config.ts
    cap_config_path = Path('frontend/capacitor.config.ts')
    if cap_config_path.exists():
        with open(cap_config_path, 'w') as f:
            f.write(capacitor_config)
        print("✅ Capacitor config updated")

    # For Tauri - update tauri.conf.json to include the backend
    tauri_config = '''
{
  "$schema": "../node_modules/@tauri-apps/cli/schema.json",
  "build": {
    "beforeBuildCommand": "",
    "beforeDevCommand": "",
    "devPath": "http://localhost:3000",
    "distDir": "../build"
  },
  "bundle": {
    "active": true,
    "category": "Productivity",
    "copyright": "",
    "deb": {
      "depends": []
    },
    "externalBin": [
      "../bundled-backend/waveza-backend"
    ],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "identifier": "com.waveza.app",
    "longDescription": "",
    "macOS": {
      "entitlements": null,
      "exceptionDomain": "",
      "frameworks": [],
      "providerShortName": null,
      "signingIdentity": null
    },
    "resources": [
      "../bundled-backend/"
    ],
    "shortDescription": "",
    "targets": "all",
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": ""
    }
  },
  "identifier": "com.waveza.app",
  "productName": "WaveZA",
  "version": "1.0.0",
  "plugins": {}
}
'''

    tauri_config_path = Path('frontend/src-tauri/tauri.conf.json')
    if tauri_config_path.exists():
        with open(tauri_config_path, 'w') as f:
            f.write(tauri_config)
        print("✅ Tauri config updated")

def main():
    """Main build function."""
    print("🔨 Building WaveZA for offline native app usage...")

    # Step 1: Create standalone executable
    if not create_standalone_app():
        sys.exit(1)

    # Step 2: Create startup script
    create_startup_script()

    # Step 3: Update native app configurations
    update_native_configs()

    print("\n🎉 Build complete!")
    print("\nNext steps:")
    print("1. Copy 'bundled-backend/' folder to your native app projects")
    print("2. Update your React app to connect to 'http://localhost:5000' when running locally")
    print("3. For production native apps, start the backend executable on app launch")
    print("4. Test the native apps with offline functionality")

if __name__ == '__main__':
    main()