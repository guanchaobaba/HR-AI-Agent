from seleniumbase import SB

with SB(
    browser="chrome",            # Browser choice: chrome, edge, firefox, safari
    # Enables undetected-chromedriver mode (anti-bot-detection)
    uc=True,
    uc_cdp_events=True,          # Enables CDP event capturing in undetected mode
    # Runs undetected-chromedriver as subprocess (more stable)
    uc_subprocess=True,



    # Use existing Chrome profile
    user_data_dir=r"C:\Users\rasel\AppData\Local\Google\Chrome\User Data",
    binary_location=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    xvfb=False,                  # Virtual display for Linux systems
    maximize=True,               # Maximizes browser window
    uc_cdp=True,                 # Shortcut for uc_cdp_events
) as sb:
    url = "https://www.browserscan.net/bot-detection"
    sb.activate_cdp_mode(url)    # Must activate CDP mode after initialization
    sb.sleep(1)

    # Now use CDP commands
    sb.cdp.flash("Test Results", duration=4)
    sb.cdp.assert_element('strong:contains("Normal")')
