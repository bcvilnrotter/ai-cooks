---
title: AI Cooks Game
emoji: 🍳
colorFrom: yellow
colorTo: red
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# AI Cooks

A game inspired by Guild Wars 2's crafting system where you combine 4 ingredients to discover new recipes.

## How to Play

1. Select 4 ingredients from the available options
2. Click "Combine Ingredients" to see if they create a valid recipe
3. Discover new ingredients that can be used in future combinations
4. Request new base ingredients if you don't see what you want

## Features

- AI-generated images for ingredients and recipes
- Dynamic recipe validation to determine if combinations "make sense"
- Ability to request new base ingredients
- Discovered recipes become new ingredients for future combinations

## Technical Details

This application uses:

- Gradio for the user interface
- Stable Diffusion for image generation
- Hugging Face models for recipe validation and text generation
- Python for backend logic

## Running Locally

1. Clone the repository
2. Install the dependencies: `pip install -r requirements.txt`
3. Generate placeholder images: `python generate_placeholders.py`
4. Run the application: `python app.py`
5. Open your browser to the URL shown in the terminal (usually http://localhost:7860)

Alternatively, you can use the test script which will check dependencies, generate placeholders, and run the application:

- On Windows: Double-click `test.bat` or run it from the command line
- On macOS/Linux: `python test_app.py`

## Deployment to Hugging Face Spaces

This application is designed to be deployed on Hugging Face Spaces. There are two ways to deploy:

### Method 1: Using the Deployment Script

We've provided a deployment script that automates the process:

1. Install the Hugging Face CLI: `pip install huggingface_hub`
2. Run the deployment script:
   - On Windows: Double-click `deploy.bat` or run it from the command line
   - On macOS/Linux: `python deploy_to_huggingface.py`
3. The script will:
   - Read your Hugging Face token from the specified location
   - Create a new Space if it doesn't exist
   - Push the code to the Space
   - Provide a URL to access your deployed application

### Method 2: Manual Deployment

If you prefer to deploy manually:

1. Create a new Space on Hugging Face
2. Initialize a git repository in this directory
3. Add the Hugging Face Space as a remote
4. Commit and push your code to the Space

The application will be automatically built and deployed by Hugging Face Spaces.

### Accessing Your Deployed Application

Once deployed, your application will be available at:
`https://huggingface.co/spaces/[username]/[space-name]`

## Credits

- Inspired by Guild Wars 2's crafting system
- Uses Hugging Face's Stable Diffusion for image generation
- Built with Gradio for the user interface
