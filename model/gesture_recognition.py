# gesture_recognition.py

import cv2
import queue
import mediapipe as mp
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.framework.formats import landmark_pb2
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SENSITIVITY, CLICK_THRESHOLD

class GestureRecognizer:
    def __init__(self, model_path):
        self.model_path = model_path
        self.hand_data = {"target_x": SCREEN_WIDTH // 2, "target_y": SCREEN_HEIGHT // 2, "click": False}
        self.latest_detection_result = None
        self.last_valid_target = {"target_x": SCREEN_WIDTH // 2, "target_y": SCREEN_HEIGHT // 2}
        self.frame_queue = queue.Queue(maxsize=1)  # 最大队列大小为1，确保只保留最新帧

    def hand_landmark_callback(self, result: mp_vision.HandLandmarkerResult, output_image, timestamp_ms: int):
        if result.hand_landmarks:
            # 获取第一只手的关键点
            hand_landmarks = result.hand_landmarks[0]
            index_finger_tip = hand_landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            wrist = hand_landmarks[mp.solutions.hands.HandLandmark.WRIST]

            # 计算食指位置映射到屏幕坐标
            target_x = int(index_finger_tip.x * SCREEN_WIDTH * SENSITIVITY)
            target_y = int(index_finger_tip.y * SCREEN_HEIGHT * SENSITIVITY)

            # 更新上一次有效目标位置
            self.last_valid_target["target_x"] = target_x
            self.last_valid_target["target_y"] = target_y

            # 检测点击动作
            depth_difference = index_finger_tip.z - wrist.z
            is_currently_clicking = depth_difference < CLICK_THRESHOLD

            # 更新共享变量
            self.hand_data.update({
                "target_x": target_x,
                "target_y": target_y,
                "click": is_currently_clicking
            })

            # 更新最新检测结果
            self.latest_detection_result = result
        else:
            # 如果未检测到手，保持上一次的有效目标位置
            self.hand_data.update({
                "target_x": self.last_valid_target["target_x"],
                "target_y": self.last_valid_target["target_y"],
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

            # 获取食指和手腕的关键点
            index_finger_tip = hand_landmarks[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
            wrist = hand_landmarks[mp.solutions.hands.HandLandmark.WRIST]

            # 计算深度差值
            depth_difference = index_finger_tip.z - wrist.z

            # 判断是否点击
            is_clicking = depth_difference < CLICK_THRESHOLD

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
                f"Index Z: {index_finger_tip.z:.3f} | Wrist Z: {wrist.z:.3f}\n"
                f"Depth Diff: {depth_difference:.3f}\n"
                f"Click: {'Yes' if is_clicking else 'No'}"
            )
            lines = info_text.split("\n")
            for i, line in enumerate(lines):
                cv2.putText(annotated_image, line,
                            (text_x, text_y + 20 * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                            0.7, (255, 255, 255), 1, cv2.LINE_AA)

        return annotated_image

    def start(self):
        BaseOptions = mp_tasks.BaseOptions
        HandLandmarker = mp_vision.HandLandmarker
        HandLandmarkerOptions = mp_vision.HandLandmarkerOptions
        VisionRunningMode = mp_vision.RunningMode

        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.hand_landmark_callback
        )

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # 分辨率
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 320)
        cap.set(cv2.CAP_PROP_FPS, 20)

        with HandLandmarker.create_from_options(options) as landmarker:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("无法读取摄像头画面")
                    break

                # 将最新帧放入队列
                try:
                    self.frame_queue.put(frame, block=False)  # 非阻塞方式放入队列
                except queue.Full:
                    pass  # 如果队列已满，丢弃旧帧

                # 水平翻转画面（镜像效果）
                frame = cv2.flip(frame, 1)

                # 将帧转换为 RGB 格式
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 使用 mediapipe.Image 包装帧，并指定图像格式
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # 将帧提交给 HandLandmarker 进行处理
                landmarker.detect_async(mp_image, timestamp_ms=int(cap.get(cv2.CAP_PROP_POS_MSEC)))

        cap.release()
