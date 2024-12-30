from blf.constants import (
    AppId,
    BusType,
    Compression,
    ObjFlags,
    ObjTypeEnum,
    SysVarType,
    TriggerFlag,
)
from blf.general import (
    AppText,
    AppTrigger,
    DriverOverrun,
    EnvironmentVariable,
    FileStatistics,
    RealTimeClock,
    SystemVariable,
)
from tests import DATA_DIR


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
    assert obj.uncompressed_file_size == 0x557CAB7
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
    assert obj.header.base.object_type is ObjTypeEnum.APP_TEXT
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0
    assert obj.source == 1
    assert obj.reserved1 == 16843009
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
    assert obj.header.base.object_type is ObjTypeEnum.APP_TRIGGER
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.pre_trigger_time == 1229782938247303441
    assert obj.post_trigger_time == 2459565876494606882
    assert obj.channel == 13107
    assert obj.flags == TriggerFlag.SINGLE_TRIGGER
    assert obj.app_specific == 1145324612
    assert obj.pack() == raw


def test_environment_variable_integer():
    raw = (DATA_DIR / "ENV_INTEGER.lobj").read_bytes()
    obj = EnvironmentVariable.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjTypeEnum.ENV_INTEGER
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
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
    assert obj.header.base.object_type is ObjTypeEnum.ENV_DOUBLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
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
    assert obj.header.base.object_type is ObjTypeEnum.ENV_STRING
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
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
    assert obj.header.base.object_type is ObjTypeEnum.ENV_DATA
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.DOUBLE
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.LONG
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.STRING
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.DOUBLEARRAY
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.LONGARRAY
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.LONGLONG
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.SYS_VARIABLE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.type is SysVarType.BYTEARRAY
    assert obj.representation == 572662306
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
    assert obj.header.base.object_type is ObjTypeEnum.REALTIMECLOCK
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.time == 1229782938247303441
    assert obj.logging_offset == 2459565876494606882
    assert obj.pack() == raw


def test_driver_overrun():
    raw = (DATA_DIR / "OVERRUN_ERROR.lobj").read_bytes()
    obj = DriverOverrun.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjTypeEnum.OVERRUN_ERROR
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.bus_type is BusType.CAN
    assert obj.channel == 8738
    assert obj.reserved == 13107
    assert obj.pack() == raw
