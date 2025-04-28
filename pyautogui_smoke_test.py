import time
import threading
import pyautogui


def log_mouse_positions(interval=0.1, duration=5):
    """
    Logs the mouse position every `interval` seconds for `duration` seconds.
    """
    end = time.time() + duration
    while time.time() < end:
        x, y = pyautogui.position()
        print(f"{time.strftime('%H:%M:%S')}    Mouse at ({x:4d}, {y:4d})")
        time.sleep(interval)


if __name__ == "__main__":
    # 1) Start logging in the background for the next 10 seconds
    log_thread = threading.Thread(target=log_mouse_positions,
                                  kwargs={"interval": 0.1, "duration": 10},
                                  daemon=True)
    log_thread.start()

    # 2) Perform the test movements
    print(">>> Moving right by 200…")
    pyautogui.moveRel(200, 0, duration=1.0)
    time.sleep(0.5)
    print(">>> Moving left by 200…")
    pyautogui.moveRel(-200, 0, duration=1.0)
    time.sleep(0.5)
    print(">>> Moving to center…")
    w, h = pyautogui.size()
    pyautogui.moveTo(w//2, h//2, duration=1.0)

    # 3) Wait for logger to finish
    log_thread.join()
    print("Done.")
