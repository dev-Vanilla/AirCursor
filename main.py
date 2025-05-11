import os
import sys  # Only needed for access to command line arguments
import threading
import queue
from PySide6.QtCore import (
    Qt, QSettings, QSize, QTranslator, QLocale, QLibraryInfo,
    QUrl, QEvent, QTimer
)
from PySide6.QtGui import (
    QIcon, QImage, QPixmap, QColor, QPainter, QAction, QCloseEvent,
    QStyleHints, QGuiApplication, QPalette
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSystemTrayIcon, QMenu,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
    QLabel, QLineEdit, QComboBox, QSlider, QPushButton, QDial
)
from app import MainWindow
from control import Controller
from recognize  import Recognizer
from resources import rc_resources
from translations import rc_translations

def main():
    # You need one (and only one) QApplication instance per application.
    app = QApplication(sys.argv)  # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.

    # app.setStyle("Windows")

    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'qtbase', '_', QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'main', '_', ':/translations'):
        app.installTranslator(translator)

    # Create a Qt MainWindow, which will be our window.
    window = MainWindow()
    # window.show()  # IMPORTANT!!! Windows are hidden by default.
    # TODO:还是应该显示窗口，然后设置里加一条隐藏的选项

    # Start the event loop.
    app.exec()

    # Your application won't reach here until you exit and the event loop has stopped.

if __name__ == "__main__":
    main()


# TODO:分离各页面，捋清各部分
# TODO:最大化、最小化窗口
# TODO:眼神动态聚焦窗口（Mediapipe Eyes/Faces）
# TODO:尝试使用adwaita-qss，pyside最小应用深色模式测试
# TODO:博文撰写，杂志投稿
# TODO:SPE web demo原型设计开发
