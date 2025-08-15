"""
Map gestures to system-level media controls.

Requested behavior:
  - Thumbs up     -> volume increase
  - Thumbs down   -> volume decrease
  - Palm          -> Play
  - Fist          -> Pause
  - Swipe right   -> Next track  (Ctrl+Right)
  - Swipe left    -> Previous    (Ctrl+Left)

Notes:
  * Many desktop players only expose a single "Play/Pause" toggle globally.
    We'll try discrete play/pause via media keys if available; otherwise we
    gracefully fall back to the common toggle behavior.
"""

import logging

try:
    import keyboard  # better global media key support on Windows
except Exception:
    keyboard = None

try:
    import pyautogui  # robust hotkeys (Ctrl+Right/Left) & volume keys
except Exception:
    pyautogui = None

logger = logging.getLogger("actions")
logging.basicConfig(level=logging.INFO)


def _safe_hotkey(*keys) -> bool:
    try:
        if pyautogui:
            pyautogui.hotkey(*keys)
            return True
    except Exception as e:
        logger.exception("hotkey(%s) failed: %s", keys, e)
    return False


def _safe_press(key: str) -> bool:
    try:
        if pyautogui:
            pyautogui.press(key)
            return True
    except Exception as e:
        logger.exception("press(%s) failed: %s", key, e)
    return False


def _send_media(action: str) -> bool:
    """
    Helper for media actions:
      action in {"play","pause", "next", "previous", "volume_up", "volume_down"}
    """
    # Prefer keyboard's system media keys when present
    if keyboard:
        try:
            if action in ("play", "pause"):
                keyboard.send("play/pause media")
                return True
            elif action == "next":
                # Use only Ctrl+Right for next track
                return _safe_hotkey("ctrl", "right")
            elif action == "previous":
                # Use only Ctrl+Left for previous track
                return _safe_hotkey("ctrl", "left")
            elif action == "volume_up":
                keyboard.send("volume up")
                return True
            elif action == "volume_down":
                keyboard.send("volume down")
                return True
        except Exception as e:
            logger.exception("keyboard media send failed: %s", e)

    # Fallbacks with pyautogui
    if action == "next":
        return _safe_hotkey("ctrl", "right")
    if action == "previous":
        return _safe_hotkey("ctrl", "left")
    if action == "volume_up":
        return _safe_press("volumeup")
    if action == "volume_down":
        return _safe_press("volumedown")
    if action in ("play", "pause"):
        return _safe_press("playpause") or _safe_press("space")

    return False


def perform_action(gesture: str) -> bool:
    """
    Receives a gesture string and performs the mapped action.
    Accepts: "play", "pause", "next", "previous", "volume_up", "volume_down"
    """
    g = (gesture or "").lower()
    if g == "volume_up":
        logger.info("Action: volume up")
        return _send_media("volume_up")

    if g == "volume_down":
        logger.info("Action: volume down")
        return _send_media("volume_down")

    if g == "next":
        logger.info("Action: next track")
        return _send_media("next")

    if g == "previous":
        logger.info("Action: previous track")
        return _send_media("previous")

    if g == "play":
        logger.info("Action: play")
        return _send_media("play")

    if g == "pause":
        logger.info("Action: pause")
        return _send_media("pause")

    logger.debug("Unknown gesture: %s", gesture)
    return False
