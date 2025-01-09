from enum import IntEnum, IntFlag
from typing import Final

FILE_SIGNATURE: Final = b"LOGG"
OBJ_SIGNATURE: Final = b"LOBJ"
OBJ_SIGNATURE_SIZE: Final = len(OBJ_SIGNATURE)


class ObjType(IntEnum):
    UNKNOWN = 0
    CAN_MESSAGE = 1
    CAN_ERROR = 2
    CAN_OVERLOAD = 3
    CAN_STATISTIC = 4
    APP_TRIGGER = 5
    ENV_INTEGER = 6
    ENV_DOUBLE = 7
    ENV_STRING = 8
    ENV_DATA = 9
    LOG_CONTAINER = 10
    LIN_MESSAGE = 11
    LIN_CRC_ERROR = 12
    LIN_DLC_INFO = 13
    LIN_RCV_ERROR = 14
    LIN_SND_ERROR = 15
    LIN_SLV_TIMEOUT = 16
    LIN_SCHED_MODCH = 17
    LIN_SYN_ERROR = 18
    LIN_BAUDRATE = 19
    LIN_SLEEP = 20
    LIN_WAKEUP = 21
    MOST_SPY = 22
    MOST_CTRL = 23
    MOST_LIGHTLOCK = 24
    MOST_STATISTIC = 25
    reserved_1 = 26
    reserved_2 = 27
    reserved_3 = 28
    FLEXRAY_DATA = 29
    FLEXRAY_SYNC = 30
    CAN_DRIVER_ERROR = 31
    MOST_PKT = 32
    MOST_PKT2 = 33
    MOST_HWMODE = 34
    MOST_REG = 35
    MOST_GENREG = 36
    MOST_NETSTATE = 37
    MOST_DATALOST = 38
    MOST_TRIGGER = 39
    FLEXRAY_CYCLE = 40
    FLEXRAY_MESSAGE = 41
    LIN_CHECKSUM_INFO = 42
    LIN_SPIKE_EVENT = 43
    CAN_DRIVER_SYNC = 44
    FLEXRAY_STATUS = 45
    GPS_EVENT = 46
    FR_ERROR = 47
    FR_STATUS = 48
    FR_STARTCYCLE = 49
    FR_RCVMESSAGE = 50
    REALTIMECLOCK = 51
    AVAILABLE2 = 52
    AVAILABLE3 = 53
    LIN_STATISTIC = 54
    J1708_MESSAGE = 55
    J1708_VIRTUAL_MSG = 56
    LIN_MESSAGE2 = 57
    LIN_SND_ERROR2 = 58
    LIN_SYN_ERROR2 = 59
    LIN_CRC_ERROR2 = 60
    LIN_RCV_ERROR2 = 61
    LIN_WAKEUP2 = 62
    LIN_SPIKE_EVENT2 = 63
    LIN_LONG_DOM_SIG = 64
    APP_TEXT = 65
    FR_RCVMESSAGE_EX = 66
    MOST_STATISTICEX = 67
    MOST_TXLIGHT = 68
    MOST_ALLOCTAB = 69
    MOST_STRESS = 70
    ETHERNET_FRAME = 71
    SYS_VARIABLE = 72
    CAN_ERROR_EXT = 73
    CAN_DRIVER_ERROR_EXT = 74
    LIN_LONG_DOM_SIG2 = 75
    MOST_150_MESSAGE = 76
    MOST_150_PKT = 77
    MOST_ETHERNET_PKT = 78
    MOST_150_MESSAGE_FRAGMENT = 79
    MOST_150_PKT_FRAGMENT = 80
    MOST_ETHERNET_PKT_FRAGMENT = 81
    MOST_SYSTEM_EVENT = 82
    MOST_150_ALLOCTAB = 83
    MOST_50_MESSAGE = 84
    MOST_50_PKT = 85
    CAN_MESSAGE2 = 86
    LIN_UNEXPECTED_WAKEUP = 87
    LIN_SHORT_OR_SLOW_RESPONSE = 88
    LIN_DISTURBANCE_EVENT = 89
    SERIAL_EVENT = 90
    OVERRUN_ERROR = 91
    EVENT_COMMENT = 92
    WLAN_FRAME = 93
    WLAN_STATISTIC = 94
    MOST_ECL = 95
    GLOBAL_MARKER = 96
    AFDX_FRAME = 97
    AFDX_STATISTIC = 98
    KLINE_STATUSEVENT = 99
    CAN_FD_MESSAGE = 100
    CAN_FD_MESSAGE_64 = 101
    ETHERNET_RX_ERROR = 102
    ETHERNET_STATUS = 103
    CAN_FD_ERROR_64 = 104
    LIN_SHORT_OR_SLOW_RESPONSE2 = 105
    AFDX_STATUS = 106
    AFDX_BUS_STATISTIC = 107
    reserved_4 = 108
    AFDX_ERROR_EVENT = 109
    A429_ERROR = 110
    A429_STATUS = 111
    A429_BUS_STATISTIC = 112
    A429_MESSAGE = 113
    ETHERNET_STATISTIC = 114
    reserved_5 = 115
    reserved_6 = 116
    reserved_7 = 117
    TEST_STRUCTURE = 118
    DIAG_REQUEST_INTERPRETATION = 119
    ETHERNET_FRAME_EX = 120
    ETHERNET_FRAME_FORWARDED = 121
    ETHERNET_ERROR_EX = 122
    ETHERNET_ERROR_FORWARDED = 123
    FUNCTION_BUS = 124
    DATA_LOST_BEGIN = 125
    DATA_LOST_END = 126
    WATER_MARK_EVENT = 127
    TRIGGER_CONDITION = 128

    @staticmethod
    def from_int(object_type: int) -> "ObjType":
        try:
            return ObjType(object_type)
        except ValueError:
            return ObjType.UNKNOWN


