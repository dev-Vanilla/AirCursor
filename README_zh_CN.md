<h4 align="right"> 
<a href="README.md">English</a> 
<span href="README_zh_CN.md" 
style="margin: 0 10px;" >中文</span> 
</h4>

<p align="center">
    <img src="./resources/imgs/icon.svg" width=169/>
</p>  

<p align="center">
    <a href="https://github.com/dev-Vanilla/AirCursor/releases"><img src="https://img.shields.io/github/v/release/dev-Vanilla/AirCursor?style=flat-square&logo=github" alt="Release"></a>
    <a href="https://github.com/dev-Vanilla/AirCursor/stargazers"><img src="https://img.shields.io/github/stars/dev-Vanilla/AirCursor?style=flat-square&logo=github" alt="Stars"></a>
    <a href="https://github.com/dev-Vanilla/AirCursor/actions/workflows/build.yaml"><img src="https://img.shields.io/github/actions/workflow/status/dev-Vanilla/AirCursor/build.yaml?style=flat-square&logo=github" alt="Build"></a>
    <a href="https://github.com/dev-Vanilla/AirCursor/blob/main/LICENSE"><img src="https://img.shields.io/github/license/dev-Vanilla/AirCursor?style=flat-square&logo=github" alt="License"></a>
   </a>
</p>


<h1 align="center">AirCursor</h1>

<p align="center"><em>"我们要用世上最好的触控设备——我们与生俱来的手指"</em></p>  
<p align="center"><strong>— 史蒂夫·乔布斯, 2007 iPhone 发布会</strong></p>


## 概览

数十年来，鼠标、键盘和屏幕一直是人机交互的主要方式。尽管这些工具十分高效，但长期使用易致疲劳。随着技术的飞速发展，这些彼时的革命性创新也稍显局限。如果可以通过简单的空中手势控制电脑，那将怎样？受此愿景和最近 AR 领域的创新启发，我开发了 **AirCursor**，一款基于手势控制的鼠标应用。

AirCursor 使用 **MediaPipe** 实现实时手部追踪，并通过 **PySide6** 提供用户界面，使我们能够通过手势直观地控制电脑。无需额外硬件，AirCursor 将简单的手部动作转化为精确的鼠标操作，例如移动光标、点击、拖拽和滚动——仅需动动手指即可完成。

该项目设计轻量、跨平台且易于使用，适合开发者和普通用户。

---

## 功能特性

- **实时手势识别**：支持高精度的手部关键点检测。
- **低硬件依赖**：只需带有摄像头的设备即可运行。
- **跨平台支持**：兼容 Windows、macOS 和 Linux，支持 ARM 和 x64 平台。
- **鼠标操作**：
  - 🖐️ **移动**：用食指指向以移动光标。
  - 🫵 **点击**：用拇指和食指捏合以执行点击。
  - 🤏 **拖拽**：保持捏合状态并移动手部以拖拽物品。
  - ✌️ **滚动**：用手掌上下滑动以滚动页面。
- **系统托盘支持**：可最小化到系统托盘并作为后台服务运行。
- **灵敏度调节**：可调整点击、移动和滚动的灵敏度。

### 计划功能（待办清单）

以下是未来计划实现的功能：

- [ ] **更多手势**: 最小化, 最大化, 关闭窗口, 切换桌面 ...
- [ ] **自定义手势**：允许用户定义自己的手势。
- [ ] **Linux Wayland 支持**：扩展对 Linux Wayland 环境的兼容性。
- [ ] **多语言界面**：增加对多种语言的支持。
- [ ] **性能优化**：优化手势识别算法以降低延迟。
- [ ] **硬件集成**：探索与 AR/VR 设备的集成，打造沉浸式体验。
- [ ] **多手势组合支持**：支持双手和多指手势。

### 兼容性

| 平台         | 环境          | 状态        |
|--------------|---------------|-------------|
| **Windows**  | 所有版本      | ✅ 已支持   |
| **macOS**    | macOS 10.15+  | ✅ 已支持   |
| **Linux**    | Wayland       | 🚧 计划中   |
|              | Xorg          | ✅ 已支持   |

---

## 快速开始

### 试用 AirCursor
1. 前往 [GitHub Releases 页面](https://github.com/dev-Vanilla/AirCursor/releases)，下载适用于你平台的可执行文件：
   - `.exe` 适用于 Windows
   - `.app` 适用于 macOS
   - `.bin` 适用于 Linux
2. 双击下载的文件运行应用程序。
3. 开始享受用手势控制电脑的乐趣吧！

### 安装
1. 前往 [GitHub Releases 页面](https://github.com/dev-Vanilla/AirCursor/releases)，下载适用于你平台的安装包：
   - `.msi` 适用于 Windows
   - `.dmg` 适用于 macOS
   - `.deb` 或 `.rpm` 适用于 Linux
2. 使用平台的标准安装流程安装软件包。
3. 启动应用程序并立即开始使用。

---

### 使用说明

1. 启动应用程序后，通过系统托盘菜单启用手势识别（右键单击托盘图标并选择“启动”）。
2. 使用以下手势控制鼠标：
   - ☝️ **移动**：用食指指向以移动光标。
   - 🫵 **点击**：用拇指和食指捏合以执行点击。
   - 🤏 **拖拽**：保持捏合状态并移动手部以拖拽物品。
   - ✌️ **滚动**：用手掌上下滑动以滚动页面。
3. 你可以通过系统托盘图标暂停或退出服务。

---

## 开发指南

### 快速开始

要设置开发环境，请按照以下步骤操作：

```bash
git clone https://github.com/dev-Vanilla/AirCursor.git
cd AirCursor
pip install -r requirements.txt
python3 main.py
```

### 依赖项

确保已安装以下依赖项：
- Python 3.12+
- OpenCV (`pip install opencv-python`)
- MediaPipe (`pip install mediapipe`)
- PySide6 (`pip install PySide6`)
- pynput (`pip install pynput`)

---

### 贡献指南

欢迎社区贡献！以下是你可以帮助的方式：

- **报告问题或建议功能**：通过 [Issues](https://github.com/dev-Vanilla/AirCursor/issues) 页面提交问题。
- **提交 Pull Request**：Fork 项目，做出更改，并提交带有详细描述的 Pull Request。
- **传播项目**：将 AirCursor 分享给可能感兴趣的人！

提交代码时，请确保：
- 你的代码符合项目的编码标准。
- 为新增功能提供清晰简洁的文档。
- 在提交前彻底测试你的更改。

---

### 许可证

本项目采用 [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.txt) 许可证。更多详情，请参阅 [LICENSE](LICENSE) 文件。

---

### 联系我们

如有任何问题或反馈，请随时通过 [vanillayhd@outlook.com](mailto:vanillayhd@outlook.com) 联系我。

让我们重新定义人机交互的未来！
