from blf.general import AppText, FileStatistics
from tests import DATA_DIR


def test_file_statistics():
    raw = (DATA_DIR / "FILE_STATISTICS.logg").read_bytes()
    obj = FileStatistics.unpack(raw)
    assert obj.signature == b"LOGG"
    assert obj.statistics_size == 144
    assert obj.api_number == 0x3E4630
    assert obj.application_id == 2
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
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 97
    assert obj.header.object_type == 65
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0
    assert obj.source == 1
    assert obj.reserved1 == 16843009
    assert obj.text_length == 49
    assert obj.reserved2 == 0
    assert obj.text == "C:\\Users\\user\\Desktop\\project car\\myDatabase.dbc"
    assert obj.pack() == raw
