# MotionField

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Run the new application:
```bash
python PV-MAT-CustomTkinter.py
```

## Features

### ✅ Implemented
- Modern dark/light theme UI
- File browser for video selection
- Basic video processing and panorama creation
- Drawing measurement lines on canvas
- Line selection and deletion
- Playback controls (play, pause, next, previous)
- Frame slider for navigation
- Color selection for lines
- Distance units selection
- Help system

### 🔄 Partially Implemented
- Video frame display (currently shows panorama)
- Object tracking (placeholder)
- Distance calibration (placeholder)

### 📋 To Be Implemented
- Full video frame navigation
- Object tracking with bounding boxes
- Distance calibration with real-world measurements
- Velocity calculations
- Path visualization
- Magnifier tool

## Troubleshooting

If you encounter the OpenCV tracker error:
```bash
pip uninstall opencv-python
pip install opencv-contrib-python
```

This ensures you have the full OpenCV package with tracking capabilities.
