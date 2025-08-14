"""
Map gestures to system-level media controls.

Uses `keyboard` primarily (works on Windows for media keys).
Falls back to `pyautogui` where needed.
"""

import time
import logging

try:
    import keyboard
except Exception:
    keyboard = None

try:
    import pyautogui
except Exception:
    pyautogui = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("actions")

def _send_media_key(key_name: str) -> bool:
    """
    Try to send media key using `keyboard` library if available, else pyautogui fallback.
    key_name examples: "play/pause media", "next track media", "previous track media"
    """
    try:
        if keyboard:
            # keyboard supports names like "play/pause media" on Windows
            keyboard.send(key_name)
            return True
        elif pyautogui:
            # pyautogui doesn't have media keys cross-platform, try multimedia key presses:
            # As a safe fallback, press space (play/pause) or arrow keys for skip (works in browser)
            if "play" in key_name:
                pyautogui.press("space")
            elif "next" in key_name:
                pyautogui.hotkey("ctrl", "right")
            elif "previous" in key_name:
                pyautogui.hotkey("ctrl", "left")
            else:
                return False
            return True
    except Exception as e:
        logger.exception("Failed to send media key: %s", e)
    return False

def perform_action(gesture: str) -> bool:
    """
    Receives a gesture string and performs the mapped action.
    Returns True if an action was successfully triggered.
    """
    gesture = gesture.lower()
    if gesture == "play_pause":
        logger.info("Action: play/pause")
        return _send_media_key("play/pause media")
    elif gesture == "next":
        logger.info("Action: next track")
        return _send_media_key("next track media")
    elif gesture == "previous":
        logger.info("Action: previous track")
        return _send_media_key("previous track media")
    elif gesture == "volume_up":
        logger.info("Action: volume up")
        # try to press volume up key (platform dependent)
        return _send_media_key("volume up")
    elif gesture == "volume_down":
        logger.info("Action: volume down")
        return _send_media_key("volume down")
    else:
        return False
