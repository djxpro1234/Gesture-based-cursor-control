# Gesture Control

Control your mouse cursor using hand gestures via webcam.

## Gestures

| Gesture | Action |
|---------|--------|
| Index finger point | Move cursor |
| Pinch index + thumb | Left click |
| Pinch middle + thumb | Right click |
| Pinch ring + thumb | Double click |
| Index + middle up | Scroll up |
| Only pinky up | Scroll down |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Download the [hand_landmarker.task](https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task) model and place it in the project root.

## Run

```bash
python main.py
```

Press `q` to quit.

## Requirements

- Python 3.10+
- Webcam
- macOS (uses PyAutoGUI for cursor control)
