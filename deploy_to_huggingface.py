#!/usr/bin/env python
"""
Deployment script for AI Cooks to Hugging Face Spaces.
This script handles the deployment of the AI Cooks application to Hugging Face Spaces.
"""

import os
import sys
import subprocess
import argparse
import tempfile
import shutil
from pathlib import Path
from huggingface_hub import HfApi, create_repo, upload_folder

# Space details
SPACE_NAME = "ai-cooks-game"
ACCOUNT_NAME = "bcvilnrotter"
FULL_SPACE_NAME = f"{ACCOUNT_NAME}/{SPACE_NAME}"

def read_token(token_path, token_key):
    """Read the Hugging Face token from the specified file."""
    try:
        # Get the absolute path
        token_path = os.path.abspath(token_path)
        
        # Check if the file exists
        if not os.path.exists(token_path):
            print(f"Error: Token file not found at {token_path}")
            return None
        
        # Read the file
        with open(token_path, 'r') as f:
            lines = f.readlines()
        
        # Find the line with the token
        for line in lines:
            if token_key in line:
                # Extract the token
                token = line.strip().split('=')[1].strip().strip('"').strip("'")
                return token
        
        print(f"Error: Token key '{token_key}' not found in {token_path}")
        return None
    
    except Exception as e:
        print(f"Error reading token: {e}")
        return None

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

def generate_placeholders():
    """Generate placeholder images for the base ingredients."""
    print("Generating placeholder images...")
    try:
        result = run_command("python generate_placeholders.py")
        if result is None:
            print("Warning: Failed to generate placeholder images. Continuing with deployment...")
        return True
    except Exception as e:
        print(f"Warning: Error generating placeholder images: {e}. Continuing with deployment...")
        return True

def deploy_to_space(token):
    """Deploy the application to the Hugging Face Space."""
    print(f"Deploying to {FULL_SPACE_NAME}...")
    
    # Generate placeholder images
    generate_placeholders()
    
    try:
        # Initialize the Hugging Face API
        api = HfApi(token=token)
        
        # Create the space if it doesn't exist
        try:
            print(f"Checking if space {FULL_SPACE_NAME} exists...")
            api.repo_info(repo_id=FULL_SPACE_NAME, repo_type="space")
            print(f"Space {FULL_SPACE_NAME} already exists.")
        except Exception:
            print(f"Space {FULL_SPACE_NAME} doesn't exist. Creating...")
            create_repo(
                repo_id=FULL_SPACE_NAME,
                token=token,
                repo_type="space",
                space_sdk="gradio",
                private=False  # Make the space public so it's accessible
            )
            print(f"Successfully created space {FULL_SPACE_NAME}.")
        
        # Upload the files to the space
        print("Uploading files to the space...")
        upload_folder(
            folder_path=".",
            repo_id=FULL_SPACE_NAME,
            repo_type="space",
            token=token,
            ignore_patterns=[".git", ".gitignore", "__pycache__", "*.pyc", "*.pyo", "*.pyd", ".DS_Store", "deploy_to_huggingface.py", "deploy.bat", "test_app.py", "test.bat"]
        )
        
        print(f"Successfully deployed to https://huggingface.co/spaces/{FULL_SPACE_NAME}")
        return True
    except Exception as e:
        print(f"Error deploying to Hugging Face Spaces: {e}")
        return False

def main():
    """Main function to deploy the application to Hugging Face Spaces."""
    parser = argparse.ArgumentParser(description="Deploy AI Cooks to Hugging Face Spaces")
    parser.add_argument("--token-path", default="../.gitignore/.env", help="Path to the file containing the Hugging Face token")
    parser.add_argument("--token-key", default="HUGGINGFACE_TOKEN_CHANGELOG_LLM", help="Key for the Hugging Face token in the file")
    
    args = parser.parse_args()
    
    # Read the token
    token = read_token(args.token_path, args.token_key)
    if token is None:
        return 1
    
    # Deploy to the space
    if not deploy_to_space(token):
        return 1
    
    print("Deployment completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
