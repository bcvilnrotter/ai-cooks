from typing import List, Dict, Any, Tuple, Optional
import random
import string
import time
import hashlib
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import transformers for LLM-based validation
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers is available for recipe validation")
except ImportError as e:
    logger.error(f"Error importing transformers: {e}")
    TRANSFORMERS_AVAILABLE = False

class RecipeValidator:
    """
    Handles validation of ingredient combinations and generation of new recipes.
    """
    def __init__(self, model_name: str = "google/flan-t5-small"):
        """
        Initialize the recipe validator.
        
        Args:
            model_name: The Hugging Face model to use for recipe validation
        """
        self.model_name = model_name
        self.llm = None
        
        # Initialize the LLM if transformers is available
        if TRANSFORMERS_AVAILABLE:
            try:
                self._initialize_llm()
            except Exception as e:
                print(f"Warning: Could not initialize LLM for recipe validation: {e}")
                print("Will use fallback validation method.")
    
    def _initialize_llm(self):
        """Initialize the language model for recipe validation."""
        if not TRANSFORMERS_AVAILABLE:
            return
        
        # Initialize the text generation pipeline
        self.llm = pipeline(
            "text2text-generation",
            model=self.model_name,
            max_length=100
        )
    
    def _generate_recipe_id(self, ingredient_ids: List[str]) -> str:
        """
        Generate a unique ID for a recipe based on its ingredients.
        
        Args:
            ingredient_ids: List of ingredient IDs
            
        Returns:
            A unique recipe ID
        """
        # Sort the ingredient IDs for consistency
        sorted_ids = sorted(ingredient_ids)
        
        # Create a string representation of the sorted IDs
        id_string = "_".join(sorted_ids)
        
        # Create a hash of the ID string
        hash_object = hashlib.md5(id_string.encode())
        hash_hex = hash_object.hexdigest()
        
        # Return a shortened version of the hash
        return f"recipe_{hash_hex[:8]}"
    
    def validate_combination(self, ingredients: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validate if a combination of ingredients makes sense as a recipe.
        
        Args:
            ingredients: List of ingredient data dictionaries
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if we have exactly 4 ingredients
        if len(ingredients) != 4:
            return False, "A recipe must have exactly 4 ingredients."
        
        # Extract ingredient names and properties
        ingredient_names = [ing.get("name", "") for ing in ingredients]
        all_properties = []
        for ing in ingredients:
            all_properties.extend(ing.get("properties", []))
        
        # Use LLM-based validation if available
        if TRANSFORMERS_AVAILABLE and self.llm is not None:
            return self._validate_with_llm(ingredient_names, all_properties)
        else:
            # Use fallback rule-based validation
            return self._validate_with_rules(ingredient_names, all_properties)
    
    def _validate_with_llm(self, ingredient_names: List[str], properties: List[str]) -> Tuple[bool, str]:
        """
        Validate a recipe combination using a language model.
        
        Args:
            ingredient_names: List of ingredient names
            properties: List of all ingredient properties
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            # Create a prompt for the LLM
            prompt = f"Can these ingredients be combined into a recipe? Ingredients: {', '.join(ingredient_names)}. Answer with 'Yes' or 'No' and explain why."
            
            # Generate a response
            response = self.llm(prompt)[0]["generated_text"]
            
            # Parse the response
            if "yes" in response.lower():
                return True, response
            else:
                return False, response
        
        except Exception as e:
            print(f"Error validating with LLM: {e}")
            # Fall back to rule-based validation
            return self._validate_with_rules(ingredient_names, properties)
    
    def _validate_with_rules(self, ingredient_names: List[str], properties: List[str]) -> Tuple[bool, str]:
        """
        Validate a recipe combination using rule-based logic.
        
        Args:
            ingredient_names: List of ingredient names
            properties: List of all ingredient properties
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Count property occurrences
        property_counts = {}
        for prop in properties:
            property_counts[prop] = property_counts.get(prop, 0) + 1
        
        # Rule 1: Check for incompatible combinations
        incompatible_pairs = [
            ("meat", "vegetable"),  # This is actually compatible, but just as an example
        ]
        
        for prop1, prop2 in incompatible_pairs:
            if prop1 in properties and prop2 in properties:
                return False, f"Incompatible combination: {prop1} and {prop2} don't work well together."
        
        # Rule 2: Need at least one binding or liquid ingredient
        if "binding" not in properties and "liquid" not in properties:
            # Actually, let's make this valid 70% of the time for more interesting combinations
            if random.random() > 0.3:
                return True, "This unusual combination might work!"
            return False, "Recipe needs at least one binding or liquid ingredient."
        
        # Rule 3: Too many of the same property might be unbalanced
        for prop, count in property_counts.items():
            if count >= 3 and prop in ["sweet", "acidic", "pungent"]:
                # Make it valid 50% of the time
                if random.random() > 0.5:
                    return True, "This intense combination could work!"
                return False, f"Too many {prop} ingredients make this unbalanced."
        
        # Default to valid with some randomness for more interesting gameplay
        # 80% chance of being valid if it passed all the rules
        if random.random() < 0.8:
            return True, "These ingredients combine well together."
        else:
            return False, "These ingredients don't quite work together."
    
    def generate_recipe(self, ingredients: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Generate a new recipe from a combination of ingredients.
        
        Args:
            ingredients: List of ingredient data dictionaries
            
        Returns:
            Recipe data dictionary or None if invalid
        """
        logger.info(f"Validating ingredient combination for recipe generation")
        
        # Check if we have exactly 4 ingredients
        if len(ingredients) != 4:
            logger.warning(f"Invalid number of ingredients: {len(ingredients)}")
            return None
        
        # Log the ingredient names we're validating
        ingredient_names = [ing.get("name", "Unknown") for ing in ingredients]
        logger.info(f"Validating combination: {', '.join(ingredient_names)}")
        
        # Validate the combination
        is_valid, reason = self.validate_combination(ingredients)
        
        if not is_valid:
            logger.warning(f"Invalid combination: {reason}")
            return None
        
        logger.info(f"Valid combination: {reason}")
        
        # Extract ingredient names and properties
        ingredient_names = [ing.get("name", "") for ing in ingredients]
        all_properties = []
        for ing in ingredients:
            all_properties.extend(ing.get("properties", []))
        
        # Generate a recipe name
        recipe_name = self._generate_recipe_name(ingredient_names, all_properties)
        
        # Generate a recipe description
        recipe_description = self._generate_recipe_description(ingredient_names, all_properties)
        
        # Generate a recipe image prompt
        image_prompt = self._generate_recipe_image_prompt(recipe_name, ingredient_names)
        
        # Create the recipe data
        recipe_id = self._generate_recipe_id([ing.get("id", "") for ing in ingredients])
        
        recipe = {
            "id": recipe_id,
            "name": recipe_name,
            "description": recipe_description,
            "ingredients": ingredients,
            "image_prompt": image_prompt,
            "image_url": None,
            "created_at": int(time.time())
        }
        
        return recipe
    
    def _generate_recipe_name(self, ingredient_names: List[str], properties: List[str]) -> str:
        """
        Generate a name for a recipe based on its ingredients.
        
        Args:
            ingredient_names: List of ingredient names
            properties: List of all ingredient properties
            
        Returns:
            A recipe name
        """
        # Use LLM if available
        if TRANSFORMERS_AVAILABLE and self.llm is not None:
            try:
                prompt = f"Create a creative recipe name using these ingredients: {', '.join(ingredient_names)}."
                response = self.llm(prompt)[0]["generated_text"]
                return response.strip()
            except Exception:
                pass
        
        # Fallback method
        cooking_methods = ["Baked", "Fried", "Grilled", "Roasted", "Sautéed", "Stewed", "Steamed"]
        dish_types = ["Delight", "Surprise", "Special", "Fusion", "Creation", "Medley", "Mix"]
        
        # Choose a random cooking method and dish type
        method = random.choice(cooking_methods)
        dish_type = random.choice(dish_types)
        
        # Choose 1-2 random ingredients to feature in the name
        featured_ingredients = random.sample(ingredient_names, min(2, len(ingredient_names)))
        
        # Generate the name
        if len(featured_ingredients) == 1:
            return f"{method} {featured_ingredients[0]} {dish_type}"
        else:
            return f"{method} {featured_ingredients[0]} & {featured_ingredients[1]} {dish_type}"
    
    def _generate_recipe_description(self, ingredient_names: List[str], properties: List[str]) -> str:
        """
        Generate a description for a recipe based on its ingredients.
        
        Args:
            ingredient_names: List of ingredient names
            properties: List of all ingredient properties
            
        Returns:
            A recipe description
        """
        # Use LLM if available
        if TRANSFORMERS_AVAILABLE and self.llm is not None:
            try:
                prompt = f"Write a short, appetizing description for a dish made with: {', '.join(ingredient_names)}."
                response = self.llm(prompt)[0]["generated_text"]
                return response.strip()
            except Exception:
                pass
        
        # Fallback method
        adjectives = ["delicious", "mouthwatering", "flavorful", "tasty", "savory", "delightful", "exquisite"]
        cooking_verbs = ["combined", "mixed", "blended", "fused", "incorporated", "integrated"]
        
        # Choose random words
        adjective = random.choice(adjectives)
        verb = random.choice(cooking_verbs)
        
        # Generate the description
        return f"A {adjective} dish where {ingredient_names[0]}, {ingredient_names[1]}, {ingredient_names[2]}, and {ingredient_names[3]} are {verb} to create a unique culinary experience."
    
    def _generate_recipe_image_prompt(self, recipe_name: str, ingredient_names: List[str]) -> str:
        """
        Generate an image prompt for a recipe.
        
        Args:
            recipe_name: The name of the recipe
            ingredient_names: List of ingredient names
            
        Returns:
            An image generation prompt
        """
        return f"{recipe_name} made with {', '.join(ingredient_names)}, food photography, professional lighting, high resolution, detailed texture"
