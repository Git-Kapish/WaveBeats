# WaveBeats 🎶

[![License: CC BY-ND 4.0](https://img.shields.io/badge/License-CC%20BY--ND%204.0-lightgrey.svg)](LICENSE)

Smart, webcam-driven media control using hand gestures — a small prototype that maps simple gestures to media actions for hands-free playback control.

Tagline: Control playback and volume with intuitive hand gestures (play, pause, skip, volume) using OpenCV + MediaPipe.

---

## Description

WaveBeats captures a live webcam feed, extracts hand landmarks with MediaPipe, and maps a concise set of gestures into system media actions. It is designed as a lightweight, extendable prototype to explore gesture-driven interaction for media playback.

Core behavior is implemented in `main.py` (capture & UI), `gestures.py` (gesture detection), and `actions.py` (system key mapping).

## Purpose

This project serves two goals: it's a personal, hands‑free media controller you can actually use, and a compact demo of computer vision, gesture recognition, and OS automation skills. It showcases practical engineering decisions (threshold tuning, cooldowns, fallbacks) and provides a clear, extensible codebase recruiters and technical reviewers can inspect. The implementation is intentionally small and readable so developers can adapt or extend gestures quickly.

---

## Features

- 👍 Thumbs Up → Volume Increase
- 👎 Thumbs Down → Volume Decrease
- ⇠ Swipe Left → Previous Track (increased sensitivity)
- ⇢ Swipe Right → Next Track (increased sensitivity)
- ✋ Palm → Play/Pause
- 🤏 Pinch (Thumb + Index) → Quit Program
- Real-time webcam overlay showing detected gesture
- Configurable thresholds in `config.json` for tuning sensitivity
- Lightweight CPU-only operation (no GPU required)

---

## Tech stack

- Python 3.10+
- OpenCV (`cv2`) — camera capture & display
- MediaPipe Hands — hand landmark detection
- `pyautogui` / `keyboard` — send hotkeys and media keys (platform-dependent)
- Standard Python libs: `math`, `collections`, `json`

Key files:
- `main.py` — main capture loop and overlay
- `gestures.py` — gesture detection heuristics
- `actions.py` — maps gestures to system/media actions
- `utils.py` — cooldown and history helpers
- `config.json` — runtime thresholds and options

---

## Installation (Windows — PowerShell)

1. Clone the repository and open PowerShell in the project folder.
2. Create & activate a virtual environment and install requirements:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

3. Run the app:

```powershell
python main.py
```

Notes:
- On Windows you may need to run PowerShell as Administrator for `keyboard` to send global media keys reliably.
- If you run on macOS or Linux, see the Limitations section below for platform notes.

---

## How to use

- Launch the app. The webcam preview shows the detected gesture at the top-left.
- Perform clear gestures (stand/sit at a consistent distance). The app uses a cooldown to avoid accidental repeats.
- Tune `config.json` values such as `swipe_norm_threshold`, `pinch_threshold`, and `rotation_angle_threshold` if detection is too sensitive or too strict.

---

## Limitations

- Platform differences:
	- Vision pipeline (OpenCV + MediaPipe) is cross-platform.
	- Sending media keys is platform-dependent: the current implementation targets Windows primarily. macOS often requires AppleScript or Accessibility permissions for reliable control; Linux behavior varies by desktop environment.
- Some media players ignore simulated media keys when unfocused. Web players (Chrome, Spotify Web) are usually more responsive to hotkeys like Ctrl+Right / Ctrl+Left.
- Gesture detection is heuristic-based and sensitive to lighting, camera angle, and user distance.

---

## Troubleshooting

- If the overlay always shows `none`: verify webcam feed and landmarks are visible; adjust thresholds in `config.json`.
- If gestures appear on-screen but actions don't run: try running the terminal as Administrator (Windows) or validate `pyautogui` / `keyboard` independently.
- If next/previous don't work for a specific player: try the same action in a browser tab (Spotify Web / YouTube) where hotkeys are usually handled.

---

## Contributing

Because this project is released under the Creative Commons
Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0) license,
distribution of modified or derivative versions is prohibited by the
license. If you have an improvement or feature idea, please open an
issue to discuss it first. The maintainer may accept contributions
under separate terms or incorporate suggested changes directly.

Ideas (after discussing via issues):
- Add macOS handlers in `actions.py` (AppleScript for Music/Spotify)
- Add new gestures in `gestures.py` or unit tests for `utils.py`

---

## Author

WaveBeats — by Git‑Kapish
Repository: https://github.com/Git-Kapish/WaveBeats

---

## License

This project is licensed under the Creative Commons Attribution-NoDerivatives
4.0 International (CC BY-ND 4.0). See the included `LICENSE` file for the
full legal text and permissions.

SPDX-License-Identifier: CC-BY-ND-4.0