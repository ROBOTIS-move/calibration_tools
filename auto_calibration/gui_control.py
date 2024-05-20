from datetime import datetime
import glob
import os
import struct

import auto_calib_ui
import camera_calibrator as calib
import csi_camera as csi
import dynamixel_control as dxl
import gui_worker as worker
from novitec_lib.rectrl import (
    c_char_p,
    CAM0,
    RECTRL_Close,
    RECTRL_Open,
    RECTRL_ReadCalibrationData,
    RECTRL_WriteCalibrationData)

import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
import task_states


class GuiControl(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.auto_calib_gui = auto_calib_ui.Ui_MainWindow()
        self.auto_calib_gui.setupUi(self)
        self.dxl = dxl.DynamixelControl('/dev/ttyUSB1', 1, 4000000)
        self.calib = calib.CameraCalibrator(9, 6, 40.0)
        self.cam = csi.CSICamera(
            '/dev/v4l/by-path/platform-tegra-capture-vi-video-index0', 1920, 1080)
        self.capture_thread = worker.CaptureThreadWorker(self.cam, self.calib, self.dxl)
        self.capture_thread.streaming_signal.connect(self.get_image)
        self.capture_thread.acquisition_signal.connect(self.do_calibration)
        self.capture_thread.ui_log_signal.connect(self.get_string)

        self.auto_calib_gui.connection_push_button.toggled.connect(
            self.on_connection_button_toggled)
        self.auto_calib_gui.initialization_push_button.toggled.connect(
            self.on_initialization_button_toggled)
        self.auto_calib_gui.calibration_push_button.toggled.connect(
            self.on_calibration_button_toggled)
        self.auto_calib_gui.rom_writing_push_button.toggled.connect(
            self.on_rom_writing_button_toggled)

        self.button_lists = {
            'connection': self.auto_calib_gui.connection_push_button,
            'initialization': self.auto_calib_gui.initialization_push_button,
            'calibration': self.auto_calib_gui.calibration_push_button,
            'rom': self.auto_calib_gui.rom_writing_push_button}

        self.button_states = {
            'connection': self.button_lists['connection'].isEnabled(),
            'initialization': self.button_lists['initialization'].isEnabled(),
            'calibration': self.button_lists['calibration'].isEnabled(),
            'rom': self.button_lists['rom'].isEnabled()}

        self.showFullScreen()

    def closeEvent(self, event: QtCore.QEvent):
        self.capture_thread.run_thread = False
        self.capture_thread.wait()
        self.dxl.close_dxl()
        self.cam.release_camera()
        event.accept()

    def set_button_state(self, button_name, state, update_state=True):
        button = self.button_lists[button_name]
        if state == task_states.ButtonState.DEFAULT:
            button.setChecked(False)
        elif state == task_states.ButtonState.PUSHED:
            button.setChecked(True)
        elif state == task_states.ButtonState.ENABLED:
            button.setChecked(False)
            button.setEnabled(True)
        elif state == task_states.ButtonState.DISABLED:
            button.setChecked(False)
            button.setEnabled(False)
        else:
            self.print_to_ui('Invaild state input!')
        if update_state:
            self.button_states[button_name] = button.isEnabled()

    def change_step(self, step):
        if step == task_states.StepState.CAMERA_CONNECTION:
            self.set_button_state(
                'initialization',
                task_states.ButtonState.DISABLED)
            self.set_button_state(
                'calibration',
                task_states.ButtonState.DISABLED)
            self.set_button_state(
                'rom',
                task_states.ButtonState.DISABLED)
            self.set_pass_fail_state()
        elif step == task_states.StepState.INITIALIZATION:
            self.set_button_state(
                'initialization',
                task_states.ButtonState.ENABLED)
            self.set_button_state(
                'calibration',
                task_states.ButtonState.DISABLED)
            self.set_button_state(
                'rom',
                task_states.ButtonState.DISABLED)
            self.set_pass_fail_state()
        elif step == task_states.StepState.CALIBRATION:
            self.set_button_state(
                'initialization',
                task_states.ButtonState.DEFAULT)
            self.set_button_state(
                'calibration',
                task_states.ButtonState.ENABLED)
            self.set_pass_fail_state()
        elif step == task_states.StepState.ROM_WRITING:
            self.set_button_state(
                'calibration',
                task_states.ButtonState.DISABLED)
            self.set_button_state(
                'rom',
                task_states.ButtonState.ENABLED)

    def disable_all_buttons(self):
        for button in self.button_lists.values():
            button.setEnabled(False)

    def enable_all_buttons(self):
        for key, value in self.button_lists.items():
            if self.button_states[key]:
                value.setEnabled(True)
            else:
                value.setEnabled(False)

    def set_pass_fail_state(self, state='Result'):
        self.auto_calib_gui.pass_fail_label.setText(state)
        if state == 'PASS':
            self.auto_calib_gui.pass_fail_label.setStyleSheet(
               'color: white; background-color: rgb(0, 255, 0);')
        elif state == 'FAIL':
            self.auto_calib_gui.pass_fail_label.setStyleSheet(
               'color: white; background-color: rgb(255, 0, 0);')
        else:
            self.auto_calib_gui.pass_fail_label.setStyleSheet('')

    def on_connection_button_toggled(self, is_checked):
        if is_checked:
            if self.dxl.open_dxl() == \
               task_states.DynamixelState.TASK_SUCCESS:
                self.print_to_ui('Open dxl successfully!')
            else:
                self.print_to_ui('Cannot open dxl')
            if self.cam.connect_to_camera() == \
               task_states.CameraState.TASK_SUCCESS:
                self.print_to_ui('Open CSI camera successfully!')
                self.capture_thread.run_thread = True
                self.capture_thread.start()
                self.change_step(task_states.StepState.INITIALIZATION)
            else:
                self.print_to_ui('Cannot open camera')
        else:
            self.capture_thread.run_thread = False
            self.capture_thread.wait()
            self.cam.release_camera()
            self.print_to_ui('Rlease camera')
            if self.dxl.close_dxl() == task_states.CameraState.TASK_SUCCESS:
                self.print_to_ui('Close dxl')
            self.auto_calib_gui.image_stream.clear()
            self.change_step(task_states.StepState.CAMERA_CONNECTION)

    def on_initialization_button_toggled(self, is_checked):
        if is_checked:
            self.calib.initialize_save_folder()
            self.capture_thread.img_cnt = 0
            self.dxl.back_to_homing_position()
            self.change_step(task_states.StepState.CALIBRATION)

    def on_calibration_button_toggled(self, is_checked):
        if is_checked:
            self.disable_all_buttons()
            self.capture_thread.enable_data_acquisition()

    def on_rom_writing_button_toggled(self, is_checked):
        if is_checked:
            self.print_to_ui('rom writing button clicked!')
            RECTRL_Open()
            tmp_data = bytearray()
            self.print_to_ui(self.calib.cam_params)
            for i, data in enumerate(self.calib.cam_params):
                tmp_data[i * 4:(i + 1) * 4] = struct.pack('f', data)
            cal_data = c_char_p(bytes(tmp_data))
            if RECTRL_WriteCalibrationData(CAM0, cal_data, len(tmp_data)) == 0:
                self.print_to_ui('write calibration data successfully')

            # check bytes
            empty_data = bytearray(len(tmp_data))
            r_cal_data = c_char_p(bytes(empty_data))
            if RECTRL_ReadCalibrationData(CAM0, r_cal_data, len(tmp_data)) > 0:
                _r_data = bytearray(r_cal_data.value)
                data_array = [
                    struct.unpack('f', _r_data[i * 4:(i + 1) * 4])[0]
                    for i in range(len(_r_data)//4)]
                self.print_to_ui('read calibration data successfully')
                self.print_to_ui(data_array)

            RECTRL_Close()
            self.change_step(task_states.StepState.INITIALIZATION)

    def load_data(self):
        files = glob.glob(os.path.join(self.calib.save_path, '*.jpg'))
        n_files = len(files)
        self.print_to_ui('The number of files: ' + str(n_files))
        imgs, points_2d, points_3d = self.calib.load_data(n_files, self.calib.save_path)
        self.print_to_ui('Data loading done!')
        points_3d = np.array(points_3d)
        points_2d = np.array(points_2d)
        points_2d.transpose(2, 0, 1)
        points_3d.transpose(2, 0, 1)
        points_3d = points_3d.reshape(-1, 3)
        points_2d = points_2d.reshape(-1, 2)
        return points_2d, points_3d

    def do_calibration(self):
        img_pts, world_pts = self.load_data()
        reproj_err, cam_mat, dcm, tvec = self.calib.calculate_intrinsics(img_pts, world_pts)
        cam_dcm, cam_tvec = self.calib.calculate_extrinsics(dcm, tvec)
        self.print_to_ui('Camera calibration done!')
        self.print_to_ui('[Calibration Error (pixels)]')
        self.print_to_ui(reproj_err)
        self.print_to_ui('[Camera Matrix]')
        self.print_to_ui(cam_mat)
        self.print_to_ui('[Rotation (cam to pin)]')
        self.print_to_ui(cam_dcm)
        self.print_to_ui('[Translation (cam to pin)]')
        self.print_to_ui(cam_tvec)
        self.enable_all_buttons()
        if reproj_err[0] < self.calib.calib_tol:
            self.calib.save_result(reproj_err, cam_mat, cam_dcm, cam_tvec)
            rod = self.calib.convert_to_rodrigues(cam_dcm)
            self.calib.cam_params = [
                cam_mat[0, 0],  # focal_length x
                cam_mat[1, 1],  # focal_length y
                cam_mat[0, 2],  # principal point x
                cam_mat[1, 2],  # principal point y
                rod[0],  # axis-angle x
                rod[1],  # axis-angle y
                rod[2],  # axis-angle z
                cam_tvec[0],  # translate x
                cam_tvec[1],  # translate y
                cam_tvec[2]]  # translate z
            self.print_to_ui(self.calib.cam_params)
            self.set_pass_fail_state('PASS')
            self.change_step(task_states.StepState.ROM_WRITING)
        else:
            self.set_pass_fail_state('FAIL')
            self.change_step(task_states.StepState.INITIALIZATION)

    def get_image(self, qimg):
        pixmap = QtGui.QPixmap.fromImage(qimg)
        scaled_pixmap = \
            pixmap.scaled(
                self.auto_calib_gui.image_stream.width(),
                self.auto_calib_gui.image_stream.height(),
                QtCore.Qt.KeepAspectRatio)
        self.auto_calib_gui.image_stream.setPixmap(scaled_pixmap)

    def get_string(self, message):
        self.print_to_ui(message)

    def print_to_ui(self, message):
        now = datetime.now()
        date_time = now.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(message, str):
            message = '[' + str(date_time) + '] ' + message
            self.auto_calib_gui.log_text_browser.append(message)
            return True
        elif isinstance(message, list) or isinstance(message, np.ndarray):
            if isinstance(message, np.ndarray):
                message = list(message)
            dim = np.array(message).shape
            if len(dim) > 2:
                not_supported = '[' + str(date_time) + '] Not supported dimension!'
                self.auto_calib_gui.log_text_browser.append(not_supported)
                return False
            elif len(dim) == 1:
                message = '[' + str(date_time) + '] ' + str(message)
                self.auto_calib_gui.log_text_browser.append(message)
                return True
            else:
                for row in message:
                    row = '[' + str(date_time) + '] ' + str(row)
                    self.auto_calib_gui.log_text_browser.append(row)
                return True
        else:
            not_supported = '[' + str(date_time) + '] Not supported type!'
            self.auto_calib_gui.log_text_browser.append(not_supported)
            return False