class AppId(IntEnum):
    UNKNOWN = 0
    CANALYZER = 1
    CANOE = 2
    CANSTRESS = 3
    CANLOG = 4
    CANAPE = 5
    CANCASEXLLOG = 6
    VLCONFIG = 7
    PORSCHELOGGER = 200

    @staticmethod
    def from_int(application_id: int) -> "AppId":
        try:
            return AppId(application_id)
        except ValueError:
            return AppId.UNKNOWN


class Compression(IntEnum):
    NONE = 0
    SPEED = 1
    DEFAULT = 6
    MAX = 9

    @staticmethod
    def from_int(compression_level: int) -> "Compression | int":
        try:
            return Compression(compression_level)
        except ValueError:
            return compression_level


class ObjFlags(IntFlag):
    TIME_TEN_MICS = 0x1
    TIME_ONE_NANS = 0x2


class TriggerFlag(IntFlag):
    SINGLE_TRIGGER = 0x0
    LOGGING_START = 0x1
    LOGGING_STOP = 0x2


class CanFdFlags(IntFlag):
    NERR = 0x0004
    HIGH_VOLTAGE_WAKE_UP = 0x0008
    REMOTE_FRAME = 0x0010
    TX_ACKNOWLEDGE = 0x0040
    TX_REQUEST = 0x0080
    SRR = 0x0200
    R0 = 0x0400
    R1 = 0x0800
    FDF = 0x1000
    BRS = 0x2000
    ESI = 0x4000
    FRAME_PART_OF_BURST = 0x20000
    SINGLE_SHOT_MODE_NOT_TRANSMITTED = 0x40000
    SINGLE_SHOT_MODE_REASON = 0x80000  # 0 = arbitration lost, 1 = frame disturbed


class SysVarType(IntEnum):
    DOUBLE = 1
    LONG = 2
    STRING = 3
    DOUBLEARRAY = 4
    LONGARRAY = 5
    LONGLONG = 6
    BYTEARRAY = 7


class BusType(IntEnum):
    CAN = 1
    LIN = 5
    MOST = 6
    FLEXRAY = 7
    J1708 = 9
    ETHERNET = 10
    WLAN = 13
    AFDX = 14


class AppTextSource(IntEnum):
    MEASUREMENTCOMMENT = 0
    DBCHANNELINFO = 1
    METADATA = 2
    ATTACHMENT = 3
    TRACELINE = 4


class FunctionBusType(IntEnum):
    UNDEFINED = 0
    SIGNAL = 1
    SERVICE_FUNCTION = 2
    STATE = 3


class TriggerConditionStatus(IntEnum):
    UNKNOWN = 0
    START = 1
    STOP = 2
    STARTSTOP = 3
