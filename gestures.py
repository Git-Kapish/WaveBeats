"""
Gesture detection logic based on MediaPipe hand landmarks.

Functions:
- detect_gesture(hand_landmarks, hand_history, frame_shape, config)
    Returns: one of ("play_pause","next","previous","volume_up","volume_down","none")
"""

from typing import Optional
import math

# Landmark indices for finger tips and pip joints
TIPS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
PIPS = [3, 6, 10, 14, 18]   # prox. interphalangeal / lower joint

def _finger_is_up(landmarks, tip_idx, pip_idx, frame_shape):
    """
    Determine if finger is up: compare y of tip and pip for fingers (not thumb).
    For the thumb we compare x due to orientation in mirrored frame.
    """
    h, w = frame_shape[0], frame_shape[1]
    tip = landmarks.landmark[tip_idx]
    pip = landmarks.landmark[pip_idx]

    # For index..pinky higher (smaller y) -> finger up
    if tip_idx != 4:  # not thumb
        return tip.y < pip.y
    else:
        # For thumb use x comparison (thumb is sideways). Consider handedness is mirrored.
        return tip.x < pip.x  # in mirrored frame this works when thumb is open to left

def _calc_distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def _palm_center_x(landmarks):
    # approximate palm center using landmark 9
    return landmarks.landmark[9].x

def detect_gesture(hand_landmarks, hand_history, frame_shape, config) -> str:
    """
    Detects a limited set of gestures:
    - Fist (all fingers down) -> play_pause
    - Open palm (all fingers up) -> play_pause (or none)
    - Swipe right (fast increase in palm x) -> next
    - Swipe left (fast decrease) -> previous
    - Volume control: index + thumb distance (if both extended) -> volume_up/volume_down (thresholded)
    """

    # 1) Finger up/down
    fingers_up = []
    for tip, pip in zip(TIPS, PIPS):
        fingers_up.append(_finger_is_up(hand_landmarks, tip, pip, frame_shape))

    # Interpret basic gestures
    all_down = not any(fingers_up)
    all_up = all(fingers_up)

    # Calculate swipe from hand_history (list of recent cx values possibly with None)
    # Compute delta between newest valid and oldest valid snapshot
    xs = [x for x in hand_history.history if x is not None]
    swipe = None
    if len(xs) >= 3:
        dx = xs[-1] - xs[0]
        # Normalize by frame width
        frame_w = frame_shape[1]
        norm_dx = dx / frame_w
        swipe_threshold = config.get("swipe_norm_threshold", 0.12)
        if norm_dx > swipe_threshold:
            swipe = "right"
        elif norm_dx < -swipe_threshold:
            swipe = "left"

    # Volume control: if thumb and index both up, use their distance to interpret volume gestures
    thumb = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    thumb_index_dist = _calc_distance(thumb, index_tip)

    # heuristic thresholds
    vol_close_thresh = config.get("volume_close_thresh", 0.05)
    vol_far_thresh = config.get("volume_far_thresh", 0.12)

    # Decide gestures with priority:
    # 1. swipe -> next/previous
    if swipe == "right":
        return "next"
    if swipe == "left":
        return "previous"

    # 2. fist -> play/pause
    if all_down:
        return "play_pause"

    # 3. volume by thumb-index distance (if both up)
    if fingers_up[0] and fingers_up[1]:  # thumb and index up
        if thumb_index_dist < vol_close_thresh:
            # finger pinched -> volume down (or mute)
            return "volume_down"
        elif thumb_index_dist > vol_far_thresh:
            return "volume_up"

    # 4. all open palm can be play/pause toggle as well (optional)
    if all_up:
        # return "play_pause"
        return "none"

    return "none"
