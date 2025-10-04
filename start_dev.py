#!/usr/bin/env python
"""
Development startup script for Healthcare Backend API
This script provides an easy way to start the development server with SQLite
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the development server with proper settings"""
    
    # Ensure we're in the right directory
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    print("🏥 Healthcare Backend API - Development Server")
    print("=" * 50)
    print()
    
    # Check if virtual environment exists
    if not (base_dir / '.venv').exists():
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv .venv")
        sys.exit(1)
    
    # Check if SQLite database exists, create if not
    db_path = base_dir / 'db.sqlite3'
    if not db_path.exists():
        print("📊 Creating SQLite database...")
        subprocess.run([
            sys.executable, 'manage.py', 'migrate', 
            '--settings=config.settings_dev'
        ], check=True)
        print("✅ Database created successfully!")
        print()
    
    print("🚀 Starting development server...")
    print("📍 Admin interface: http://127.0.0.1:8000/admin/")
    print("📚 API documentation: http://127.0.0.1:8000/swagger/")
    print("🔗 API base URL: http://127.0.0.1:8000/api/v1/")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the development server
        subprocess.run([
            sys.executable, 'manage.py', 'runserver', 
            '--settings=config.settings_dev',
            '127.0.0.1:8000'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()