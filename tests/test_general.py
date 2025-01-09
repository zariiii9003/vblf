from tests import DATA_DIR
from vblf.constants import (
    AppId,
    AppTextSource,
    BusType,
    Compression,
    FunctionBusType,
    ObjFlags,
    ObjType,
    SysVarType,
    TriggerConditionStatus,
    TriggerFlag,
)
from vblf.general import (
    AppText,
    AppTrigger,
    DriverOverrun,
    EnvironmentVariable,
    EventComment,
    FileStatistics,
    FunctionBus,
    GlobalMarker,
    RealTimeClock,
    SystemVariable,
    TriggerCondition,
)


def test_file_statistics():
    raw = (DATA_DIR / "FILE_STATISTICS.logg").read_bytes()
    obj = FileStatistics.unpack(raw)
    assert obj.signature == b"LOGG"
    assert obj.statistics_size == 144
    assert obj.api_number == 0x3E4630
    assert obj.application_id is AppId.CANOE
    assert obj.compression_level is Compression.SPEED
    assert obj.application_major == 12
    assert obj.application_minor == 0
    assert obj.file_size == 24763512
    assert obj.uncompressed_file_size == 89639607
    assert obj.object_count == 923421
    assert obj.application_build == 101
    assert obj.measurement_start_time.year == 2024
    assert obj.measurement_start_time.month == 11
    assert obj.measurement_start_time.day == 20
    assert obj.measurement_start_time.hour == 15
    assert obj.measurement_start_time.minute == 20
    assert obj.measurement_start_time.second == 24
    assert obj.measurement_start_time.milliseconds == 850
    assert obj.last_object_time.year == 2024
    assert obj.last_object_time.month == 11
    assert obj.last_object_time.day == 20
    assert obj.last_object_time.hour == 15
    assert obj.last_object_time.minute == 23
    assert obj.last_object_time.second == 50
    assert obj.last_object_time.milliseconds == 712
    assert obj.restore_points_offset == 24751994
    assert obj.pack() == raw


def test_app_text():
    raw = (DATA_DIR / "APP_TEXT.lobj").read_bytes()
    obj = AppText.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.APP_TEXT
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0
    assert obj.source is AppTextSource.DBCHANNELINFO
    assert obj.reserved1 == 0x01010101
    assert obj.text_length == 49
    assert obj.reserved2 == 0
    assert obj.text == "C:\\Users\\user\\Desktop\\project car\\myDatabase.dbc"
    assert obj.pack() == raw


def test_app_trigger():
    raw = (DATA_DIR / "APP_TRIGGER.lobj").read_bytes()
    obj = AppTrigger.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.APP_TRIGGER
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.pre_trigger_time == 0x1111111111111111
    assert obj.post_trigger_time == 0x2222222222222222
    assert obj.channel == 0x3333
    assert obj.flags == TriggerFlag.SINGLE_TRIGGER
    assert obj.app_specific == 0x44444444
    assert obj.pack() == raw


def test_environment_variable_integer():
    raw = (DATA_DIR / "ENV_INTEGER.lobj").read_bytes()
    obj = EnvironmentVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ENV_INTEGER
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.name_length == 3
    assert obj.data_length == 4
    assert obj.reserved == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x11\x11\x11\x11"
    assert obj.pack() == raw


def test_environment_variable_double():
    raw = (DATA_DIR / "ENV_DOUBLE.lobj").read_bytes()
    obj = EnvironmentVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ENV_DOUBLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.name_length == 3
    assert obj.data_length == 8
    assert obj.reserved == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x00\x00\x00\x00\x00\x00\x00\x40"
    assert obj.pack() == raw


def test_environment_variable_string():
    raw = (DATA_DIR / "ENV_STRING.lobj").read_bytes()
    obj = EnvironmentVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ENV_STRING
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.name_length == 3
    assert obj.data_length == 3
    assert obj.reserved == 0
    assert obj.name == "xyz"
    assert obj.data == b"xyz"
    assert obj.pack() == raw


def test_environment_variable_data():
    raw = (DATA_DIR / "ENV_DATA.lobj").read_bytes()
    obj = EnvironmentVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ENV_DATA
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.name_length == 3
    assert obj.data_length == 3
    assert obj.reserved == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x01\x02\x03"
    assert obj.pack() == raw


