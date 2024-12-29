from blf.can import (
    CanDriverError,
    CanDriverErrorExt,
    CanDriverStatistic,
    CanErrorFrame,
    CanErrorFrameExt,
    CanFdErrorFrame64,
    CanFdMessage,
    CanFdMessage64,
    CanFdMessage64Flags,
    CanMessage,
    CanMessage2,
)
from tests import DATA_DIR


def test_can_message():
    raw = (DATA_DIR / "CAN_MESSAGE.lobj").read_bytes()
    obj = CanMessage.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 48
    assert obj.header.object_type == 1
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.flags == 34
    assert obj.dlc == 51
    assert obj.frame_id == 1145324612
    assert obj.data == bytes([0x55, 0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB, 0xCC])
    assert obj.pack() == raw


def test_can_message2():
    raw = (DATA_DIR / "CAN_MESSAGE2.lobj").read_bytes()
    obj = CanMessage2.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 56
    assert obj.header.object_type == 86
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.flags == 34
    assert obj.dlc == 51
    assert obj.frame_id == 1145324612
    assert obj.data == b"\x55\x66\x77\x88\x99\xaa\xbb\xcc"
    assert obj.frame_length == 3722304989
    assert obj.bit_count == 238
    assert obj.reserved1 == 255
    assert obj.reserved2 == 4369
    assert obj.pack() == raw


def test_canfd_message():
    raw = (DATA_DIR / "CAN_FD_MESSAGE.lobj").read_bytes()
    obj = CanFdMessage.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 120
    assert obj.header.object_type == 100
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.dlc == 51
    assert obj.frame_id == 1145324612
    assert obj.frame_length == 1431655765
    assert obj.arb_bit_count == 102
    assert obj.canfd_flags == 119
    assert obj.valid_data_bytes == 64
    assert obj.reserved1 == 153
    assert obj.reserved2 == 2863311530
    assert obj.data == bytes(range(64))
    assert obj.reserved3 == 0
    assert obj.pack() == raw


def test_canfd_message64():
    raw = (DATA_DIR / "CAN_FD_MESSAGE_64.lobj").read_bytes()
    obj = CanFdMessage64.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 88
    assert obj.header.object_type == 101
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 1181363
    assert obj.channel == 1
    assert obj.dlc == 8
    assert obj.valid_data_bytes == 8
    assert obj.tx_count == 0
    assert obj.frame_id == 168
    assert obj.frame_length == 104238
    assert obj.flags == 3158016
    assert isinstance(obj.flags, CanFdMessage64Flags)
    assert obj.btr_cfg_arb == 1179648592
    assert obj.btr_cfg_data == 1260912976
    assert obj.time_offset_brs_ns == 68863
    assert obj.time_offset_crc_del_ns == 16638
    assert obj.bit_count == 134
    assert obj.dir == 0
    assert obj.ext_data_offset == 80
    assert obj.crc == 2147501637
    assert obj.data == b"\xb8\xda\x1f\x80\xff\x00\x00\x00"
    assert obj.btr_ext_arb == 536942390
    assert obj.btr_ext_data == 536873244
    assert obj.pack() == raw


def test_can_driver_statistic():
    raw = (DATA_DIR / "CAN_STATISTIC.lobj").read_bytes()
    obj = CanDriverStatistic.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 64
    assert obj.header.object_type == 4
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 1015388138
    assert obj.channel == 1
    assert obj.bus_load == 3286
    assert obj.standard_data_frames == 2093
    assert obj.extended_data_frames == 93
    assert obj.standard_remote_frames == 0
    assert obj.extended_remote_frames == 0
    assert obj.error_frames == 0
    assert obj.overload_frames == 0
    assert obj.reserved == 0
    assert obj.pack() == raw


def test_can_driver_error():
    raw = (DATA_DIR / "CAN_DRIVER_ERROR.lobj").read_bytes()
    obj = CanDriverError.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 40
    assert obj.header.object_type == 31
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 16971450
    assert obj.channel == 1
    assert obj.tx_errors == 0
    assert obj.rx_errors == 0
    assert obj.error_code == 104
    assert obj.pack() == raw


def test_can_driver_error_ext():
    raw = (DATA_DIR / "CAN_DRIVER_ERROR_EXT.lobj").read_bytes()
    obj = CanDriverErrorExt.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 64
    assert obj.header.object_type == 74
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.tx_errors == 34
    assert obj.rx_errors == 51
    assert obj.error_code == 1145324612
    assert obj.flags == 1431655765
    assert obj.state == 102
    assert obj.pack() == raw


def test_can_error_frame():
    raw = (DATA_DIR / "CAN_ERROR.lobj").read_bytes()
    obj = CanErrorFrame.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 40
    assert obj.header.object_type == 2
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.length == 8738
    assert obj.reserved == 0
    assert obj.pack() == raw


def test_can_error_frame_ext():
    raw = (DATA_DIR / "CAN_ERROR_EXT.lobj").read_bytes()
    obj = CanErrorFrameExt.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 64
    assert obj.header.object_type == 73
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 4369
    assert obj.length == 8738
    assert obj.flags == 858993459
    assert obj.ecc == 68
    assert obj.position == 85
    assert obj.dlc == 102
    assert obj.reserved1 == 119
    assert obj.frame_length_in_ns == 2290649224
    assert obj.frame_id == 2576980377
    assert obj.flags_ext == 43690
    assert obj.reserved2 == 48059
    assert obj.data == b"\xcc\xdd\xee\xff\x11\x22\x33\x44"
    assert obj.pack() == raw


def test_canfd_error_frame64():
    raw = (DATA_DIR / "CAN_FD_ERROR_64.lobj").read_bytes()
    obj = CanFdErrorFrame64.unpack(raw)
    assert obj.header.signature == b"LOBJ"
    assert obj.header.header_size == 32
    assert obj.header.header_version == 1
    assert obj.header.object_size == 152
    assert obj.header.object_type == 104
    assert obj.header.object_flags == 2
    assert obj.header.client_index == 4369
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 2459565876494606882
    assert obj.channel == 17
    assert obj.dlc == 34
    assert obj.valid_data_bytes == 64
    assert obj.ecc == 68
    assert obj.flags == 21845
    assert obj.error_code_ext == 26214
    assert obj.ext_flags == 30583
    assert obj.ext_data_offset == 140
    assert obj.reserved1 == 153
    assert obj.frame_id == 2863311530
    assert obj.frame_length == 3149642683
    assert obj.btr_cfg_arb == 3435973836
    assert obj.btr_cfg_data == 3722304989
    assert obj.time_offset_brs_ns == 4008636142
    assert obj.time_offset_crc_del_ns == 4294967295
    assert obj.crc == 286331153
    assert obj.error_position == 8738
    assert obj.reserved2 == 13107
    assert obj.data == bytes(range(64))
    assert obj.btr_ext_arb == 286331153
    assert obj.btr_ext_data == 572662306
    assert obj.pack() == raw
