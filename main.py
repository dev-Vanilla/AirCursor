import os
import sys  # Only needed for access to command line arguments
import threading
import queue
from PySide6.QtCore import Qt, QSettings, QSize, QTranslator, QLocale, QLibraryInfo, QUrl
from PySide6.QtGui import QIcon, QImage, QPixmap, QColor, QPainter, QAction, QCloseEvent
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget  # 正确导入 QSvgWidget
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSystemTrayIcon, QMenu,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
    QLabel, QLineEdit, QComboBox, QSlider, QPushButton, QDial
)
from control import Controller
from recognize  import Recognizer
from resources import rc_resources
from translations import rc_translations

ORGANIZATION_NAME = "aircursor"
APPLICATION_NAME = "AirCursor"

# 定义默认配置
DEFAULT_CONFIG = {
    "screen_width": 1920,  # 默认屏幕宽度
    "screen_height": 1080,  # 默认屏幕高度
    "scale": 1.0,  # 默认 HiDPI 缩放比例（浮点数）
    "camera_width": 480,  # 默认屏幕宽度
    "camera_height": 270,  # 默认屏幕高度
    "fps": 30,  # 默认 FPS
    "scroll_speed": 1,
    "click_sensitivity": 50,
    "move_sensitivity": 90
}


class EventManager:
    def __init__(self):
        self.pause_event = threading.Event()

event_manager = EventManager()  # 全局事件管理器