def test_system_variable_double():
    raw = (DATA_DIR / "SYS_VARIABLE__DOUBLE.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.DOUBLE
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 8
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x00\x00\x00\x00\x00\x00\x00\x40"
    assert obj.pack() == raw


def test_system_variable_long():
    raw = (DATA_DIR / "SYS_VARIABLE__LONG.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.LONG
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 4
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x11\x11\x11\x11"
    assert obj.pack() == raw


def test_system_variable_string():
    raw = (DATA_DIR / "SYS_VARIABLE__STRING.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.STRING
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 3
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"xyz"
    assert obj.pack() == raw


def test_system_variable_double_array():
    raw = (DATA_DIR / "SYS_VARIABLE__DOUBLEARRAY.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.DOUBLEARRAY
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 24
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == (
        b"\x00\x00\x00\x00\x00\x00\xf0\x3f"
        b"\x00\x00\x00\x00\x00\x00\x00\x40"
        b"\x00\x00\x00\x00\x00\x00\x08\x40"
    )
    assert obj.pack() == raw


def test_system_variable_long_array():
    raw = (DATA_DIR / "SYS_VARIABLE__LONGARRAY.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.LONGARRAY
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 12
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00"
    assert obj.pack() == raw


def test_system_variable_longlong():
    raw = (DATA_DIR / "SYS_VARIABLE__LONGLONG.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.LONGLONG
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 8
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x11\x11\x11\x11\x11\x11\x11\x11"
    assert obj.pack() == raw


def test_system_variable_bytearray():
    raw = (DATA_DIR / "SYS_VARIABLE__BYTEARRAY.lobj").read_bytes()
    obj = SystemVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.type is SysVarType.BYTEARRAY
    assert obj.representation == 0x22222222
    assert obj.reserved1 == 0x4444444433333333
    assert obj.name_length == 3
    assert obj.data_length == 3
    assert obj.reserved2 == 0
    assert obj.name == "xyz"
    assert obj.data == b"\x01\x02\x03"
    assert obj.pack() == raw


def test_real_time_clock():
    raw = (DATA_DIR / "REALTIMECLOCK.lobj").read_bytes()
    obj = RealTimeClock.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.REALTIMECLOCK
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.time == 0x1111111111111111
    assert obj.logging_offset == 0x2222222222222222
    assert obj.pack() == raw


def test_driver_overrun():
    raw = (DATA_DIR / "OVERRUN_ERROR.lobj").read_bytes()
    obj = DriverOverrun.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.OVERRUN_ERROR
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.bus_type is BusType.CAN
    assert obj.channel == 0x2222
    assert obj.reserved == 0x3333
    assert obj.pack() == raw


def test_event_comment():
    raw = (DATA_DIR / "EVENT_COMMENT.lobj").read_bytes()
    obj = EventComment.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.EVENT_COMMENT
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.commented_event_type == 0x11111111
    assert obj.text_length == 3
    assert obj.reserved == 0
    assert obj.text == "xyz"
    assert obj.pack() == raw


def test_global_marker():
    raw = (DATA_DIR / "GLOBAL_MARKER.lobj").read_bytes()
    obj = GlobalMarker.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.GLOBAL_MARKER
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.commented_event_type == 0x11111111
    assert obj.foreground_color == 0x22222222
    assert obj.background_color == 0x33333333
    assert obj.is_relocatable == 0x44
    assert obj.reserved1 == 0
    assert obj.reserved2 == 0
    assert obj.group_name_length == 3
    assert obj.marker_name_length == 3
    assert obj.description_length == 3
    assert obj.group_name == "xyz"
    assert obj.marker_name == "xyz"
    assert obj.description == "xyz"
    assert obj.pack() == raw


def test_function_bus():
    raw = (DATA_DIR / "FUNCTION_BUS.lobj").read_bytes()
    obj = FunctionBus.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 3
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.FUNCTION_BUS
    assert obj.header.object_flags is ObjFlags.TIME_TEN_MICS
    assert obj.header.object_static_size == 16
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x22222222222222
    assert obj.object_type is FunctionBusType.SIGNAL
    assert obj.ve_type == 0x11111111
    assert obj.name_length == 21
    assert obj.data_length == 21
    assert obj.name == "functionBusObjectName"
    assert obj.data == b"functionBusObjectData"
    assert obj.pack() == raw


def test_trigger_condition():
    raw = (DATA_DIR / "TRIGGER_CONDITION.lobj").read_bytes()
    obj = TriggerCondition.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 3
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.TRIGGER_CONDITION
    assert obj.header.object_flags is ObjFlags.TIME_TEN_MICS
    assert obj.header.object_static_size == 12
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x22222222222222
    assert obj.state is TriggerConditionStatus.START
    assert obj.trigger_block_name_length == 17
    assert obj.trigger_condition_length == 18
    assert obj.trigger_block_name == "TriggerBlockName_"
    assert obj.trigger_condition == "TriggerCondition__"
    assert obj.pack() == raw
