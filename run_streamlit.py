#!/usr/bin/env python
"""
Script to run the Streamlit frontend for the AI Travel Assistant.
"""

import subprocess
import sys
import os
import signal
import time

def check_port_availability(port):
    """Check if a port is available."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def main():
    print("Starting AI Travel Assistant Streamlit Frontend...")
    
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Check if the streamlit app file exists
    if not os.path.exists("streamlit_app.py"):
        print("Error: streamlit_app.py not found in current directory.")
        return
    
    # Check if default Streamlit port (8501) is available
    if not check_port_availability(8501):
        print("Warning: Port 8501 is already in use.")
        choice = input("Would you like to kill the process on port 8501? (y/n): ")
        if choice.lower() == 'y':
            # Kill process on port 8501 (Windows)
            subprocess.run(["netstat", "-ano"], check=False)
            subprocess.run(["taskkill", "/F", "/IM", "streamlit.exe"], check=False)
            time.sleep(2)  # Wait a bit before starting
    
    print("Starting Streamlit app on http://localhost:8501")
    print("Make sure your FastAPI backend is running on http://localhost:8000")
    
    # Run the streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501"])
    except KeyboardInterrupt:
        print("\nStreamlit app stopped.")
    except Exception as e:
        print(f"Error running Streamlit app: {e}")

if __name__ == "__main__":
    main()