import pyautogui
import time
import random
import math


def human_like_mouse_move(start_x, start_y, end_x, end_y, duration=1.0, curve_intensity=5):
    """
    Move the mouse in a human-like curved motion with various movement patterns.
    """
    # Get current mouse position if start not provided
    if start_x is None or start_y is None:
        start_x, start_y = pyautogui.position()

    # Calculate distance
    distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)

    # Determine number of steps based on distance and duration
    steps = max(int(distance/10), 20)
    interval = duration / steps

    # Select a random movement pattern
    pattern = random.choice(
        ['bezier', 'circle', 'zigzag', 'corner', 'overshoot'])

    if pattern == 'bezier':
        # Standard bezier curve with correction points
        control_x1 = start_x + (random.random() - 0.5) * \
            distance * 0.4 * (curve_intensity/5)
        control_y1 = start_y + (random.random() - 0.5) * \
            distance * 0.4 * (curve_intensity/5)
        control_x2 = end_x + (random.random() - 0.5) * \
            distance * 0.4 * (curve_intensity/5)
        control_y2 = end_y + (random.random() - 0.5) * \
            distance * 0.4 * (curve_intensity/5)

        # Move the mouse along the path
        last_point = (start_x, start_y)
        for i in range(steps):
            t = i / steps
            x = (1-t)**3 * start_x + 3*(1-t)**2 * t * control_x1 + \
                3*(1-t) * t**2 * control_x2 + t**3 * end_x
            y = (1-t)**3 * start_y + 3*(1-t)**2 * t * control_y1 + \
                3*(1-t) * t**2 * control_y2 + t**3 * end_y

            # Occasionally use last_point to simulate momentum and hand tremor (5% chance)
            if random.random() < 0.05:
                # Blend current target with last position (momentum effect)
                x = 0.85 * x + 0.15 * last_point[0]
                y = 0.85 * y + 0.15 * last_point[1]
                # Add stronger jitter for "tremor"
                jitter_x = x + random.uniform(-4, 4)
                jitter_y = y + random.uniform(-4, 4)
            else:
                # Normal jitter
                jitter_x = x + random.uniform(-2, 2)
                jitter_y = y + random.uniform(-2, 2)

            # Move mouse and update last_point
            pyautogui.moveTo(jitter_x, jitter_y)
            last_point = (jitter_x, jitter_y)
            time.sleep(interval * random.uniform(0.8, 1.2))

    elif pattern == 'circle':
        # Move in a partial circular arc to target
        center_x = (start_x + end_x) / 2
        center_y = (start_y + end_y) / 2
        radius = distance / 2

        # Random clockwise or counterclockwise
        clockwise = random.choice([1, -1])

        for i in range(steps):
            t = i / steps
            angle = math.pi * t * clockwise

            # Calculate position on arc
            x = center_x + math.cos(angle) * radius * \
                (1-t) + (end_x - center_x) * t
            y = center_y + math.sin(angle) * radius * \
                (1-t) + (end_y - center_y) * t

            pyautogui.moveTo(x, y)
            time.sleep(interval * random.uniform(0.8, 1.2))

    elif pattern == 'zigzag':
        # Move in a zigzag pattern to destination
        for i in range(steps):
            t = i / steps

            # Base position
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t

            # Add zigzag variation
            # Decreasing amplitude as we approach target
            amplitude = distance * 0.1 * (1-t)
            if i % 2 == 0:
                x += random.uniform(0, amplitude)
                y -= random.uniform(0, amplitude)
            else:
                x -= random.uniform(0, amplitude)
                y += random.uniform(0, amplitude)

            pyautogui.moveTo(x, y)
            time.sleep(interval * random.uniform(0.9, 1.1))

    elif pattern == 'corner':
        # Move to a corner first, then to destination
        corner_x = end_x
        corner_y = start_y

        if random.random() < 0.5:  # Randomize which corner we use
            corner_x = start_x
            corner_y = end_y

        # First half - move to corner
        half_steps = steps // 2
        for i in range(half_steps):
            t = i / half_steps
            x = start_x + (corner_x - start_x) * t
            y = start_y + (corner_y - start_y) * t

            pyautogui.moveTo(x + random.uniform(-2, 2),
                             y + random.uniform(-2, 2))
            time.sleep(interval * random.uniform(0.9, 1.1))

        # Second half - move from corner to destination
        for i in range(half_steps):
            t = i / half_steps
            x = corner_x + (end_x - corner_x) * t
            y = corner_y + (end_y - corner_y) * t

            pyautogui.moveTo(x + random.uniform(-2, 2),
                             y + random.uniform(-2, 2))
            time.sleep(interval * random.uniform(0.9, 1.1))

    elif pattern == 'overshoot':
        # Overshoot and correct - humans often do this

        # Calculate overshoot point (10-20% past target)
        overshoot_t = random.uniform(1.1, 1.2)
        overshoot_x = start_x + (end_x - start_x) * overshoot_t
        overshoot_y = start_y + (end_y - start_y) * overshoot_t

        # First move quickly toward overshoot point
        quick_steps = int(steps * 0.8)
        for i in range(quick_steps):
            t = i / quick_steps

            # Use Bezier for natural arc
            control_x = start_x + (end_x - start_x) * \
                0.5 + random.uniform(-30, 30)
            control_y = start_y + (end_y - start_y) * \
                0.5 + random.uniform(-30, 30)

            x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * overshoot_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * overshoot_y

            pyautogui.moveTo(x, y)
            time.sleep(interval * 0.9)  # Move faster during overshoot

        # Then slowly correct back to actual target
        correction_steps = steps - quick_steps
        for i in range(correction_steps):
            t = i / correction_steps

            x = overshoot_x + (end_x - overshoot_x) * t
            y = overshoot_y + (end_y - overshoot_y) * t

            # Slower correction movement with small wiggles
            pyautogui.moveTo(x + random.uniform(-3, 3),
                             y + random.uniform(-3, 3))
            time.sleep(interval * 1.5)  # Slower during correction

    # Final cleanup - make sure we end exactly at the target
    pyautogui.moveTo(end_x, end_y)


