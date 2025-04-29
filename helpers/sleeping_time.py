import time
import random


def random_sleep(min_sleep: float, max_sleep: float, multiplier: float = 1.0) -> None:
    """
    Sleep for a random duration between min_sleep and max_sleep, scaled by multiplier.
    Example:
        random_sleep(0.5, 2.0, multiplier=0.8)
    """
    duration = random.uniform(min_sleep, max_sleep) * multiplier
    time.sleep(duration)
