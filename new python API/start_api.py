#!/usr/bin/env python3
"""
Startup script for the Python Recommendation API (PostgreSQL version)
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "flask",
        "flask_cors",
        "sqlalchemy",
        "psycopg2",
        "pandas",
        "sklearn",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == "flask_cors":
                import flask_cors
            elif package == "sklearn":
                import sklearn
            elif package == "psycopg2":
                import psycopg2
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False

    print("✅ All required packages are installed")
    return True


def check_database_connection():
    """Check if the PostgreSQL database is accessible"""
    try:
        from sqlalchemy import create_engine
        import pandas as pd

        # Database configuration
        host = "localhost"
        user = "postgres"
        password = "1234"
        database = "Macromed"
        port = 5432

        engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        )

        # Try to load products table
        products_df = pd.read_sql("SELECT * FROM products LIMIT 1", engine)
        print(f"✅ Database connection successful. Found {len(products_df)} products")
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("Please ensure:")
        print("1. PostgreSQL server is running")
        print("2. Database exists and is accessible")
        print("3. Products table exists with data")
        print("4. Credentials are correct")
        return False


def start_api():
    """Start the Flask API"""
    print("🚀 Starting Python Recommendation API...")
    print("📍 API will be available at: http://localhost:5000")
    print("📋 Available endpoints:")
    print("   - GET /api/recommend?product_id=<id>&type=<content|price>")
    print(
        "   - Health check: http://localhost:5000/api/recommend?product_id=1&type=content"
    )
    print("\n" + "=" * 50)

    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 API stopped by user")
    except Exception as e:
        print(f"❌ Failed to start API: {e}")


def main():
    """Main entry point"""
    print("🤖 Python Recommendation API Startup")
    print("=" * 50)

    # Ensure app.py exists
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the API directory")
        sys.exit(1)

    # Check dependencies and DB
    if not check_dependencies():
        sys.exit(1)

    if not check_database_connection():
        sys.exit(1)

    # Start the Flask server
    start_api()


if __name__ == "__main__":
    main()
