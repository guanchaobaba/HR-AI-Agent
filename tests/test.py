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

    # ─── 3) Run JS to fetch all metrics in *physical* pixels ──────────────
    # debug_script = """
    # (function() {
    #     // Get the first contact element directly in JavaScript
    #     const el = document.querySelector(".im-ui-contact-info");
    #     if (!el) return null;

    #     // Get metrics
    #     const r = el.getBoundingClientRect();
    #     const win = window;
    #     const dpr = win.devicePixelRatio || 1;

    #     return {
    #         clientX: r.left,
    #         clientY: r.top,
    #         width: r.width,
    #         height: r.height,
    #         screenX: win.screenX || win.screenLeft,
    #         screenY: win.screenY || win.screenTop,
    #         innerW: win.innerWidth,
    #         innerH: win.innerHeight,
    #         outerW: win.outerWidth,
    #         outerH: win.outerHeight,
    #         dpr: dpr
    #     };
    # })();
    # """
    # m = sb.cdp.evaluate(debug_script)
    # if not isinstance(m, dict):
    #     raise RuntimeError(f"JS did not return a dict; got: {m!r}")

    # # ─── 4) Log raw JS values (for debugging) ─────────────────────────────
    # screen_w, screen_h = pyautogui.size()
    # logger.info(f"JS metrics: {m}")
    # logger.info(f"Screen size (px): {screen_w}×{screen_h}")

    # # 5) Compute the *physical* center of the element,
    # #    accounting for the browser chrome = outerH - innerH (in CSS px)
    # chrome_ui_css = m['outerH'] - m['innerH']
    # chrome_ui_phys = chrome_ui_css * m['dpr']

    # tx = m['screenX'] + (m['clientX'] * m['dpr']) + \
    #     (m['width'] * m['dpr'] / 2)

    # ty = m['screenY'] + chrome_ui_phys + \
    #     (m['clientY'] * m['dpr']) + (m['height'] * m['dpr'] / 2)

    # # ─── 6) Clamp to your monitor if you like ────────────────────────────
    # tx = max(0, min(screen_w - 1, tx))
    # ty = max(0, min(screen_h - 1, ty))

    # logger.info(f"Computed click target: ({tx:.0f}, {ty:.0f})")

    # # ─── 7) Move & click ─────────────────────────────────────────────────
    # pyautogui.moveTo(tx, ty, duration=1.0, tween=easeInOutCubic)
    # pyautogui.click()
    # logger.info("Clicked on the contact item via PyAutoGUI")
