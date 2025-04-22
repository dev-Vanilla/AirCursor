# AirCursor

### Project Overview
AirCursor is a gesture-controlled mouse application built with PySide6 and MediaPipe. By capturing hand gestures in real-time via the camera, you can control the mouse's movement, clicks, drag-and-drop, and scrolling using your fingers.

### Key Features
- **Real-time Gesture Recognition**: Supports hand landmark detection.
- **Mouse Operations**:
  - Point with your index finger to move the cursor.
  - Pinch your thumb and index finger to trigger a click.
  - Swipe gestures for scrolling.
- **System Tray Support**: Minimize to the system tray.
- **Customizable Sensitivity**: Adjust sensitivity for clicking, moving, and scrolling.
- **Cross-platform Support**: Works on Windows, macOS, and Linux.

### Installation Guide

#### Dependencies
Make sure you have installed the following dependencies:
- Python 3.10+
- OpenCV (`pip install opencv-python`)
- MediaPipe (`pip install mediapipe`)
- PySide6 (`pip install PySide6`)

#### Quick Start
Clone the project and run:
```bash
git clone https://github.com/yourusername/AirCursor.git
cd AirCursor
pip install -r requirements.txt
python main.py
```

### Usage Instructions
1. After launching the application, the camera will automatically start.
2. Use gestures to control the mouse:
   - **Move**: Point with your index finger.
   - **Click**: Pinch your thumb and index finger.
   - **Drag**: Keep pinching and move your hand.
   - **Scroll**: Swipe your palm up or down.
3. You can pause or exit the service via the system tray icon.

### Screenshots
<!-- ![Main Interface](resources/screenshot_main.png)
![Settings Interface](resources/screenshot_settings.png) -->

### Contribution Guidelines
If you find any bugs or have improvement suggestions, please submit an Issue. If you'd like to contribute code, fork the project and submit a Pull Request.

### License
This project is licensed under the [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.txt). For more details, see the [LICENSE](LICENSE) file.