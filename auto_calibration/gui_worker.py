import copy
import struct
import time

import cv2

from novitec_lib.rectrl import (
    c_char_p,
    CAM0,
    RECTRL_Close,
    RECTRL_Open,
    RECTRL_ReadCalibrationData,
    RECTRL_WriteCalibrationData)

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
        try:
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
        except cv2.error as e:
            self.ui_log_signal.emit(f'color convert exception: {e}')
        except TypeError as e:
            self.ui_log_signal.emit(f'type error: {e}')
        return None

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
                            if qimg is None:
                                continue
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
                if img is not None:
                    qimg = self.convert_cv_to_qimg(img)
                    if qimg is None:
                        continue
                    self.streaming_signal.emit(qimg)


class ROMWriteThreadWorker(QtCore.QThread):

    done_signal = QtCore.Signal()
    ui_log_signal = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.input_data_array = []
        self.data_array = []
        self.run_thread = False
        self.enable_rom_writing = False

    def enable_write_rom(self):
        self.enable_rom_writing = True

    def run(self):
        while self.run_thread:
            if self.enable_rom_writing:
                RECTRL_Open()
                self.ui_log_signal.emit('Open i2c successfully')
                tmp_data = bytearray()
                for i, data in enumerate(self.input_data_array):
                    tmp_data[i * 4:(i + 1) * 4] = struct.pack('f', data)

                cal_data = c_char_p(bytes(tmp_data))
                self.ui_log_signal.emit('Writing...')
                if RECTRL_WriteCalibrationData(CAM0, cal_data, len(tmp_data)) == 0:
                    self.ui_log_signal.emit('Write calibration data successfully')

                empty_data = bytearray(len(tmp_data))
                r_cal_data = c_char_p(bytes(empty_data))

                self.ui_log_signal.emit('Reading...')
                if RECTRL_ReadCalibrationData(CAM0, r_cal_data, len(tmp_data)) > 0:
                    self.ui_log_signal.emit('Reading calibration data done')
                    _r_data = bytearray(r_cal_data.value)
                    self.data_array = [
                        struct.unpack('f', _r_data[i * 4:(i + 1) * 4])[0]
                        for i in range(len(_r_data)//4)]
                RECTRL_Close()
                self.ui_log_signal.emit('Close i2c successfully')

                self.done_signal.emit()
                self.enable_rom_writing = False
