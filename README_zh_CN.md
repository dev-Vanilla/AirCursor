# AirCursor

### 项目简介
AirCursor 是一个基于手势控制的鼠标应用程序，使用 PySide6 和 MediaPipe 实现。通过摄像头实时捕捉手势，你可以用手指控制鼠标的移动、点击、拖动和滚动操作。

### 功能特性
- **实时手势识别**：支持手部关键点检测。
- **鼠标操作**：
  - 食指指向目标位置。
  - 捏合手指触发点击。
  - 手势滑动实现滚动。
- **托盘图标支持**：最小化到系统托盘。
- **自定义灵敏度**：调整点击、移动和滚动的灵敏度。
- **跨平台支持**：适用于 Windows、macOS 和 Linux。

### 安装指南

#### 依赖项
请确保已安装以下依赖项：
- Python 3.10+
- OpenCV (`pip install opencv-python`)
- MediaPipe (`pip install mediapipe`)
- PySide6 (`pip install PySide6`)

#### 快速开始
克隆项目并运行：
```bash
git clone https://github.com/yourusername/AirCursor.git
cd AirCursor
pip install -r requirements.txt
python main.py
```

### 使用说明
1. 启动应用程序后，摄像头将自动开启。
2. 使用手势控制鼠标：
   - **移动**：食指指向目标位置。
   - **点击**：捏合食指和拇指。
   - **拖动**：保持捏合状态并移动手指。
   - **滚动**：上下滑动手掌。
3. 可通过托盘图标暂停或退出服务。

### 截图
<!-- ![主界面](resources/screenshot_main.png)
![设置界面](resources/screenshot_settings.png) -->

### 贡献指南
如果你发现了 Bug 或有改进建议，请提交 Issue。如果你想贡献代码，请 Fork 项目并提交 Pull Request。

### 许可证
本项目采用 [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.txt) 许可证。详情请参阅 [LICENSE](LICENSE) 文件。