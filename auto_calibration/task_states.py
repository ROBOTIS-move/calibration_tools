from enum import Enum


class ButtonState(Enum):
    DEFAULT = 0
    PUSHED = 1
    ENABLED = 2
    DISABLED = 3


class StepState(Enum):
    CAMERA_CONNECTION = 0
    INITIALIZATION = 1
    CALIBRATION = 2
    ROM_WRITING = 3


class DynamixelState(Enum):
    TASK_SUCCESS = 0
    PORT_OPEN_ERROR = -1
    PORT_CLOSE_ERROR = -2
    BAUDRATE_ERROR = -3
    COMM_ERROR = -4
    DXL_ERROR = -5
    UNKNOWN_ERROR = -99


class CameraState(Enum):
    TASK_SUCCESS = 0
    PORT_OPEN_ERROR = -1
    PORT_CLOSE_ERROR = -2
    UNKNOWN_ERROR = -99
