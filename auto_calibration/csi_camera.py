import threading

import cv2

import task_states


class CSICamera:

    def __init__(self, device_path, img_width, img_height):
        self.by_path = device_path
        self.img_width = img_width
        self.img_height = img_height
        self.img = []
        self.cap = cv2.VideoCapture()
        self.run_thread = False
        self.capture_thread = threading.Thread(target=self.read_image)
        self.lock = threading.Lock()

    def connect_to_camera(self):
        if self.cap.isOpened():
            return task_states.CameraState.PORT_OPEN_ERROR

        self.cap.open(self.by_path, cv2.CAP_V4L2)
        if self.cap.isOpened():
            if not self.capture_thread.is_alive():
                self.capture_thread = threading.Thread(target=self.read_image)
                self.run_thread = True
                self.capture_thread.start()
            return task_states.CameraState.TASK_SUCCESS
        else:
            return task_states.CameraState.PORT_OPEN_ERROR

    def release_camera(self):
        self.cap.release()
        if self.run_thread:
            self.run_thread = False
            self.capture_thread.join()
        return task_states.CameraState.TASK_SUCCESS

    def read_image(self):
        while self.run_thread and self.cap.isOpened():
            with self.lock:
                ret, self.img = self.cap.read()

    def get_image(self):
        with self.lock:
            return self.img
