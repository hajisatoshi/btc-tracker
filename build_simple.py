#!/usr/bin/env python3
"""
Simple build script for BTC Portfolio Tracker
"""

import os
import subprocess
import sys

def build_simple():
    """Build the executable using a simpler approach"""
    print("Building executable with simpler approach...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        import shutil
        shutil.rmtree('dist')
    if os.path.exists('build'):
        import shutil
        shutil.rmtree('build')
    
    # Simple PyInstaller command
    cmd = [
        'pyinstaller',
        '--distpath', 'dist',
        '--workpath', 'build',
        '--clean',
        '--add-data', 'frontend:frontend',
        '--add-data', 'backend:backend',
        '--add-data', 'README.md:.',
        '--add-data', 'LICENSE:.',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'requests',
        '--hidden-import', 'flask',
        '--hidden-import', 'flask_cors',
        '--hidden-import', 'flask_jwt_extended',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'threading',
        '--hidden-import', 'subprocess',
        '--hidden-import', 'dotenv',
        '--hidden-import', 'ipaddress',
        '--name', 'BTC-Portfolio-Tracker',
        'main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print("Executable created in: dist/BTC-Portfolio-Tracker/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

if __name__ == "__main__":
    success = build_simple()
    if success:
        print("\nTesting executable...")
        exe_path = "dist/BTC-Portfolio-Tracker/BTC-Portfolio-Tracker"
        if os.path.exists(exe_path):
            print(f"Executable found at: {exe_path}")
            print("You can run it with: ./dist/BTC-Portfolio-Tracker/BTC-Portfolio-Tracker")
        else:
            print("Executable not found!")
    else:
        sys.exit(1)
