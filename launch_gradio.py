#!/usr/bin/env python3
"""
Quick launcher for Gradio UI
"""

import subprocess
import sys
import os

def main():
    """Launch Gradio UI with proper error handling."""
    try:
        print("🚀 Starting Gradio UI for Java & Spring Boot Upgrader Agent...")
        print("📝 Make sure you have installed dependencies: pip install -r requirements.txt")
        print("🌐 The UI will be available at: http://localhost:7860")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Run the Gradio UI
        subprocess.run([sys.executable, "ui_gradio.py"], check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Gradio UI...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Gradio UI: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
    except FileNotFoundError:
        print("❌ Python not found. Make sure Python is installed and in your PATH.")

if __name__ == "__main__":
    main()
