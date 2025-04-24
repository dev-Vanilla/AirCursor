import os
import sys

def resource_path(relative_path):
    """
    获取资源的绝对路径。
    在开发环境中，返回相对路径；
    在打包后的环境中，从 _MEIPASS 中获取路径。
    """
    if hasattr(sys, "_MEIPASS"):
        # 如果是打包后的环境，从 _MEIPASS 中获取路径
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

icon_path = resource_path("resources/imgs/icon.svg")
logo_path = resource_path("resources/imgs/logo.svg")
model_path = resource_path("model/hand_landmarker.task")