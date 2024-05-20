import copy
import time

import cv2

from PySide6 import QtCore, QtGui


class CaptureThreadWorker(QtCore.QThread):

    streaming_signal = QtCore.Signal(QtGui.QImage)
    acquisition_signal = QtCore.Signal()
    ui_log_signal = QtCore.Signal(str)

    def __init__(self, cam, calib, dxl):
        super().__init__()
        self.cam = cam
        self.calib = calib
        self.dxl = dxl
        self.enable_detection = False
        self.get_data = False
        self.capture_cnt = 0
        self.step_size = 60
        self.max_step_cnt = 5
        self.run_thread = False

    def __del__(self):
        self.run_thread = False

    def convert_cv_to_qimg(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        qimage = QtGui.QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QtGui.QImage.Format_RGB888)
        return qimage

    def draw_corners(self, cv_img, corners):
        for corner in corners:
            x, y = corner.ravel()
            cv2.circle(cv_img, (int(x), int(y)), 10, (0, 0, 255), 5)

    def enable_data_acquisition(self):
        self.enable_detection = True

    def disable_data_acquisition(self):
        self.enable_detection = False

    def run(self):
        points_3d = []
        points_2d = []
        obj_3d = self.calib.create_checker_board()

        while self.run_thread:
            if self.enable_detection:
                if abs(self.dxl.present_step_pulse -
                       self.dxl.read_dxl_present_position()) < \
                       self.dxl.dxl_moving_status_threshold:
                    time.sleep(0.5)
                    img = self.cam.get_image()
                    if img is not None:
                        is_detected, gray, corners = self.calib.find_corners(img)
                        if is_detected:
                            opt_corners = self.calib.optimize_corners(gray, corners)
                            img_backup = img.copy()
                            self.draw_corners(img, opt_corners)
                            cv2.putText(
                                img,
                                str(self.capture_cnt),
                                (50, 75),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                3,
                                (0, 255, 0),
                                3,
                                cv2.LINE_AA)
                            qimg = self.convert_cv_to_qimg(img)
                            self.streaming_signal.emit(qimg)

                            copied_obj_3d = copy.deepcopy(obj_3d)
                            copied_obj_3d[:, -1] = self.capture_cnt * self.step_size
                            points_3d.append(copied_obj_3d)
                            points_2d.append(opt_corners)
                            self.calib.save_data(
                                self.capture_cnt,
                                img_backup,
                                opt_corners,
                                copied_obj_3d)
                            self.ui_log_signal.emit(
                                'data (' +
                                str(self.capture_cnt) +
                                ') saved at ' +
                                self.calib.save_path)
                            self.capture_cnt = self.capture_cnt + 1

                            if self.capture_cnt < self.max_step_cnt:
                                time.sleep(1)
                                self.dxl.write_dxl_goal_position_in_mm(
                                    self.capture_cnt * self.step_size)
                            else:
                                self.capture_cnt = 0
                                self.enable_detection = False
                                self.acquisition_signal.emit()

                    else:
                        self.ui_log_signal.emit('img none!')
            else:
                img = self.cam.get_image()
                qimg = self.convert_cv_to_qimg(img)
                self.streaming_signal.emit(qimg)
