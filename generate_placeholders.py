#!/usr/bin/env python
"""
Script to generate placeholder images for the base ingredients.
This ensures that the application has images to display even if the image generation API is not available.
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

def load_ingredients():
    """Load the ingredients from the JSON file."""
    try:
        with open("data/ingredients.json", "r") as f:
            data = json.load(f)
        return data.get("base_ingredients", [])
    except Exception as e:
        print(f"Error loading ingredients: {e}")
        return []

def generate_placeholder(ingredient, output_dir):
    """Generate a placeholder image for an ingredient."""
    try:
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get the ingredient ID and name
        ingredient_id = ingredient.get("id", "unknown")
        ingredient_name = ingredient.get("name", "Unknown")
        
        # Get properties for color selection
        properties = ingredient.get("properties", [])
        
        # Choose background color based on ingredient type
        bg_color = (240, 240, 240)  # Default light gray
        if "vegetable" in properties:
            bg_color = (200, 240, 200)  # Light green for vegetables
        elif "fruit" in properties:
            bg_color = (240, 200, 200)  # Light red for fruits
        elif "meat" in properties:
            bg_color = (240, 220, 200)  # Light brown for meats
        elif "grain" in properties:
            bg_color = (240, 230, 180)  # Light yellow for grains
        elif "dairy" in properties:
            bg_color = (230, 230, 250)  # Light blue for dairy
        
        # Create a more visually interesting placeholder image
        img = Image.new("RGB", (200, 200), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a border
        border_color = (80, 80, 80)
        for i in range(4):
            draw.rectangle([i, i, 199-i, 199-i], outline=border_color, width=1)
        
        # Try to use a default font, or use the default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 22)
            font = ImageFont.truetype("arial.ttf", 20)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except IOError:
            title_font = ImageFont.load_default()
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw the ingredient name with a more prominent design
        # Draw a header
        draw.rectangle([0, 0, 200, 30], fill=(50, 50, 60))
        draw.text((10, 5), "AI Cooks", fill=(255, 255, 255), font=title_font)
        
        # Draw ingredient name more prominently in center
        name_width = draw.textlength(ingredient_name, font=font) if hasattr(draw, 'textlength') else len(ingredient_name) * 12
        name_x = (200 - name_width) / 2
        draw.text((name_x, 80), ingredient_name, fill=(0, 0, 0), font=font)
        
        # Draw a visual indicator
        draw.ellipse([75, 120, 125, 170], fill=(180, 180, 180))
        
        # Add properties as tags at the bottom
        if properties:
            props_text = ", ".join(properties[:2])  # Limit to first 2 properties
            draw.text((10, 180), props_text, fill=(80, 80, 80), font=small_font)
        
        # Save the image
        output_path = os.path.join(output_dir, f"{ingredient_id}.png")
        img.save(output_path)
        print(f"Generated placeholder for {ingredient_name} at {output_path}")
        
        return output_path
    except Exception as e:
        print(f"Error generating placeholder for {ingredient.get('name', 'unknown')}: {e}")
        return None

def main():
    """Main function to generate placeholder images for all base ingredients."""
    # Load the ingredients
    ingredients = load_ingredients()
    if not ingredients:
        print("No ingredients found.")
        return
    
    # Create the output directory
    output_dir = os.path.join("assets", "images", "placeholders")
    
    # Generate placeholders for all ingredients
    for ingredient in ingredients:
        generate_placeholder(ingredient, output_dir)
    
    print(f"Generated {len(ingredients)} placeholder images in {output_dir}")

if __name__ == "__main__":
    main()