def human_click(x=None, y=None, button='left'):
    """
    Perform a very human-like click with variable pre-click behaviors.
    """
    if x is not None and y is not None:
        # Move to position with human-like curve
        human_like_mouse_move(None, None, x, y,
                              duration=random.uniform(
                                  0.4, 0.9),  # Variable speed
                              curve_intensity=random.randint(2, 7))

    # Random pre-click behavior (20% chance)
    if random.random() < 0.2:
        behavior = random.choice(['hesitate', 'circle', 'doublePosition'])

        if behavior == 'hesitate':
            # Hesitate before clicking (common when targeting small elements)
            time.sleep(random.uniform(0.1, 0.4))

        elif behavior == 'circle':
            # Small circular motion around target (very human targeting behavior)
            current_x, current_y = pyautogui.position()
            radius = random.randint(3, 8)
            steps = random.randint(5, 10)

            for i in range(steps):
                angle = (i / steps) * math.pi * 2
                circle_x = current_x + math.cos(angle) * radius
                circle_y = current_y + math.sin(angle) * radius
                pyautogui.moveTo(circle_x, circle_y)
                time.sleep(0.01)

            # Return to center
            pyautogui.moveTo(current_x, current_y)

        elif behavior == 'doublePosition':
            # Readjust position slightly (humans often reposition for precision)
            current_x, current_y = pyautogui.position()
            adjust_x = current_x + random.randint(-5, 5)
            adjust_y = current_y + random.randint(-5, 5)

            # Small movement away and back
            pyautogui.moveTo(adjust_x, adjust_y)
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.moveTo(current_x, current_y)

    # Slight pause before clicking (very natural targeting behavior)
    time.sleep(random.uniform(0.05, 0.15))

    # Click with variable duration
    pyautogui.click(button=button, duration=random.uniform(0.01, 0.1))

    # Sometimes humans keep the mouse still after clicking, sometimes they move it slightly
    if random.random() < 0.3:
        time.sleep(random.uniform(0.1, 0.3))
    else:
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(
            current_x + random.randint(-10, 10),
            current_y + random.randint(-10, 10),
            duration=0.1
        )
