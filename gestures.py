"""
Gesture detection logic based on MediaPipe hand landmarks.

Returns one of:
  "play", "pause", "next", "previous", "volume_up", "volume_down", "none"
"""

import math

# MediaPipe landmark indices
# Thumb: 1(CMC), 2(MCP), 3(IP), 4(TIP)
# Index/Middle/Ring/Pinky: MCP -> PIP -> DIP -> TIP
TIPS = [4, 8, 12, 16, 20]          # thumb, index, middle, ring, pinky tips
PIPS = [3, 6, 10, 14, 18]          # corresponding lower joints

# Small tolerance to reduce jitter
MARGIN_Y = 0.02    # for up/down comparisons
MARGIN_X = 0.02    # not used much here but handy if needed


def _finger_is_up(landmarks, tip_idx, pip_idx) -> bool:
    #For non-thumb fingers: finger is 'up' if tip is ABOVE pip (smaller y).
    tip = landmarks.landmark[tip_idx]
    pip = landmarks.landmark[pip_idx]
    return (tip.y + MARGIN_Y) < pip.y


def _thumb_extended_up(landmarks) -> bool:
    
    # Thumb 'up' if:
    #   1) Thumb is extended (tip far enough from IP),
    #   2) Thumb tip is ABOVE thumb IP (smaller y).
    
    tip = landmarks.landmark[4]
    ip  = landmarks.landmark[3]
    # distance threshold for "extended"
    dist = math.hypot(tip.x - ip.x, tip.y - ip.y)
    extended = dist > 0.05
    oriented_up = (tip.y + MARGIN_Y) < ip.y
    return extended and oriented_up


def _thumb_extended_down(landmarks) -> bool:
    #Thumb 'down' if extended and tip is BELOW IP (larger y).
    tip = landmarks.landmark[4]
    ip  = landmarks.landmark[3]
    dist = math.hypot(tip.x - ip.x, tip.y - ip.y)
    extended = dist > 0.05
    oriented_down = (tip.y - MARGIN_Y) > ip.y
    return extended and oriented_down


def _all_non_thumb_up(landmarks) -> bool:
    # rest of the fingers are 'up' if tips are ABOVE their PIPs (smaller y).
    return all(_finger_is_up(landmarks, TIPS[i], PIPS[i]) for i in range(1, 5))


def _all_non_thumb_down(landmarks) -> bool:
    # rest of the fingers are 'down' if tips are BELOW their PIPs (larger y).
    return not any(_finger_is_up(landmarks, TIPS[i], PIPS[i]) for i in range(1, 5))


def detect_gesture(hand_landmarks, hand_history, frame_shape, config) -> str:
    # Anti-clockwise rotation detection for volume down
    def get_hand_angle(landmarks):
        wrist = landmarks.landmark[0]
        index_tip = landmarks.landmark[8]
        dx = index_tip.x - wrist.x
        dy = index_tip.y - wrist.y
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    # Use correct attribute name for maxlen (HandHistory likely uses 'max_length')
    maxlen = getattr(hand_history, 'maxlen', getattr(hand_history, 'max_length', 8))
    if hasattr(hand_history, 'angle_history'):
        hand_history.angle_history.append(get_hand_angle(hand_landmarks))
        if len(hand_history.angle_history) > maxlen:
            hand_history.angle_history.popleft()
    else:
        from collections import deque
        hand_history.angle_history = deque([get_hand_angle(hand_landmarks)], maxlen=maxlen)

    angles = list(getattr(hand_history, 'angle_history', []))
    if len(angles) >= 3:
        d_angle = angles[-1] - angles[0]
        rot_thresh = float(config.get("rotation_angle_threshold", -20))  # negative for anti-clockwise
        if d_angle < rot_thresh:
            return "volume_down"
    
    # Mapping:
    #   Thumbs up   -> volume_up
    #   Thumbs down -> volume_down
    #   Palm        -> play
    #   Fist        -> pause
    #   Swipe left  -> previous
    #   Swipe right -> next
    

    # Swipe detection (increases sensitivity)
    xs = [x for x in hand_history.history if x is not None]
    if len(xs) >= 3:
        dx = xs[-1] - xs[0]
        frame_w = frame_shape[1]
        norm_dx = dx / max(1, frame_w) # normalize
        swipe_threshold = float(config.get("swipe_norm_threshold", 0.02))
        if norm_dx > swipe_threshold:
            return "next"
        elif norm_dx < -swipe_threshold:
            return "previous"

    # Volume down: anti-clockwise hand rotation (detect by palm center y decreasing over time)
    palm_ys = [None if x is None else hand_landmarks.landmark[9].y for x in hand_history.history]
    palm_ys = [y for y in palm_ys if y is not None]
    if len(palm_ys) >= 3:
        dy = palm_ys[-1] - palm_ys[0]
        rot_thresh = float(config.get("rotation_y_threshold", 0.07))
        if dy < -rot_thresh:
            return "volume_down"

    # Static pose detection
    non_thumb_up = _all_non_thumb_up(hand_landmarks)
    non_thumb_down = _all_non_thumb_down(hand_landmarks)

    thumb_up_pose = _thumb_extended_up(hand_landmarks)
    thumb_down_pose = _thumb_extended_down(hand_landmarks)

    # Palm: all fingers up
    if thumb_up_pose and non_thumb_up:
        return "play"

    # Fist: all non-thumb fingers down, thumb folded across or resting on top
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    thumb_mcp = hand_landmarks.landmark[2]
    thumb_folded = (abs(thumb_tip.x - thumb_mcp.x) < 0.07) and (abs(thumb_tip.y - thumb_mcp.y) < 0.07)
    if non_thumb_down and thumb_folded:
        return "pause"

    # Thumbs up/down with other fingers closed
    if thumb_up_pose and non_thumb_down:
        return "volume_up"
    # More tolerant thumbs down: thumb extended down, other fingers down
    if thumb_down_pose and non_thumb_down:
        return "volume_down"

    return "none"
