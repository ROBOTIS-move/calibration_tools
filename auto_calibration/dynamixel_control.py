import time

from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler

import task_states


class DynamixelControl():

    def __init__(self, dev_name, dxl_id, baudrate):
        self.dev_name = dev_name  # '/dev/ttyUSB1'
        self.dxl_id = dxl_id  # 0
        self.baudrate = baudrate  # 4000000
        self.protocol_ver = 2.0
        self.addr_torque_present_position = 552
        self.dxl_moving_status_threshold = 1
        self.present_step_pulse = 0
        self.step_pulse = 52429  # 1 mm
        self.is_opened = False

        self.portHandler = PortHandler(self.dev_name)
        self.packetHandler = PacketHandler(self.protocol_ver)

    def open_dxl(self):
        if not self.portHandler.openPort():
            return task_states.DynamixelState.PORT_OPEN_ERROR

        if not self.portHandler.setBaudRate(self.baudrate):
            return task_states.DynamixelState.BAUDRATE_ERROR

        result = self.torque(1)
        if result != task_states.DynamixelState.TASK_SUCCESS:
            return result

        self.is_opened = True
        return task_states.DynamixelState.TASK_SUCCESS

    def close_dxl(self):
        if self.is_opened:
            result = self.torque(0)
            if result != task_states.DynamixelState.TASK_SUCCESS:
                return result
            self.portHandler.closePort()
            self.is_opened = False
            return task_states.DynamixelState.TASK_SUCCESS
        else:
            # already closed
            return task_states.DynamixelState.PORT_CLOSE_ERROR

    def torque(self, state):
        dxl_comm_result, dxl_error = \
            self.packetHandler.write1ByteTxRx(
                self.portHandler,
                self.dxl_id,
                512,
                state)
        if dxl_comm_result != COMM_SUCCESS:
            return task_states.DynamixelState.COMM_ERROR
        elif dxl_error != 0:
            return task_states.DynamixelState.DXL_ERROR
        else:
            time.sleep(1)
            return task_states.DynamixelState.TASK_SUCCESS

    def back_to_homing_position(self):
        self.write_dxl_goal_position_in_mm(0)

    def write_dxl_goal_position_in_mm(self, mm):
        self.present_step_pulse = int(mm * self.step_pulse)
        dxl_comm_result, dxl_error = \
            self.packetHandler.write4ByteTxRx(
                self.portHandler,
                self.dxl_id,
                532,
                self.present_step_pulse)
        if dxl_comm_result != COMM_SUCCESS:
            return task_states.DynamixelState.COMM_ERROR
        elif dxl_error != 0:
            return task_states.DynamixelState.DXL_ERROR
        else:
            return task_states.DynamixelState.TASK_SUCCESS

    def read_dxl_present_position(self):
        dxl_present_position, dxl_comm_result, dxl_error = \
            self.packetHandler.read4ByteTxRx(
                self.portHandler,
                self.dxl_id,
                552)
        if dxl_comm_result != COMM_SUCCESS:
            return task_states.DynamixelState.COMM_ERROR
        elif dxl_error != 0:
            return task_states.DynamixelState.DXL_ERROR

        return dxl_present_position
