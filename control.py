# import pyautogui
from pynput.mouse import Controller as MouseController, Button

class Controller:
    def __init__(self, settings):
        self.mouse = MouseController()
        self.settings = settings  # 保存 QSettings 实例
        self.current_mouse_x, self.current_mouse_y = self.mouse.position
        self.is_pressing = False

        # 初始化参数
        self.update_parameters()

    def update_parameters(self):
        """从 QSettings 更新参数"""
        self.scroll_step = int(int(self.settings.value("screen_height", 1080)) / 120)
        self.scroll_speed = int(self.settings.value("scroll_speed", 1))
        self.tolerance = 102 - int(self.settings.value("move_sensitivity", 90))


    def update_mouse_position(self, target_x, target_y):
        # 计算当前手指位置与上一次有效位置的距离
        # distance = ((target_x - self.current_mouse_x) ** 2 + (target_y - self.current_mouse_y) ** 2) ** 0.5
        dx = target_x - self.current_mouse_x
        dy = target_y - self.current_mouse_y

        # 如果距离小于容差阈值，则忽略抖动
        if abs(dx) > self.tolerance:
            stride_x = int((dx - (dx)/(abs(dx)) * self.tolerance))
            self.current_mouse_x += stride_x

        if abs(dy) > self.tolerance:
            stride_y = int((dy - (dy)/(abs(dy)) * self.tolerance))
            self.current_mouse_y += stride_y

        # self.mouse.move(stride_x, stride_y)

        # pyautogui.moveTo(self.current_mouse_x, self.current_mouse_y)
        self.mouse.position = (self.current_mouse_x, self.current_mouse_y)


    def handle_click(self, click_flag):
        # if self.is_pressing:
        #     self.mouse.release(Button.left)
        #     self.is_pressing = False

        if click_flag and not self.is_pressing:
            # current_time = time.time()  # 获取当前时间

            # # 检查冷却时间
            # if current_time - self.last_click_time < CLICK_COOLDOWN:
            #     return  # 如果未达到冷却时间，则忽略本次点击
            self.mouse.click(Button.left)  # 按下鼠标左键
            self.is_pressing = True
        elif not click_flag:
            self.mouse.release(Button.left)  # 松开鼠标左键
            self.is_pressing = False

    def handle_scroll(self, scroll_step):
        # if self.is_pressing:
        #     self.mouse.release(Button.left)
        #     self.is_pressing = False

        self.mouse.scroll(0, int(self.scroll_step * self.scroll_speed))
        # pyautogui.scroll(int(self.scroll_step * self.scroll_speed))

    def handle_drag(self):
        if not self.is_pressing:
            self.mouse.press(Button.left)
            self.is_pressing = True

    # def handle_maximize(self):
    #     window = gw.getActiveWindow()[0]
    #     # window = gw.getWindowsAt(10, 10)
    #     if not window.isMaximized:
    #         window.maximize()
