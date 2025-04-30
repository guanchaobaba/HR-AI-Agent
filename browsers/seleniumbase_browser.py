# browsers/seleniumbase_browser.py
from time import sleep
from seleniumbase import Driver


def create_sbase_driver(
    url: str = None,
    # e.g. r"C:\Users\You\AppData\Local\Google\Chrome\User Data"
    user_data_dir: str = None,
    profile_dir: str = None,       # e.g. "Profile 1" or "Default"
    headless: bool = False,
    use_uc: bool = False,
) -> Driver:
    """
    Spins up Chrome with your real profile.
    """
    # Build the kwargs for Driver()
    driver_kwargs = {
        "browser": "chrome",
        "headless": headless,
        "uc": use_uc,                    # only if you need undetected-cc
        "user_data_dir": user_data_dir,  # parent folder
    }
    # Pass profile selection as a separate flag
    if profile_dir:
        driver_kwargs["chromium_arg"] = f"--profile-directory={profile_dir}"

    # Remove any Nones
    driver_kwargs = {k: v for k, v in driver_kwargs.items() if v is not None}

    driver = Driver(**driver_kwargs)

    if url:
        driver.open(url)

    sleep(12)
    return driver
