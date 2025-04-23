from cx_Freeze import setup, Executable
import sys

# 设置基础参数
base = None
icon_path = resources/imgs/icon.svg  # 图标路径初始化

if sys.platform == "win32":
    base = "Win32GUI"  # 隐藏控制台窗口（仅适用于 Windows）
    icon_path = "resources/imgs/icon.ico"  # Windows 图标
elif sys.platform == "darwin":
    icon_path = "resources/imgs/icon.svg"  # TODO: macOS 图标
elif sys.platform.startswith("linux"):
    icon_path = "resources/imgs/1024.png"  # Linux 图标

# 包含资源文件
include_files = [
    ("resources", "resources"),  # 将 resources 文件夹包含到打包结果中
    ("model", "model"),          # 将 model 文件夹包含到打包结果中
]

# 构建配置
build_exe_options = {
    "packages": ["PySide6"],  # 包含 PySide6
    "include_files": include_files,
    "optimize": 2,  # 优化级别
}

# 可执行文件配置
executables = [
    Executable(
        "main.py",  # 主入口文件
        base=base,
        target_name="AirCursor",  # 输出可执行文件名
        icon=icon_path,  # 根据平台选择图标
    )
]

# 打包设置
setup(
    name="AirCursor",
    version="0.0.1",
    description="AirCursor - Novel Human-Computer Interaction",
    options={"build_exe": build_exe_options},
    executables=executables,
)