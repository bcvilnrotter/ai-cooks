import os
import gradio as gr
import json
import time
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import base64
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our utility modules
from utils.storage import Storage
from utils.image_generation import ImageGenerator
from utils.recipe_validation import RecipeValidator

# Initialize our utility classes
storage = Storage()
image_generator = ImageGenerator()
recipe_validator = RecipeValidator()

# Create directories if they don't exist
os.makedirs("assets/images", exist_ok=True)

# Constants
MAX_INGREDIENTS = 4

def get_ingredient_image(ingredient: Dict[str, Any]) -> Optional[str]:
    """Get the image for an ingredient as a base64 string."""
    try:
        # First check for a direct URL
        image_url = ingredient.get("image_url")
        if image_url:
            logger.info(f"Using image URL for {ingredient.get('name')}: {image_url}")
            return image_url
        
        # Next check for an image path
        if "image_path" in ingredient and ingredient["image_path"]:
            image_path = ingredient["image_path"]
            logger.info(f"Using image path for {ingredient.get('name')}: {image_path}")
            
            # Verify the file exists
            if os.path.exists(image_path):
                return image_generator.get_image_base64(image_path)
            else:
                logger.warning(f"Image path does not exist: {image_path}")
                
        # Check the placeholder directory for an image with this ingredient's ID
        ingredient_id = ingredient.get("id")
        if ingredient_id:
            placeholder_path = os.path.join("assets", "images", "placeholders", f"{ingredient_id}.png")
            if os.path.exists(placeholder_path):
                logger.info(f"Using placeholder image for {ingredient.get('name')}: {placeholder_path}")
                with open(placeholder_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            else:
                logger.warning(f"Placeholder image not found: {placeholder_path}")
        
        # If all else fails, create a dynamic placeholder
        logger.info(f"Creating dynamic placeholder for {ingredient.get('name')}")
        
        # Use ingredient properties to determine colors if available
        properties = ingredient.get("properties", [])
        bg_color = (240, 240, 240)  # Default light gray
        
        if properties:
            if "vegetable" in properties or "fruit" in properties:
                bg_color = (200, 240, 200)  # Light green
            elif "meat" in properties:
                bg_color = (240, 220, 200)  # Light brown
            elif "grain" in properties:
                bg_color = (240, 230, 180)  # Light yellow
            elif "dairy" in properties:
                bg_color = (230, 230, 250)  # Light blue
        
        img = Image.new('RGB', (200, 200), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        # Add a border
        for i in range(4):
            draw.rectangle([i, i, 199-i, 199-i], outline=(80, 80, 80), width=1)
            
        # Try to use a font, or default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
            
        # Add ingredient name
        name = ingredient.get("name", "Unknown")
        text_width = draw.textlength(name, font=font) if hasattr(draw, 'textlength') else len(name) * 12
        text_x = (200 - text_width) / 2
        draw.text((text_x, 80), name, fill=(0, 0, 0), font=font)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error(f"Error getting image for {ingredient.get('name')}: {e}")
        # Return an emergency placeholder if all else fails
        img = Image.new('RGB', (200, 200), color=(255, 0, 0))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

def get_all_ingredients():
    """Get all ingredients with their images."""
    all_ingredients = storage.get_all_ingredients()
    base_ingredients = all_ingredients.get("base_ingredients", [])
    discovered_ingredients = all_ingredients.get("discovered_ingredients", [])
    
    # Add images to ingredients
    for ingredient in base_ingredients + discovered_ingredients:
        ingredient["image"] = get_ingredient_image(ingredient)
    
    return base_ingredients, discovered_ingredients

def combine_ingredients(selected: List[Dict[str, Any]]) -> Tuple[Optional[str], str, str, str]:
    """Combine selected ingredients to create a recipe."""
    # Check if we have the right number of ingredients
    if len(selected) != MAX_INGREDIENTS:
        return None, "Incomplete Recipe", f"Please select exactly {MAX_INGREDIENTS} ingredients to combine.", ""
    
    # Check if this combination already exists
    existing_recipe = storage.get_recipe_by_ingredients([ing.get("id") for ing in selected])
    if existing_recipe:
        # Return the existing recipe
        image = get_ingredient_image(existing_recipe)
        ingredients_text = ", ".join([ing.get("name", "Unknown") for ing in existing_recipe.get("ingredients", [])])
        return (
            f"data:image/png;base64,{image}" if image else None,
            existing_recipe.get("name", "Unknown Recipe"),
            existing_recipe.get("description", ""),
            f"Ingredients: {ingredients_text}"
        )
    
    # Validate and generate a new recipe
    recipe = recipe_validator.generate_recipe(selected)
    
    if recipe:
        # Generate an image for the recipe
        image_path, image_base64 = image_generator.generate_image(recipe["image_prompt"])
        
        if image_path:
            recipe["image_path"] = image_path
        
        # Save the recipe
        storage.add_recipe(recipe)
        
        # Also add the recipe as a discovered ingredient
        new_ingredient = {
            "id": recipe["id"],
            "name": recipe["name"],
            "description": recipe["description"],
            "image_prompt": recipe["image_prompt"],
            "image_path": image_path if image_path else None,
            "image_url": None,
            "properties": []  # We could derive properties from the ingredients
        }
        
        storage.add_discovered_ingredient(new_ingredient)
        
        # Return the recipe details
        ingredients_text = ", ".join([ing.get("name", "Unknown") for ing in recipe.get("ingredients", [])])
        return (
            f"data:image/png;base64,{image_base64}" if image_base64 else None,
            recipe.get("name", "Unknown Recipe"),
            recipe.get("description", ""),
            f"Ingredients: {ingredients_text}"
        )
    else:
        # The combination is not valid
        return None, "Invalid Combination", "This combination of ingredients doesn't work. Try a different combination!", ""

def request_new_ingredient(name: str, description: str) -> str:
    """Handle a request for a new ingredient."""
    if not name or not description:
        return "Please provide both a name and description for the new ingredient."
    
    # Generate an ID for the new ingredient
    ingredient_id = name.lower().replace(" ", "_")
    
    # Check if an ingredient with this ID already exists
    existing = storage.get_ingredient_by_id(ingredient_id)
    if existing:
        return f"An ingredient named '{name}' already exists."
    
    # Create the new ingredient
    new_ingredient = {
        "id": ingredient_id,
        "name": name,
        "description": description,
        "image_prompt": f"A {name} ingredient for cooking, photorealistic",
        "image_url": None,
        "properties": []  # We could ask for properties or generate them
    }
    
    # Generate an image for the ingredient
    image_path, _ = image_generator.generate_image(new_ingredient["image_prompt"])
    
    if image_path:
        new_ingredient["image_path"] = image_path
    
    # Add the new ingredient
    if storage.add_discovered_ingredient(new_ingredient):
        return f"Successfully added new ingredient: {name}"
    else:
        return f"Failed to add new ingredient: {name}"

def create_ui():
    """Create the Gradio interface."""
    # Create a simple interface
    with gr.Blocks(title="AI Cooks") as app:
        gr.Markdown("# AI Cooks")
        gr.Markdown("Combine 4 ingredients to discover new recipes!")
        
        # Create state for selected ingredients
        selected_ingredients = gr.State([])
        
        # Display base ingredients
        gr.Markdown("## Base Ingredients")
        base_ingredients, _ = get_all_ingredients()
        
        ingredients_gallery = []
        with gr.Row():
            for i in range(min(4, len(base_ingredients))):
                with gr.Column():
                    ing = base_ingredients[i]
                    # Create a placeholder image if needed
                    image_path = None
                    if ing.get("image_path") and os.path.exists(ing["image_path"]):
                        image_path = ing["image_path"]
                    else:
                        # Create a placeholder image
                        placeholder_dir = os.path.join("assets", "images", "placeholders")
                        os.makedirs(placeholder_dir, exist_ok=True)
                        placeholder_path = os.path.join(placeholder_dir, f"{ing['id']}.png")
                        
                        if not os.path.exists(placeholder_path):
                            img = Image.new('RGB', (200, 200), color=(240, 240, 240))
                            img.save(placeholder_path)
                        
                        image_path = placeholder_path
                    
                    img = gr.Image(value=image_path, elem_id=f"img_{ing['id']}")
                    ingredients_gallery.append(img)
                    gr.Markdown(f"**{ing['name']}**")
                    gr.Markdown(ing['description'])
        
        # Simple recipe creation form
        gr.Markdown("## Create a Recipe")
        with gr.Row():
            with gr.Column():
                ingredient1 = gr.Dropdown([ing['name'] for ing in base_ingredients], label="Ingredient 1")
                ingredient2 = gr.Dropdown([ing['name'] for ing in base_ingredients], label="Ingredient 2")
            with gr.Column():
                ingredient3 = gr.Dropdown([ing['name'] for ing in base_ingredients], label="Ingredient 3")
                ingredient4 = gr.Dropdown([ing['name'] for ing in base_ingredients], label="Ingredient 4")
        
        combine_button = gr.Button("Combine Ingredients")
        
        # Result area
        with gr.Group():
            result_image = gr.Image(label="Recipe Image")
            result_name = gr.Textbox(label="Recipe Name")
            result_description = gr.Textbox(label="Description")
            result_ingredients = gr.Textbox(label="Ingredients")
        
        # New ingredient request form
        with gr.Accordion("Request New Ingredient", open=False):
            gr.Markdown("Don't see an ingredient you want? Request a new one!")
            with gr.Row():
                name_input = gr.Textbox(label="Ingredient Name")
                desc_input = gr.Textbox(label="Description")
            request_button = gr.Button("Request Ingredient")
            request_result = gr.Textbox(label="Result", interactive=False)
        
        # Handle combine button click
        def on_combine(ing1, ing2, ing3, ing4):
            # Find the ingredient data for each selected ingredient
            selected = []
            missing = []
            
            # Check which ingredients are missing or not selected
            for i, name in enumerate([ing1, ing2, ing3, ing4]):
                if not name:
                    missing.append(f"Ingredient {i+1}")
                    continue
                    
                found = False
                for ing in base_ingredients:
                    if ing['name'] == name:
                        selected.append(ing)
                        found = True
                        break
                
                if not found:
                    logger.warning(f"Could not find ingredient with name: {name}")
            
            # Log what's happening
            logger.info(f"Selected {len(selected)} ingredients for recipe combination")
            
            # Combine the ingredients
            if len(selected) == MAX_INGREDIENTS:
                logger.info(f"Combining ingredients: {', '.join([ing.get('name', 'Unknown') for ing in selected])}")
                image, name, description, ingredients_text = combine_ingredients(selected)
                
                # Convert data URL to file path if needed
                if image and isinstance(image, str) and image.startswith("data:image/png;base64,"):
                    # Create a placeholder image
                    placeholder_dir = os.path.join("assets", "images", "recipes")
                    os.makedirs(placeholder_dir, exist_ok=True)
                    recipe_id = f"recipe_{int(time.time())}"
                    placeholder_path = os.path.join(placeholder_dir, f"{recipe_id}.png")
                    
                    try:
                        # Decode base64 and save image
                        image_data = base64.b64decode(image.split(",")[1])
                        with open(placeholder_path, "wb") as f:
                            f.write(image_data)
                        
                        image = placeholder_path
                        logger.info(f"Recipe image saved to {placeholder_path}")
                    except Exception as e:
                        logger.error(f"Error saving recipe image: {e}")
                
                return image, name, description, ingredients_text
            else:
                if missing:
                    return None, "Incomplete Recipe", f"Please select ingredients for: {', '.join(missing)}", ""
                return None, "Incomplete Recipe", "Please select 4 different ingredients.", ""
        
        combine_button.click(
            fn=on_combine,
            inputs=[ingredient1, ingredient2, ingredient3, ingredient4],
            outputs=[result_image, result_name, result_description, result_ingredients]
        )
        
        # Handle new ingredient request
        request_button.click(
            fn=request_new_ingredient,
            inputs=[name_input, desc_input],
            outputs=request_result
        )
    
    return app

# Create and launch the app
if __name__ == "__main__":
    app = create_ui()
    app.launch()  # Local development only, no sharing
