import json
import os
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Storage:
    """
    Handles data storage operations for ingredients and recipes.
    """
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the storage with the data directory path.
        
        Args:
            data_dir: Directory where data files are stored
        """
        self.data_dir = data_dir
        self.ingredients_file = os.path.join(data_dir, "ingredients.json")
        self.recipes_file = os.path.join(data_dir, "recipes.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        if not os.path.exists(self.ingredients_file):
            self._initialize_ingredients_file()
        
        if not os.path.exists(self.recipes_file):
            self._initialize_recipes_file()
    
    def _initialize_ingredients_file(self):
        """Create an empty ingredients file with the basic structure."""
        data = {
            "base_ingredients": [],
            "discovered_ingredients": []
        }
        with open(self.ingredients_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _initialize_recipes_file(self):
        """Create an empty recipes file with the basic structure."""
        data = {
            "recipes": []
        }
        with open(self.recipes_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_all_ingredients(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all ingredients (base and discovered).
        
        Returns:
            Dictionary containing base_ingredients and discovered_ingredients lists
        """
        with open(self.ingredients_file, 'r') as f:
            return json.load(f)
    
    def get_base_ingredients(self) -> List[Dict[str, Any]]:
        """
        Get only the base ingredients.
        
        Returns:
            List of base ingredients
        """
        with open(self.ingredients_file, 'r') as f:
            data = json.load(f)
            return data.get("base_ingredients", [])
    
    def get_discovered_ingredients(self) -> List[Dict[str, Any]]:
        """
        Get only the discovered ingredients.
        
        Returns:
            List of discovered ingredients
        """
        with open(self.ingredients_file, 'r') as f:
            data = json.load(f)
            return data.get("discovered_ingredients", [])
    
    def get_ingredient_by_id(self, ingredient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific ingredient by its ID.
        
        Args:
            ingredient_id: The ID of the ingredient to find
            
        Returns:
            The ingredient data or None if not found
        """
        all_ingredients = self.get_all_ingredients()
        
        # Check base ingredients
        for ingredient in all_ingredients.get("base_ingredients", []):
            if ingredient.get("id") == ingredient_id:
                return ingredient
        
        # Check discovered ingredients
        for ingredient in all_ingredients.get("discovered_ingredients", []):
            if ingredient.get("id") == ingredient_id:
                return ingredient
        
        return None
    
    def add_discovered_ingredient(self, ingredient: Dict[str, Any]) -> bool:
        """
        Add a new discovered ingredient.
        
        Args:
            ingredient: The ingredient data to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.ingredients_file, 'r') as f:
                data = json.load(f)
            
            # Check if ingredient with same ID already exists
            for existing in data.get("discovered_ingredients", []):
                if existing.get("id") == ingredient.get("id"):
                    return False
            
            # Add the new ingredient
            data["discovered_ingredients"].append(ingredient)
            
            # Save the updated data
            with open(self.ingredients_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding discovered ingredient: {e}")
            return False
    
    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """
        Get all discovered recipes.
        
        Returns:
            List of recipes
        """
        with open(self.recipes_file, 'r') as f:
            data = json.load(f)
            return data.get("recipes", [])
    
    def add_recipe(self, recipe: Dict[str, Any]) -> bool:
        """
        Add a new recipe.
        
        Args:
            recipe: The recipe data to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.recipes_file, 'r') as f:
                data = json.load(f)
            
            # Check if recipe with same ID already exists
            for existing in data.get("recipes", []):
                if existing.get("id") == recipe.get("id"):
                    return False
            
            # Add the new recipe
            data["recipes"].append(recipe)
            
            # Save the updated data
            with open(self.recipes_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding recipe: {e}")
            return False
    
    def get_recipe_by_ingredients(self, ingredient_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find a recipe that uses the exact set of ingredients.
        
        Args:
            ingredient_ids: List of ingredient IDs
            
        Returns:
            The recipe data or None if not found
        """
        # Sort the ingredient IDs for consistent comparison
        sorted_ids = sorted(ingredient_ids)
        
        recipes = self.get_all_recipes()
        for recipe in recipes:
            recipe_ingredients = recipe.get("ingredients", [])
            recipe_ids = [ing.get("id") for ing in recipe_ingredients]
            if sorted(recipe_ids) == sorted_ids:
                return recipe
        
        return None