class MainWindow(QMainWindow):
    def __init__(self):
        # When you subclass a Qt class you must always call the super __init__ function to allow Qt to set up the object.
        super().__init__()
        self.setWindowTitle("AirCursor")
        self.setWindowIcon(QIcon(":/resources/imgs/icon.svg"))  # 设置窗口图标
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)  # 初始化 QSettings
        self.initialize_settings()  # 加载配置（如果不存在则使用默认值）

        self.isRecognizing = False  # 是否在控制鼠标
        self.isWindowVisible = False  # 决定是否更新视频帧

        self.event_manager = event_manager

        # self.pause_event = threading.Event()  # 用于暂停/恢复线程
        # self.pause_event.clear()  # 默认不使线程运行
        self.event_manager.pause_event.clear()  # 默认不使线程运行

        # 初始化 Controller
        self.controller = Controller(self.settings)
        self.recognizer = Recognizer(
            model_path = ":/resources/model/hand_landmarker.task",
            settings = self.settings,
            event_manager = self.event_manager
        )

        # self.recognizer.hand_data_signal.connect(self.mouse_control_thread)
        self.recognizer.frame_signal.connect(self.update_livestream_thread)

        # Main Layout
        main_layout = QHBoxLayout()

        # 侧边栏
        sidebar = QVBoxLayout()
        buttons = [self.tr("Welcome"), self.tr("LiveStream"), self.tr("Settings"), self.tr("About")]
        self.buttons = []
        for text in buttons:
            button = QPushButton(text)
            button.setFixedWidth(100)  # 设置按钮宽度
            button.clicked.connect(self.create_page_switcher(text))
            sidebar.addWidget(button)
            self.buttons.append(button)
        sidebar.addStretch()  # 添加弹性空间，使按钮靠上对齐

        # 内容区域
        self.stacked_widget = QStackedWidget()
        self.pages = {}

        # 创建页面
        for page_name in buttons:
            if page_name == self.tr("Welcome"):
                page = self.create_main_page()
            elif page_name == self.tr("LiveStream"):
                # Live Stream Section
                self.livestream = QLabel()
                self.livestream.setText(self.tr("Livestream view will show here."))  # Placeholder text
                self.livestream.setAlignment(Qt.AlignCenter)
                page = self.livestream
            elif page_name == self.tr("Settings"):
                # 配置页面
                page = self.create_config_page()
            else:
                # 其他页面
                page = QLabel(f"这是 {page_name} 页面的内容")
                page.setAlignment(Qt.AlignCenter)

            self.pages[page_name] = page
            self.stacked_widget.addWidget(page)


        # 将侧边栏和内容区域添加到主布局
        main_layout.addLayout(sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.initialize_tray_icon()

        # Set Central Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)  # Set the central widget of the Window.

    def initialize_tray_icon(self):
        # Create a tray icon
        self.tray_icon = QSystemTrayIcon(self)
        # self.tray_icon.setIcon(QIcon("resources/icon.png"))  # 替换为你的图标路径
        # self.tray_icon.setIcon(QIcon("resources/mouse-wireless-filled-symbolic.svg"))
        self.update_tray_icon()  # 动态更新图标以适配主题
        self.tray_icon.setToolTip("AirCursor")

        # Create a tray menu
        tray_menu = QMenu()

        # Add actions to the tray menu
        self.start_stop_action = QAction(self.tr("Start Service"), self)
        show_action = QAction(self.tr("Display Window"), self)
        quit_action = QAction(self.tr("Exit"), self)

        # Connect actions to slots
        self.start_stop_action.triggered.connect(self.start_stop_recognition)
        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.quit_application)

        # Add actions to the menu
        tray_menu.addAction(self.start_stop_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)

        # Set the menu to the tray icon
        self.tray_icon.setContextMenu(tray_menu)

        # Show the tray icon
        self.tray_icon.show()

        # Send a notification on startup
        self.tray_icon.showMessage(
            "AirCursor",
            "AirCursor has been minimized to tray.",
            QSystemTrayIcon.Information,
            3000  # 消息显示时间（毫秒）
        )

    def update_tray_icon(self):
        """根据当前主题更新托盘图标"""
        # 根据系统主题选择图标颜色
        app_palette = QApplication.palette()
        if app_palette.window().color().lightness() > 128:  # 浅色模式
            icon_color = QColor(Qt.black)  # 黑色图标
        else:  # 深色模式
            icon_color = QColor(Qt.white)  # 白色图标

        # 加载 SVG 图标并动态着色
        renderer = QSvgRenderer(":/resources/imgs/logo.svg")  # 替换为你的 SVG 文件路径
        pixmap = QPixmap(QSize(256, 256))  # 高分辨率图标
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), icon_color)
        painter.end()

        # 设置托盘图标
        self.tray_icon.setIcon(QIcon(pixmap))

    def create_main_page(self):
            main_page = QWidget()
            # Configuration Section
            main_layout = QVBoxLayout()

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


            main_layout.addLayout(demo_layout)

            main_page.setLayout(main_layout)

            return main_page

    def create_config_page(self):
        """创建配置页面布局"""
        config_page = QWidget()
        # Configuration Section
        config_layout = QVBoxLayout()

        # IMPORTANT!!!!! QSettings 返回值通常为字符串（即使保存的是数字），因此需要进行类型转换

        # Screen Resolution Input
        screen_resolution_layout = QHBoxLayout()
        self.screen_width = QLineEdit(str(self.settings.value("screen_width")))
        self.screen_width.setPlaceholderText(self.tr("Width (px)"))
        self.screen_height = QLineEdit(str(self.settings.value("screen_height")))
        self.screen_height.setPlaceholderText(self.tr("Height (px)"))
        screen_resolution_layout.addWidget(QLabel(self.tr("Screen Resolution (px):")))
        screen_resolution_layout.addWidget(self.screen_width)
        screen_resolution_layout.addWidget(QLabel("x"))
        screen_resolution_layout.addWidget(self.screen_height)
        self.screen_width.textChanged.connect(lambda: self.update_screen_width(self.screen_width.text()))
        self.screen_height.textChanged.connect(lambda: self.update_screen_height(self.screen_height.text()))

        # HiDPI Scaling Stride Slider
        scale_layout = QHBoxLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_values = [1, 1.25, 1.5, 1.75, 2]  # 定义固定的缩放值列表
        self.scale_slider.setMinimum(0)  # 最小索引
        self.scale_slider.setMaximum(len(self.scale_values) - 1)  # 最大索引
        init_scale_index = self.scale_values.index(float(self.settings.value("scale")))  # 获取初始值对应的索引
        self.scale_slider.setValue(init_scale_index)  # 默认值
        self.scale_label = QLabel(f"{float(self.settings.value("scale")) * 100:.0f}%")
        scale_layout.addWidget(QLabel(self.tr("HiDPI Scaling:")))
        scale_layout.addWidget(self.scale_slider)
        scale_layout.addWidget(self.scale_label)
        self.scale_slider.valueChanged.connect(self.update_scale)

        # Camera Resolution Input
        camera_resolution_layout = QHBoxLayout()
        self.camera_width = QLineEdit(str(self.settings.value("camera_width")))
        self.camera_width.setPlaceholderText(self.tr("Width (px)"))
        self.camera_height = QLineEdit(str(self.settings.value("camera_height")))
        self.camera_height.setPlaceholderText(self.tr("Height (px)"))
        camera_resolution_layout.addWidget(QLabel(self.tr("Camera Resolution (px):")))
        camera_resolution_layout.addWidget(self.camera_width)
        camera_resolution_layout.addWidget(QLabel("x"))
        camera_resolution_layout.addWidget(self.camera_height)
        self.screen_width.textChanged.connect(lambda: self.update_camera_width(self.camera_width.text()))
        self.screen_height.textChanged.connect(lambda: self.update_camera_height(self.camera_height.text()))

        # Camera FPS Combo帧率
        fps_layout = QHBoxLayout()
        self.fps_combo = QComboBox()
        self.fps_values = ["30", "60", "90", "120"]
        self.fps_combo.addItems(self.fps_values)  # 定义固定的缩放值列表
        init_fps_index = self.fps_values.index(str(self.settings.value("fps")))  # 获取初始值对应的索引
        self.fps_combo.setCurrentIndex(init_fps_index)  # 默认值
        self.fps_label = QLabel("FPS")
        fps_layout.addWidget(QLabel(self.tr("Camera Sampling FPS:")))
        fps_layout.addWidget(self.fps_combo)
        fps_layout.addWidget(self.fps_label)
        self.fps_combo.currentTextChanged.connect(self.update_fps)

        # Scroll Speed
        scroll_layout = QHBoxLayout()
        self.scroll_slider = QSlider(Qt.Orientation.Horizontal)
        self.scroll_values = [1, 2, 3, 4, 5, 6]  # 定义固定的缩放值列表
        self.scroll_slider.setMinimum(0)  # 最小索引
        self.scroll_slider.setMaximum(len(self.scroll_values) - 1)  # 最大索引
        init_scroll_index = self.scroll_values.index(int(self.settings.value("scroll_speed")))  # 获取初始值对应的索引
        self.scroll_slider.setValue(init_scroll_index)  # 默认值
        self.scroll_label = QLabel(f"{int(self.settings.value("scroll_speed"))}")
        scroll_layout.addWidget(QLabel(self.tr("Scroll Speed:")))
        scroll_layout.addWidget(self.scroll_slider)
        scroll_layout.addWidget(self.scroll_label)
        self.scroll_slider.valueChanged.connect(self.update_scroll)


        sensitivity_layout = QHBoxLayout()

        # 点击灵敏度
        click_thres_layout = QVBoxLayout()
        self.click_thres_dial = QDial()
        self.click_thres_dial.setRange(1, 100)
        self.click_thres_dial.setSingleStep(1)
        self.click_thres_dial.setValue(int(self.settings.value("click_sensitivity")))
        self.click_sensitivity_label = QLabel(self.tr("Current sensitivity: {}").format(self.settings.value('click_sensitivity')))
        click_thres_layout.addWidget(QLabel(self.tr("Clicking Sensitivity")))
        click_thres_layout.addWidget(self.click_thres_dial)
        click_thres_layout.addWidget(self.click_sensitivity_label)
        self.click_thres_dial.valueChanged.connect(self.update_click_sensitivity)

        # 移动灵敏度
        move_thres_layout = QVBoxLayout()
        self.move_thres_dial = QDial()
        self.move_thres_dial.setRange(0, 100)
        self.move_thres_dial.setSingleStep(1)
        self.move_thres_dial.setValue(int(self.settings.value("move_sensitivity")))
        self.move_sensitivity_label = QLabel(self.tr("Current sensitivity: {}").format(self.settings.value('move_sensitivity')))
        move_thres_layout.addWidget(QLabel(self.tr("Moving Sensitivity")))
        move_thres_layout.addWidget(self.move_thres_dial)
        move_thres_layout.addWidget(self.move_sensitivity_label)
        self.move_thres_dial.valueChanged.connect(self.update_move_sensitivity)


        sensitivity_layout.addLayout(click_thres_layout)
        sensitivity_layout.addLayout(move_thres_layout)


        config_layout.addLayout(screen_resolution_layout)
        config_layout.addLayout(scale_layout)
        config_layout.addLayout(camera_resolution_layout)
        config_layout.addLayout(fps_layout)
        config_layout.addLayout(scroll_layout)
        config_layout.addLayout(sensitivity_layout)

        config_page.setLayout(config_layout)
        return config_page

    def create_page_switcher(self, page_name):
        """创建页面切换器"""
        def switch_page():
            self.stacked_widget.setCurrentWidget(self.pages[page_name])

        return switch_page

    def show_window(self):
        """Show the main window when triggered from the tray menu."""
        self.showNormal()
        self.isWindowVisible = True
        self.recognizer.LiveStreaming = True
        self.activateWindow()

    def closeEvent(self, event):
        """Override the close event to minimize to tray instead of closing."""
        event.ignore()  # Ignore the close event
        self.hide()  # Hide the main window
        self.isWindowVisible = False
        self.recognizer.LiveStreaming = False

    def quit_application(self):
        """Quit the application when triggered from the tray menu."""
        self.isRecognizing = False
        self.recognizer.Recognizing = False
        self.isWindowVisible = False
        self.recognizer.LiveStreaming = False

        self.close()
        QApplication.quit()


    def start_stop_recognition(self):
        if self.isRecognizing:
            self.isRecognizing = False
            self.recognizer.Recognizing = False
            self.event_manager.pause_event.clear()  # 暂停线程
            self.start_stop_action.setText(self.tr("Start Service"))
        else:
            self.isRecognizing = True
            self.recognizer.Recognizing = True
            self.event_manager.pause_event.set()  # 恢复线程
            threading.Thread(target=self.recognizer.recognition_thread, daemon=True).start()
            threading.Thread(target=self.mouse_control_thread, daemon=True).start()
            self.start_stop_action.setText(self.tr("Pause Service"))


    def initialize_settings(self):
        """Initialize QSettings with default values if they don't exist."""
        for key, default_value in DEFAULT_CONFIG.items():
            if self.settings.value(key) is None:  # 如果配置项不存在
                self.settings.setValue(key, default_value)

    def update_setting(self, key, value):
        """Update a setting in QSettings and ensure correct type conversion."""
        try:
            # QSettings 返回值通常为字符串（即使保存的是数字），因此需要根据默认值的类型进行转换
            # 如果默认值是整数（int），将读取的值转换为整数。
            # 如果默认值是浮点数（float），将读取的值转换为浮点数。
            if isinstance(DEFAULT_CONFIG[key], int):
                value = int(value)
            elif isinstance(DEFAULT_CONFIG[key], float):
                value = float(value)
            self.settings.setValue(key, value)
        except ValueError:
            pass  # Ignore invalid input

    def update_screen_width(self, value):
        try:
            self.settings.setValue("screen_width", int(value))
            self.recognizer.update_parameters()
            self.controller.update_parameters()
        except ValueError:
            pass  # Ignore invalid input

    def update_screen_height(self, value):
        try:
            self.settings.setValue("screen_height", int(value))
            self.recognizer.update_parameters()
            self.controller.update_parameters()
        except ValueError:
            pass  # Ignore invalid input

    def update_camera_width(self, value):
        try:
            self.settings.setValue("camera_width", int(value))
            self.recognizer.update_parameters()
            self.controller.update_parameters()
        except ValueError:
            pass  # Ignore invalid input

    def update_camera_height(self, value):
        try:
            self.settings.setValue("camera_height", int(value))
            self.recognizer.update_parameters()
            self.controller.update_parameters()
        except ValueError:
            pass  # Ignore invalid input

    def update_scale(self, index):
        """Update the HiDPI scaling label and save the value to QSettings."""
        scale = self.scale_values[index]
        self.scale_label.setText(f"{scale * 100:.0f}%")
        self.settings.setValue("scale", scale)

    def update_fps(self, text):
        """Update the FPS label and save the value to QSettings."""
        self.settings.setValue("fps", text)
        self.recognizer.update_parameters()

    def update_scroll(self, index):
        """Update the Scroll speed label and save the value to QSettings."""
        scroll = self.scroll_values[index]
        self.scroll_label.setText(f"{scroll}")
        self.settings.setValue("scroll_speed", scroll)
        self.controller.update_parameters()  # 更新 Controller 参数

    def update_click_sensitivity(self, value):
        """Update the click sensitivity dial and save the value to QSettings."""
        self.click_sensitivity_label.setText(self.tr("Current sensitivity: {}").format(value))
        self.settings.setValue("click_sensitivity", value)
        self.recognizer.update_parameters()

    def update_move_sensitivity(self, value):
        """Update the click sensitivity dial and save the value to QSettings."""
        self.move_sensitivity_label.setText(self.tr("Current sensitivity: {}").format(value))
        self.settings.setValue("move_sensitivity", value)
        self.recognizer.update_parameters()
        self.controller.update_parameters()  # 更新 Controller 参数


    def mouse_control_thread(self):
        while self.isRecognizing:
            hand_data = self.recognizer.hand_data
            if hand_data.get("is_valid", False):  # 检查手势是否有效
                if hand_data["status"] == "drag":
                    self.controller.handle_drag()
                    self.controller.update_mouse_position(
                        hand_data["target_x"], hand_data["target_y"]
                    )
                elif hand_data["status"] == "scroll":
                    # 滚动状态
                    self.controller.handle_scroll(hand_data["scroll_step"])
                    self.controller.update_mouse_position(
                        hand_data["target_x"], hand_data["target_y"]
                    )
                elif hand_data["status"] == "pre_click":
                    self.controller.handle_click(False)
                elif hand_data["status"] == "click":
                    self.controller.handle_click(True)
                else:
                    self.controller.handle_click(False)
                    if not hand_data["clicking"]:
                        self.controller.update_mouse_position(
                            hand_data["target_x"], hand_data["target_y"]
                        )
            else:
                # 如果未检测到手势，确保鼠标左键被释放
                if self.controller.is_pressing:
                    self.controller.handle_click(False)  # 强制释放鼠标左键

    def update_livestream_thread(self, frame):
        try:
            # while not self.recognizer.frame_queue.empty():  # 处理所有积压的帧
            # frame = self.recognizer.frame_queue.get_nowait()  # TODO: 非阻塞方式获取帧
            # if frame is not None:
            # 将帧转换为 QImage
            height, width, channel = frame.shape
            bytes_per_line = channel * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            # 将 QImage 转换为 QPixmap 并显示在 QLabel 中
            self.livestream.setPixmap(QPixmap.fromImage(q_image))
        except queue.Empty:
            pass  # 如果队列为空，跳过本次更新


def main():
    # You need one (and only one) QApplication instance per application.
    app = QApplication(sys.argv)  # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.


    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'qtbase', '_', QLibraryInfo.path(QLibraryInfo.TranslationsPath)):
        app.installTranslator(translator)
    translator = QTranslator(app)
    if translator.load(QLocale.system(), 'main', '_', ':/translations'):
        app.installTranslator(translator)



    # Create a Qt MainWindow, which will be our window.
    window = MainWindow()
    # window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()

    # Your application won't reach here until you exit and the event loop has stopped.

if __name__ == "__main__":
    main()
