#!/usr/bin/env python
"""
Script to update the visibility of a Hugging Face Space.
"""

import os
import sys
import argparse
from huggingface_hub import HfApi

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

def update_space_visibility(token):
    """Update the visibility of the Hugging Face Space."""
    try:
        # Initialize the Hugging Face API
        api = HfApi(token=token)
        
        # Update the space visibility
        print(f"Updating visibility of space {FULL_SPACE_NAME} to public...")
        api.update_repo_visibility(
            repo_id=FULL_SPACE_NAME,
            private=False,
            repo_type="space"
        )
        
        print(f"Successfully updated visibility of space {FULL_SPACE_NAME} to public.")
        print(f"The space is now accessible at: https://huggingface.co/spaces/{FULL_SPACE_NAME}")
        return True
    except Exception as e:
        print(f"Error updating space visibility: {e}")
        return False

def main():
    """Main function to update the visibility of a Hugging Face Space."""
    parser = argparse.ArgumentParser(description="Update the visibility of a Hugging Face Space")
    parser.add_argument("--token-path", default="../.gitignore/.env", help="Path to the file containing the Hugging Face token")
    parser.add_argument("--token-key", default="HUGGINGFACE_TOKEN_CHANGELOG_LLM", help="Key for the Hugging Face token in the file")
    
    args = parser.parse_args()
    
    # Read the token
    token = read_token(args.token_path, args.token_key)
    if token is None:
        return 1
    
    # Update the space visibility
    if not update_space_visibility(token):
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
