# MotionField

This is a modernized version of the PV-MAT (Panoramic Video Measurement and Tracking) application using **CustomTkinter** instead of PySimpleGUI.

## What Changed

### GUI Framework
- **Replaced**: PySimpleGUI with CustomTkinter
- **Benefits**: 
  - Modern, beautiful UI with dark/light themes
  - Better performance and responsiveness
  - More native look and feel
  - Easier to customize and extend

### Fixed Issues
- **OpenCV Tracker**: Fixed the `TrackerCSRT_create()` error by using the correct OpenCV package
- **Dependencies**: Updated requirements.txt with proper package versions

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

## UI Layout

The new interface features:

- **Top Toolbar**: File selection and help
- **Left Sidebar**: Distance measurement tools
- **Center**: Main canvas for video/panorama display
- **Right Sidebar**: Controls and playback options
- **Bottom**: Status bar

## Benefits of CustomTkinter

1. **Modern Appearance**: Built-in dark/light themes
2. **Better Performance**: More efficient than PySimpleGUI
3. **Responsive Design**: Better handling of window resizing
4. **Native Feel**: Looks more like a native application
5. **Easy Customization**: Simple to modify colors, fonts, and layouts
6. **Active Development**: Regularly updated and maintained

## Migration Notes

The original PySimpleGUI version is still available as `PV-MAT for MacOS.py`. The CustomTkinter version is a complete rewrite that maintains the same core functionality while providing a much better user experience.

## Troubleshooting

If you encounter the OpenCV tracker error:
```bash
pip uninstall opencv-python
pip install opencv-contrib-python
```

This ensures you have the full OpenCV package with tracking capabilities.
