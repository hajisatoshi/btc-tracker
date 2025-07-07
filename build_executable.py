#!/usr/bin/env python3
"""
Build script for creating executables for BTC Portfolio Tracker
Creates standalone executables for Windows, macOS, and Linux
"""

import os
import sys
import shutil
import subprocess
import platform

def install_requirements():
    """Install required packages for building"""
    print("Installing build requirements...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

def build_executable():
    """Build the executable"""
    print(f"Building executable for {platform.system()}...")
    
    # Build with PyInstaller
    cmd = [
        'pyinstaller',
        '--clean',
        '--onefile',
        '--windowed',
        '--name', 'BTC-Portfolio-Tracker',
        '--add-data', 'README.md:.',
        '--add-data', 'LICENSE:.',
        '--add-data', 'frontend:frontend',
        '--add-data', 'backend:backend',
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'requests',
        '--hidden-import', 'flask',
        '--hidden-import', 'flask_cors',
        '--hidden-import', 'flask_jwt_extended',
        '--hidden-import', 'werkzeug.security',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'csv',
        '--hidden-import', 'datetime',
        '--hidden-import', 'json',
        '--hidden-import', 'threading',
        '--hidden-import', 'subprocess',
        '--hidden-import', 'secrets',
        '--hidden-import', 'dotenv',
        'main.py'
    ]
    
    # Add icon if available
    if os.path.exists('assets/btc-icon.ico'):
        cmd.extend(['--icon', 'assets/btc-icon.ico'])
    
    subprocess.run(cmd, check=True)
    print("Build completed successfully!")

def create_distribution():
    """Create distribution package"""
    print("Creating distribution package...")
    
    # Create dist directory structure
    dist_dir = 'dist/BTC-Portfolio-Tracker-Package'
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy executable
    system = platform.system()
    if system == 'Windows':
        exe_name = 'BTC-Portfolio-Tracker.exe'
    else:
        exe_name = 'BTC-Portfolio-Tracker'
    
    if os.path.exists(f'dist/{exe_name}'):
        shutil.copy2(f'dist/{exe_name}', f'{dist_dir}/{exe_name}')
    
    # Copy documentation
    files_to_copy = ['README.md', 'LICENSE', 'CHANGELOG.md']
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir)
    
    print(f"Distribution created in {dist_dir}")

def main():
    """Main build function"""
    print("BTC Portfolio Tracker - Build Script")
    print("=" * 50)
    
    try:
        # Install requirements
        install_requirements()
        
        # Build executable
        build_executable()
        
        # Create distribution
        create_distribution()
        
        print("\n" + "=" * 50)
        print("Build completed successfully!")
        print(f"Executable created for {platform.system()}")
        print("Check the 'dist' directory for the output files.")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
