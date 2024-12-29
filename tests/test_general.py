from blf.constants import AppId, ObjFlags, ObjTypeEnum, TriggerFlag
from blf.general import AppText, AppTrigger, EnvironmentVariable, FileStatistics
from tests import DATA_DIR


def test_file_statistics():
    raw = (DATA_DIR / "FILE_STATISTICS.logg").read_bytes()
    obj = FileStatistics.unpack(raw)
    assert obj.signature == b"LOGG"
    assert obj.statistics_size == 144
    assert obj.api_number == 0x3E4630
    assert obj.application_id is AppId.CANOE
    assert obj.compression_level == 1
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
    assert obj.header.base.object_size == 97
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
    assert obj.header.base.object_size == 56
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
    assert obj.header.base.object_size == 55
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
    assert obj.header.base.object_size == 59
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
    assert obj.header.base.object_size == 54
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
    assert obj.header.base.object_size == 54
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
