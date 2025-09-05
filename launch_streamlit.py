#!/usr/bin/env python3
"""
Quick launcher for Streamlit UI
"""

import subprocess
import sys
import os

def main():
    """Launch Streamlit UI with proper error handling."""
    try:
        print("🚀 Starting Streamlit UI for Java & Spring Boot Upgrader Agent...")
        print("📝 Make sure you have installed dependencies: pip install -r requirements.txt")
        print("🌐 The UI will be available at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Run the Streamlit UI
        subprocess.run([sys.executable, "-m", "streamlit", "run", "ui_streamlit.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit UI...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit UI: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
    except FileNotFoundError:
        print("❌ Python not found. Make sure Python is installed and in your PATH.")

if __name__ == "__main__":
    main()
