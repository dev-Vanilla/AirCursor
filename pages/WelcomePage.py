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
from control import Controller
from recognize  import Recognizer
from resources import rc_resources
from translations import rc_translations

class WelcomePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.create_main_page()
        self.setLayout(self.main_layout)  # 把创建的布局设置到自己身上

    def create_main_page(self):
        # Configuration Section
        self.main_layout = QVBoxLayout()

        demo_layout = QGridLayout()

        move_img= QLabel("This is a demo picture.")
        move_img.setPixmap(QPixmap(":/resources/imgs/point_up.png"))
        move_text=QLabel(self.tr("<b>Move:</b> Move your index finger to control the cursor."))
        demo_layout.addWidget(move_img, 0, 0)
        demo_layout.addWidget(move_text, 1, 0)

        click_img= QLabel("This is a demo picture.")
        click_img.setPixmap(QPixmap(":/resources/imgs/index_pointing_at_the_viewer.png"))
        click_text=QLabel(self.tr("<b>Click:</b> Tap your index finger down to perform a click."))
        demo_layout.addWidget(click_img, 0, 1)
        demo_layout.addWidget(click_text, 1, 1)

        drag_img= QLabel("This is a demo picture.")
        drag_img.setPixmap(QPixmap(":/resources/imgs/pinching_hand.png"))
        drag_text=QLabel(self.tr("<b>Drag:</b> Pinch with your thumb and index finger to start dragging."))
        demo_layout.addWidget(drag_img, 2, 0)
        demo_layout.addWidget(drag_text, 3, 0)

        scroll_img= QLabel("This is a demo picture.")
        scroll_img.setPixmap(QPixmap(":/resources/imgs/v.png"))
        scroll_text=QLabel(self.tr("<b>Scroll:</b> Use your index and middle fingers to scroll."))
        demo_layout.addWidget(scroll_img, 2, 1)
        demo_layout.addWidget(scroll_text, 3, 1)

        config_img= QLabel("<font size='64'>🎛️</font>")
        config_img.setPixmap(QPixmap(":/resources/imgs/control_knobs.png"))
        config_text=QLabel(self.tr("<b>Settings:</b> Go to the Settings page to customize sensitivity and other options."))
        demo_layout.addWidget(config_img, 4, 0)
        demo_layout.addWidget(config_text, 5, 0)

        self.main_layout.addLayout(demo_layout)

