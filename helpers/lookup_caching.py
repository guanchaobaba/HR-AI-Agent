import os
import json
import hashlib
from utils.logger import logger


def get_image_id(image_path: str) -> str:
    """Generate a short unique ID based on the image filename."""
    # Extract just the filename, not the full path
    filename = os.path.basename(image_path)
    # Create a unique but shorter ID
    return hashlib.md5(filename.encode()).hexdigest()[:10]


def load_cache(cache_path: str) -> dict:
    """Load JSON cache or return empty dict."""
    try:
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in cache file: {str(e)}")
        # Backup corrupted file
        if os.path.exists(cache_path):
            os.rename(cache_path, f"{cache_path}.bak")
    return {}


def save_cache(cache: dict, cache_path: str) -> None:
    """Persist cache dict to disk."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    # Convert NumPy int64 values to regular Python ints
    sanitized_cache = {}
    for key, value in cache.items():
        if isinstance(value, list):
            # Convert each coordinate to regular int
            sanitized_cache[key] = [int(x) if hasattr(
                x, 'item') else x for x in value]
        else:
            sanitized_cache[key] = value

    with open(cache_path, "w") as f:
        json.dump(sanitized_cache, f, indent=2)
