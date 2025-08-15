"""
Main entrypoint for the Gesture Media Controller.

- Captures webcam frames with OpenCV
- Uses MediaPipe Hands to extract landmarks
- Uses gestures.detect_gesture to classify gestures
- Uses actions.perform_action to send media keys
- Uses utils.ActionCooldown to avoid repeated triggers
"""

import time
import json
from collections import deque

import cv2
import mediapipe as mp

from gestures import detect_gesture
from actions import perform_action
from utils import ActionCooldown, HandHistory

# Load config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

CAM_INDEX = CONFIG.get("camera_index", 0)
COOLDOWN_MS = CONFIG.get("cooldown_ms", 00)
MAX_HISTORY = CONFIG.get("history_length", 8)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cooldown = ActionCooldown(COOLDOWN_MS)
hand_history = HandHistory(MAX_HISTORY)

cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG.get("frame_width", 1080))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG.get("frame_height", 720))

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=CONFIG.get("min_detection_confidence", 0.6),
    min_tracking_confidence=CONFIG.get("min_tracking_confidence", 0.6),
) as hands:
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from camera.")
                break

            frame = cv2.flip(frame, 1)  # Mirror
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesture_name = "none"
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                # Add center x to history for swipe detection
                h, w, _ = frame.shape
                cx = int(hand_landmarks.landmark[9].x * w)  # use landmark 9 (palm center)
                hand_history.append(cx)

                gesture_name = detect_gesture(hand_landmarks, hand_history, frame.shape, CONFIG)
                # Quit immediately on pinch gesture
                if gesture_name == "quit":
                    print("Pinch detected — quitting")
                    break
                # Perform action if not in cooldown
                if gesture_name != "none" and cooldown.is_ready():
                    performed = perform_action(gesture_name)
                    if performed:
                        cooldown.trigger()
            else:
                hand_history.append(None)  # keep timeline

            # Draw & overlay
            if results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            cv2.putText(frame, f"Gesture: {gesture_name}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 144, 255), 2)

            cv2.imshow("Gesture Media Controller", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):  # ESC or q to quit
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
