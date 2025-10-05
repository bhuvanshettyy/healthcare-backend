#!/usr/bin/env python
"""
Development startup script for Healthcare Backend API
This script now uses PostgreSQL only (SQLite removed).
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the development server with PostgreSQL settings"""
    base_dir = Path(__file__).parent
    os.chdir(base_dir)

    print("Healthcare Backend API - Development Server (PostgreSQL)")
    print("=" * 50)
    print()

    # Check if virtual environment exists
    if not (base_dir / '.venv').exists():
        print("Virtual environment not found!")
        print("Please run: python -m venv .venv")
        sys.exit(1)

    # Show DB env summary
    print("Using PostgreSQL connection:")
    print(f"  POSTGRES_DB       = {os.getenv('POSTGRES_DB', 'healthcare_dev')}")
    print(f"  POSTGRES_USER     = {os.getenv('POSTGRES_USER', 'postgres')}")
    print(f"  POSTGRES_HOST     = {os.getenv('POSTGRES_HOST', 'localhost')}")
    print(f"  POSTGRES_PORT     = {os.getenv('POSTGRES_PORT', '5432')}")
    print()

    # Run migrations
    print("Applying migrations...")
    subprocess.run([
        sys.executable, 'manage.py', 'migrate',
        '--settings=config.settings_dev'
    ], check=True)
    print("Migrations applied successfully!\n")

    print("Starting development server...")
    print("Admin interface: http://127.0.0.1:8000/admin/")
    print("API documentation: http://127.0.0.1:8000/swagger/")
    print("API base URL: http://127.0.0.1:8000/api/v1/")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    try:
        subprocess.run([
            sys.executable, 'manage.py', 'runserver',
            '--settings=config.settings_dev',
            '127.0.0.1:8000'
        ])
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
