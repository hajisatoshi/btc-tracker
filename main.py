#!/usr/bin/env python3
"""
BTC Portfolio Tracker - Standalone Launcher
Enhanced version for executable distribution
"""

import os
import sys
import subprocess
import threading
import time
import signal
import atexit
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "frontend"))
sys.path.insert(0, str(current_dir / "backend"))

def find_python_executable():
    """Find the appropriate Python executable"""
    python_executables = ['python', 'python3', 'python.exe']
    
    for executable in python_executables:
        try:
            subprocess.run([executable, '--version'], 
                         capture_output=True, check=True, timeout=5)
            return executable
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return None

def start_backend_server():
    """Start the Flask backend server"""
    try:
        # Import backend modules
        from backend.app import app
        
        print("Starting backend server...")
        # Run Flask app
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
        
    except ImportError as e:
        print(f"Failed to import backend modules: {e}")
        # Try to start using subprocess as fallback
        python_exec = find_python_executable()
        if python_exec:
            backend_file = current_dir / "backend" / "app.py"
            if backend_file.exists():
                subprocess.run([python_exec, str(backend_file)])
    except Exception as e:
        print(f"Backend server error: {e}")

def start_frontend_gui():
    """Start the GUI frontend"""
    try:
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Import frontend modules
        from frontend.btc_gui import main
        
        print("Starting GUI application...")
        main()
        
    except ImportError as e:
        print(f"Failed to import frontend modules: {e}")
        # Try to start using subprocess as fallback
        python_exec = find_python_executable()
        if python_exec:
            frontend_file = current_dir / "frontend" / "btc_gui.py"
            if frontend_file.exists():
                subprocess.run([python_exec, str(frontend_file)])
    except Exception as e:
        print(f"Frontend GUI error: {e}")

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print("\nShutting down BTC Portfolio Tracker...")
        os._exit(0)
    
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except AttributeError:
        # Windows doesn't have all signals
        pass

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'tkinter', 'flask', 'requests', 'sqlite3', 
        'flask_cors', 'flask_jwt_extended', 'werkzeug'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🚀 BTC Portfolio Tracker v2.0")
    print("=" * 60)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return
    
    try:
        # Start backend server in a separate thread
        backend_thread = threading.Thread(target=start_backend_server, daemon=True)
        backend_thread.start()
        
        # Start frontend in main thread
        start_frontend_gui()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
