import pyautogui
import time
import random
import math


def human_like_mouse_move(start_x=None, start_y=None, end_x=0, end_y=0,
                          duration=0.2, speed_factor=1.0):
    """
    Move the mouse using PyAutoGUI’s duration+tween and a bit of random jitter.
    """
    # 1) Determine start position
    if start_x is None or start_y is None:
        start_x, start_y = pyautogui.position()

    # 2) Scale duration by speed_factor (higher speed_factor → shorter duration)
    total_dur = max(0.01, duration / speed_factor)

    # 3) Choose a tween for natural easing
    tween = random.choice([
        pyautogui.easeInQuad, pyautogui.easeOutQuad, pyautogui.easeInOutQuad
    ])

    # 4) Optional small pre‑move jitter
    jx, jy = (start_x + random.uniform(-3, 3),
              start_y + random.uniform(-3, 3))
    # 4.5) Optional small circular jitter around the jitter point

    cx, cy = jx, jy
    radius = random.uniform(3, 6)
    steps = max(6, int(random.uniform(8, 12)))
    for i in range(steps):
        angle = (i / steps) * math.tau  # full circle
        circle_x = cx + math.cos(angle) * radius
        circle_y = cy + math.sin(angle) * radius
        pyautogui.moveTo(circle_x, circle_y,
                         duration=total_dur * 0.05,
                         tween=tween)
        # return to the jitter point
    pyautogui.moveTo(cx, cy, duration=total_dur * 0.05, tween=tween)

    # 5) Main move with slight endpoint jitter
    ex, ey = (end_x + random.uniform(-2, 2),
              end_y + random.uniform(-2, 2))
    pyautogui.moveTo(ex, ey, duration=total_dur * 0.7, tween=tween)

    # 6) Final correction to exact target
    pyautogui.moveTo(end_x, end_y, duration=total_dur * 0.1)


def human_click(x=None, y=None, button='left', speed_factor=0.9):
    """
    Perform a very human-like click with variable pre-click behaviors.
    """
    if x is not None and y is not None:
        # Move to position with human-like curve
        human_like_mouse_move(None, None, x, y,
                              duration=random.uniform(
                                  0.1, 1.5), speed_factor=speed_factor)

    # Random pre-click behavior (20% chance)
    speed_multiplier = 1.0 / max(0.1, speed_factor)
    if random.random() < 0.2 * speed_multiplier:
        behavior = random.choice(['hesitate', 'circle', 'doublePosition'])

        if behavior == 'hesitate':
            # Hesitate before clicking (common when targeting small elements)
            time.sleep(random.uniform(0.1, 0.4) * speed_multiplier)

        elif behavior == 'circle':
            # Small circular motion around target (very human targeting behavior)
            current_x, current_y = pyautogui.position()
            radius = random.uniform(3, 8) * speed_multiplier
            steps = max(3, int(random.uniform(4, 10) * speed_multiplier))

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
            adjust_x = current_x + random.uniform(-5, 5)
            adjust_y = current_y + random.uniform(-5, 5)

            # Small movement away and back
            pyautogui.moveTo(adjust_x, adjust_y)
            time.sleep(random.uniform(0.1, 0.2) * speed_multiplier)
            pyautogui.moveTo(current_x, current_y)

    # Slight pause before clicking (very natural targeting behavior)
    time.sleep(random.uniform(0.05, 0.09) * speed_multiplier)

    # Click with variable duration
    pyautogui.click(button=button, duration=random.uniform(
        0.01, 0.09) * speed_multiplier)

    # Sometimes humans keep the mouse still after clicking, sometimes they move it slightly
    if random.random() < 0.3 * speed_multiplier:
        time.sleep(random.uniform(0.01, 0.3) * speed_multiplier)
    else:
        current_x, current_y = pyautogui.position()
        pyautogui.moveTo(
            current_x + random.uniform(-10, 10),
            current_y + random.uniform(-10, 10),
            duration=0.1 * speed_multiplier
        )
