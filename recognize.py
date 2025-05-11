import cv2
import queue
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.framework.formats import landmark_pb2
from PySide6.QtCore import QObject, Signal, QFile, QIODevice
from resources import rc_resources

# CAMERA_WIDTH = 480
# CAMERA_HEIGHT = 320
# CAMERA_FPS = 30
# CLICK_THRESHOLD = 0.08
DELTA_Z_THRESHOLD = 1
SCROLL_UNIT = int(1440 / 120)
EXTENDED_DISTANCE_THRESHOLD = 0.034
CLOSE_DISTANCE_THRESHOLD = 0.008
COOLDOWN_FRAME = 5
SCALE = 1.75

class Recognizer(QObject):
    frame_signal = Signal(object)   # 用于传递视频帧

    def __init__(self, model_path, settings, event_manager):
        super().__init__()
        model_file = QFile(model_path)
        if not model_file.open(QIODevice.ReadOnly):  # 必须先 open!
            raise IOError(f"无法打开 Qt 资源: {model_path}")
        self.model_data = bytes(model_file.readAll().data())
        self.settings = settings  # 保存 QSettings 实例
        self.event_manager = event_manager

        self.hand_data = {
            # "is_valid": False,
            "status": "idle",
            "target_x": 0,
            "target_y": 0,
            "is_pressing": False,
            "clicking": False
        }

        """
        hand_data = {
            "status": "idle", "click", "drag", scroll", "maximize", "minimize", "close"
            "target_x": 0,
            "target_y": 0,
            # "is_pressing": False,
            "pressing": False,
            "clicking": False (click & cooldown_time & pressing)
            "dragging": False
            "scroll": 0 (Floating Point, accumulate and int elsewhere)
            "maximize": False (status = "maximize")
            "minimize": False (status = "minimize")
            "close": False (status = "close")
        }

        # 放入一个queue，形成上下文，让机器学习判断。
        """

        self.latest_detection_result = None
        self.last_valid_target = {
            "target_x": 0,
            "target_y": 0
        }
        self.previous_depth_difference = 0  # 上一帧的 depth_difference
        self.click_cooldown_frames = 0  # 冷却时间计数器
        self.scroll_smoother = 0  # 滚动像素平滑器

        self.frame_queue = queue.Queue(maxsize=5)
        self.Recognizing = False
        self.LiveStreaming = False

        # 初始化参数
        self.update_parameters()

    def update_parameters(self):
        """从 QSettings 更新参数"""
        self.screen_width = int(self.settings.value("screen_width", 1920))
        self.screen_height = int(self.settings.value("screen_height", 1080))
        self.camera_width = int(self.settings.value("camera_width", 480))
        self.camera_height = int(self.settings.value("camera_height", 270))
        self.camera_fps = int(self.settings.value("fps", 30))
        self.click_threshold = 0.16 * int(self.settings.value("click_sensitivity", 50)) / 100
        self.tolerance = 102 - int(self.settings.value("move_sensitivity", 90))


    def hand_recognition_callback(self, result: mp_vision.HandLandmarkerResult, output_image, timestamp_ms: int):
        if result.hand_landmarks:
            # 获取第一只手的关键点
            hand_landmarks = result.hand_landmarks[0]
            self.norm_index_finger_tip = hand_landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]  # 正则化坐标

            world_landmarks = result.hand_world_landmarks[0]
            self.thumb_tip = world_landmarks[mp.solutions.hands.HandLandmark.THUMB_TIP]
            self.index_finger_tip = world_landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            self.middle_finger_tip = world_landmarks[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
            self.wrist = world_landmarks[mp.solutions.hands.HandLandmark.WRIST]

            norm_x = min(2*(self.norm_index_finger_tip.x - 0.25), 1) if self.norm_index_finger_tip.x > 0.25 else 0
            norm_y = min(2*(self.norm_index_finger_tip.y - 0.2), 1) if self.norm_index_finger_tip.y > 0.2 else 0


            # 计算食指位置映射到屏幕坐标
            target_x = int(norm_x * (self.screen_width * SCALE + self.tolerance)) - self.tolerance  # TODO: sensitivity? 乘他干嘛？是分数缩放
            target_y = int(norm_y * (self.screen_height * SCALE - self.tolerance)) - self.tolerance

            # 检测点击动作：计算 z 坐标变化量
            depth_difference = self.index_finger_tip.z - self.wrist.z
            if self.previous_depth_difference is None:
                self.previous_depth_difference = depth_difference
                return
            delta_z = 100*(self.previous_depth_difference - depth_difference)  # 计算帧与帧之间的 z 变化
            self.previous_depth_difference = depth_difference  # 更新上一帧的 depth_difference

            # 指与手腕的空间距离（的平方）
            self.index_distance = (self.index_finger_tip.x-self.wrist.x)**2 + (self.index_finger_tip.y-self.wrist.y)**2 + (self.index_finger_tip.z-self.wrist.z)**2

            # 食指是否伸出
            index_extended = self.index_distance > EXTENDED_DISTANCE_THRESHOLD and (self.wrist.z -self.index_finger_tip.z) > self.click_threshold

            # 两指是否接近
            thumb_index_close = abs(self.index_finger_tip.x - self.thumb_tip.x) < CLOSE_DISTANCE_THRESHOLD and abs(self.index_finger_tip.y - self.thumb_tip.y) < CLOSE_DISTANCE_THRESHOLD
            index_middle_close = abs(self.index_finger_tip.x - self.middle_finger_tip.x) < 4*CLOSE_DISTANCE_THRESHOLD and abs(self.index_finger_tip.y - self.middle_finger_tip.y) < 6*CLOSE_DISTANCE_THRESHOLD  # TODO

            # 有限状态机，并更新共享变量
            if self.click_cooldown_frames:  # 冷却
                self.click_cooldown_frames -= 1
                # 否则正常更新 xy、z 和点击状态
                self.last_valid_target["target_x"] = target_x
                self.last_valid_target["target_y"] = target_y
                self.hand_data.update({
                    "is_valid": True,  # 标记手势有效
                    "status": "idle",
                    "target_x": target_x,
                    "target_y": target_y,
                    "is_pressing": False,
                    "clicking": False
                })
            elif thumb_index_close and self.index_distance > 0.2 * EXTENDED_DISTANCE_THRESHOLD:  # 捏合（选中拖动）状态
                # 更新共享变量
                self.last_valid_target["target_x"] = target_x
                self.last_valid_target["target_y"] = target_y
                self.hand_data.update({
                    "is_valid": True,
                    "status": "drag",
                    "target_x": target_x,
                    "target_y": target_y,
                    "is_pressing": True,
                    "clicking": False
                })
            elif index_extended and index_middle_close:  # 滚动状态
                scroll_delta = target_y - self.last_valid_target["target_y"]
                scroll_step = int(scroll_delta/SCROLL_UNIT)

                if self.scroll_smoother * scroll_delta <= 0:
                    self.scroll_smoother = 0
                else:
                    self.scroll_smoother = scroll_delta

                self.last_valid_target["target_x"] = target_x
                self.last_valid_target["target_y"] = target_y
                self.hand_data.update({
                    "is_valid": True,
                    "status": "scroll",
                    "target_x": target_x,
                    "target_y": target_y,
                    "scroll_step": scroll_step,
                    "is_pressing": False,
                    "clicking": False  # 滚动状态下点击为 False
                })
            elif self.hand_data["status"] == "scroll":  # 滚动状态
                self.scroll_smoother = int(self.scroll_smoother*0.98)
                scroll_step = int(self.scroll_smoother/SCROLL_UNIT)

                if scroll_step:
                    self.last_valid_target["target_x"] = target_x
                    self.last_valid_target["target_y"] = target_y
                    self.hand_data.update({
                        "is_valid": True,
                        "status": "scroll",
                        "target_x": target_x,
                        "target_y": target_y,
                        "scroll_step": scroll_step,
                        "is_pressing": False,
                        "clicking": False  # 滚动状态下点击为 False
                    })
                else:
                    self.last_valid_target["target_x"] = target_x
                    self.last_valid_target["target_y"] = target_y
                    self.hand_data.update({
                        "is_valid": True,
                        "status": "idle",
                        "target_x": target_x,
                        "target_y": target_y,
                        "scroll_step": 0,
                        "is_pressing": False,
                        "clicking": False  # 滚动状态下点击为 False
                    })
            elif self.hand_data["status"] == "pre_click":
                if index_extended:  # 单击状态
                    self.last_valid_target["target_x"] = target_x
                    self.last_valid_target["target_y"] = target_y
                    # 冻结 xy 更新，则保持上一次的有效目标位置
                    self.hand_data.update({
                        "is_valid": True,  # 标记手势有效
                        "status": "click",
                        "target_x": target_x,
                        "target_y": target_y,
                        "is_pressing": True,
                        "clicking": True
                    })
                    self.click_cooldown_frames = COOLDOWN_FRAME  # 设置冷却时间
                elif delta_z > DELTA_Z_THRESHOLD:
                    self.last_valid_target["target_x"] = target_x
                    self.last_valid_target["target_y"] = target_y
                    self.hand_data.update({
                        "is_valid": True,  # 标记手势有效
                        "status": "pre_click",
                        "target_x": target_x,
                        "target_y": target_y,
                        "is_pressing": False,
                        "clicking": True
                    })
                else:
                    # 否则正常更新 xy、z 和点击状态
                    self.last_valid_target["target_x"] = target_x
                    self.last_valid_target["target_y"] = target_y
                    self.hand_data.update({
                        "is_valid": True,  # 标记手势有效
                        "status": "idle",
                        "target_x": target_x,
                        "target_y": target_y,
                        "is_pressing": False,
                        "clicking": False
                    })
            elif delta_z > DELTA_Z_THRESHOLD:  # z方向移动很快，意为正在点击，但未超过阈值
                # 如果冻结 xy 更新，则保持上一次的有效目标位置
                self.last_valid_target["target_x"] = target_x
                self.last_valid_target["target_y"] = target_y
                self.hand_data.update({
                    "is_valid": True,  # 标记手势有效
                    "status": "pre_click",
                    "target_x": target_x,
                    "target_y": target_y,
                    "is_pressing": False,
                    "clicking": True
                })
            else:  # 空闲状态
                # 否则正常更新 xy、z 和点击状态
                self.last_valid_target["target_x"] = target_x
                self.last_valid_target["target_y"] = target_y
                self.hand_data.update({
                    "is_valid": True,  # 标记手势有效
                    "status": "idle",
                    "target_x": target_x,
                    "target_y": target_y,
                    "is_pressing": False,
                    "clicking": False
                })

            # 更新最新检测结果
            self.latest_detection_result = result

        else:
            # 如果未检测到手，标记手势无效
            self.hand_data.update({
                "is_valid": False,  # 标记手势无效
                "status": "idle",
                "target_x": self.last_valid_target["target_x"],
                "target_y": self.last_valid_target["target_y"],
                "is_pressing": False,
                "click": False
            })
            self.latest_detection_result = None

    def draw_landmarks_on_image(self, rgb_image, detection_result):
        hand_landmarks_list = detection_result.hand_landmarks
        handedness_list = detection_result.handedness
        annotated_image = rgb_image.copy()  # 使用副本以避免修改原始帧

        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx]

            # 将手部关键点转换为 NormalizedLandmarkList 格式
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            # 绘制手部关键点和连接线
            mp.solutions.drawing_utils.draw_landmarks(
                annotated_image,
                hand_landmarks_proto,
                mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                mp.solutions.drawing_styles.get_default_hand_connections_style())

            # 显示 Z 值和深度差值
            height, width, _ = annotated_image.shape
            x_coordinates = [landmark.x for landmark in hand_landmarks]
            y_coordinates = [landmark.y for landmark in hand_landmarks]
            text_x = int(min(x_coordinates) * width)
            text_y = int(min(y_coordinates) * height) - 10  # MARGIN

            info_text = (
                # f"Thumb: {self.thumb_x:.3f} {self.thumb_y:.3f}\n"
                # f"Index: {self.index_x:.3f} {self.index_y:.3f} {self.index_z:.3f}\n"
                # f"Wrist: {self.wrist_x:.3f} {self.wrist_y:.3f} {self.wrist_z:.3f}\n"
                # f"det_th_in: {self.thumb_x-self.index_x:.3f}  {self.thumb_y-self.index_y:.3f}\n"
                # f"det_in_wr: {self.index_x-self.wrist_x:.3f}  {self.index_y-self.wrist_y:.3f} {self.index_z-self.wrist_z:.3f}\n"
                # f"index distance: {self.index_distance:.3f}\n"
                # f"det_z: {self.delta_z>0}\n"
                f"Status: {self.hand_data['status']}\n"
                f"press: {'Yes' if self.hand_data['is_pressing'] else 'No'}"
            )
            lines = info_text.split("\n")
            for i, line in enumerate(lines):
                cv2.putText(annotated_image, line,
                            (text_x, text_y + 20 * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                            0.7, (255, 255, 255), 1, cv2.LINE_AA)

        return annotated_image

    def recognition_thread(self):
        cap = None  # 初始化 cap 为 None
        try:
            BaseOptions = mp_tasks.BaseOptions
            HandLandmarker = mp_vision.HandLandmarker
            HandLandmarkerOptions = mp_vision.HandLandmarkerOptions
            VisionRunningMode = mp_vision.RunningMode
            options = HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_buffer=self.model_data,),
                running_mode=VisionRunningMode.LIVE_STREAM,
                result_callback=self.hand_recognition_callback
            )
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)  # 分辨率
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
            cap.set(cv2.CAP_PROP_FPS, self.camera_fps)
            with HandLandmarker.create_from_options(options) as landmarker:
                # 检查是否需要暂停
                self.event_manager.pause_event.wait()
                while self.Recognizing:  # 使用 self.running 控制线程循环
                    ret, frame = cap.read()
                    if not ret:
                        print("无法读取摄像头画面")
                        break
                    #套娃。。。???
                    # 水平翻转画面（镜像效果）
                    frame = cv2.flip(frame, 1)
                    # 将帧转换为 RGB 格式
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # 使用 mediapipe.Image 包装帧，并指定图像格式
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                    # 将帧提交给 HandLandmarker 进行处理
                    landmarker.detect_async(mp_image, timestamp_ms=int(cap.get(cv2.CAP_PROP_POS_MSEC)))

                    # # 发送手势数据信号
                    # if self.latest_detection_result is not None:
                    #     self.hand_data_signal.emit(self.hand_data)

                    if self.LiveStreaming:
                        # 如果有最新检测结果，绘制关键点
                        if self.latest_detection_result is not None:
                            annotated_image = self.draw_landmarks_on_image(rgb_frame, self.latest_detection_result)
                        else:
                            annotated_image = rgb_frame
                        try:
                            self.frame_queue.put(annotated_image, block=False)  # 非阻塞方式放入队列
                            # print("?")
                        except queue.Full:
                            pass  # 如果队列已满，丢弃旧帧
                        # 发送视频帧信号
                        self.frame_signal.emit(annotated_image)
        except Exception as e:
            import traceback
            print(f"手势识别线程发生错误: {e}")
            traceback.print_exc()  # 打印完整的堆栈信息
        finally:
            if cap is not None:  # 确保 cap 已定义再调用 release()
                cap.release()
            self.Recognizing= False  # 确保线程退出时将 running 设置为 False
