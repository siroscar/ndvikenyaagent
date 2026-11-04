"""Project configuration — county names, defaults, paths."""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DEFAULT_COUNTY = "Nairobi"
DEFAULT_YEAR = 2023

# Path to save the NDVI map image
OUTPUT_MAP = os.path.join("assets", "ndvi_map.png")

# Common Kenyan counties (extend as needed)
KENYA_COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Uasin Gishu",
    "Turkana", "Machakos", "Kiambu", "Kilifi", "Bungoma", "Meru"
]