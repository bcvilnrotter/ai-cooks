import os
import io
import base64
from typing import Optional, Tuple
import time
import random
import string
import logging
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import diffusers conditionally to handle environments where it might not be available
try:
    from diffusers import StableDiffusionPipeline
    import torch
    DIFFUSERS_AVAILABLE = True
    logger.info("Diffusers and torch are available for image generation")
except ImportError as e:
    logger.error(f"Error importing diffusers/torch: {e}")
    DIFFUSERS_AVAILABLE = False

class ImageGenerator:
    """
    Handles AI image generation for ingredients and recipes.
    """
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5", cache_dir: str = "assets/images"):
        """
        Initialize the image generator.
        
        Args:
            model_id: The Hugging Face model ID to use for image generation
            cache_dir: Directory to cache generated images
        """
        self.model_id = model_id
        self.cache_dir = cache_dir
        self.pipeline = None
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize the pipeline if diffusers is available
        if DIFFUSERS_AVAILABLE:
            try:
                self._initialize_pipeline()
            except Exception as e:
                print(f"Warning: Could not initialize image generation pipeline: {e}")
                print("Will use fallback image generation method.")
    
    def _initialize_pipeline(self):
        """Initialize the Stable Diffusion pipeline."""
        if not DIFFUSERS_AVAILABLE:
            return
        
        # Use CUDA if available, otherwise use CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the pipeline
        self.pipeline = StableDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        self.pipeline = self.pipeline.to(device)
        
        # Enable memory efficient attention if using CUDA
        if device == "cuda":
            self.pipeline.enable_attention_slicing()
    
    def _generate_image_id(self) -> str:
        """Generate a unique ID for an image."""
        timestamp = int(time.time())
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"{timestamp}_{random_str}"
    
    def generate_image(self, prompt: str, negative_prompt: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate an image based on the given prompt.
        
        Args:
            prompt: The text prompt to generate an image from
            negative_prompt: Optional negative prompt to guide generation
            
        Returns:
            Tuple of (image_path, image_base64) or (None, None) if generation fails
        """
        # Enhanced prompt for better food images
        enhanced_prompt = f"{prompt}, food photography, professional lighting, high resolution, detailed texture"
        
        # Default negative prompt for food images if none provided
        if negative_prompt is None:
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy"
        
        # Generate a unique ID for this image
        image_id = self._generate_image_id()
        image_path = os.path.join(self.cache_dir, f"{image_id}.png")
        
        # Try to generate the image using the pipeline
        if DIFFUSERS_AVAILABLE and self.pipeline is not None:
            try:
                # Generate the image
                image = self.pipeline(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=30,
                    guidance_scale=7.5
                ).images[0]
                
                # Save the image
                image.save(image_path)
                
                # Convert to base64 for display
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                return image_path, img_base64
            
            except Exception as e:
                print(f"Error generating image: {e}")
                return self._generate_fallback_image(image_id)
        else:
            # Use fallback method if pipeline is not available
            return self._generate_fallback_image(image_id)
    
    def _generate_fallback_image(self, image_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate a fallback image when the pipeline is not available.
        This uses the Hugging Face Inference API if possible, or creates a placeholder.
        
        Args:
            image_id: The unique ID for the image
            
        Returns:
            Tuple of (image_path, image_base64) or (None, None) if generation fails
        """
        try:
            # Create a simple placeholder image
            image_path = os.path.join(self.cache_dir, f"{image_id}.png")
            
            # Create a colored placeholder image
            img = Image.new('RGB', (512, 512), color=(
                random.randint(200, 255),
                random.randint(200, 255),
                random.randint(200, 255)
            ))
            
            # Add some text to the image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, or use the default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((10, 10), "AI Cooks", fill=(0, 0, 0), font=font)
            draw.text((10, 40), "Image placeholder", fill=(0, 0, 0), font=font)
            
            # Save the image
            img.save(image_path)
            
            # Convert to base64 for display
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            return image_path, img_base64
        
        except Exception as e:
            print(f"Error generating fallback image: {e}")
            return None, None
    
    def get_image_base64(self, image_path: str) -> Optional[str]:
        """
        Get the base64 encoding of an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string or None if the file doesn't exist
        """
        if not os.path.exists(image_path):
            return None
        
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            print(f"Error reading image file: {e}")
            return None
