#!/usr/bin/env python
"""
Test script for the AI Cooks application.
This script tests the application locally before deployment.
"""

import os
import sys
import subprocess
import time

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_dependencies():
    """Check if all dependencies are installed."""
    print("Checking dependencies...")
    try:
        with open("requirements.txt", "r") as f:
            dependencies = f.read().splitlines()
        
        for dependency in dependencies:
            if dependency and not dependency.startswith("#"):
                package = dependency.split(">=")[0].split("==")[0].strip()
                print(f"Checking {package}...")
                try:
                    __import__(package)
                except ImportError:
                    print(f"Warning: {package} is not installed. Installing...")
                    result = run_command(f"pip install {dependency}")
                    if result is None:
                        print(f"Failed to install {package}.")
                        return False
        
        return True
    except Exception as e:
        print(f"Error checking dependencies: {e}")
        return False

def generate_placeholders():
    """Generate placeholder images for the base ingredients."""
    print("Generating placeholder images...")
    result = run_command("python generate_placeholders.py")
    if result is None:
        print("Failed to generate placeholder images.")
        return False
    return True

def test_app():
    """Test the application locally."""
    print("Testing the application locally...")
    
    # Check if the application is already running
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'python' and 'app.py' in ' '.join(proc.info['cmdline']):
                print(f"Application is already running with PID {proc.info['pid']}.")
                return True
    except ImportError:
        print("psutil is not installed. Skipping process check.")
    
    # Start the application
    print("Starting the application...")
    try:
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for the application to start
        print("Waiting for the application to start...")
        time.sleep(5)
        
        # Check if the application is running
        if process.poll() is None:
            print("Application started successfully.")
            print("Press Ctrl+C to stop the application.")
            
            # Wait for user input
            try:
                process.wait()
            except KeyboardInterrupt:
                print("Stopping the application...")
                process.terminate()
                process.wait()
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"Application failed to start.")
            print(f"Output: {stdout}")
            print(f"Error: {stderr}")
            return False
    except Exception as e:
        print(f"Error testing the application: {e}")
        return False

def main():
    """Main function to test the application locally."""
    # Check dependencies
    if not check_dependencies():
        print("Failed to check dependencies.")
        return 1
    
    # Generate placeholder images
    if not generate_placeholders():
        print("Failed to generate placeholder images.")
        return 1
    
    # Test the application
    if not test_app():
        print("Failed to test the application.")
        return 1
    
    print("Test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
