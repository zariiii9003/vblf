from tests import DATA_DIR
from vblf.can import (
    CanDriverError,
    CanDriverErrorExt,
    CanDriverHwSync,
    CanDriverStatistic,
    CanErrorFrame,
    CanErrorFrameExt,
    CanFdErrorFrame64,
    CanFdFlags,
    CanFdMessage,
    CanFdMessage64,
    CanMessage,
    CanMessage2,
    CanOverloadFrame,
)
from vblf.constants import ObjFlags, ObjType


def test_can_message():
    raw = (DATA_DIR / "CAN_MESSAGE.lobj").read_bytes()
    obj = CanMessage.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_MESSAGE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.flags == 0x22
    assert obj.dlc == 0x33
    assert obj.frame_id == 0x44444444
    assert obj.data == b"\x55\x66\x77\x88\x99\xaa\xbb\xcc"
    assert obj.pack() == raw


def test_can_message2():
    raw = (DATA_DIR / "CAN_MESSAGE2.lobj").read_bytes()
    obj = CanMessage2.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_MESSAGE2
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.flags == 0x22
    assert obj.dlc == 0x33
    assert obj.frame_id == 0x44444444
    assert obj.data == b"\x55\x66\x77\x88\x99\xaa\xbb\xcc"
    assert obj.frame_length == 0xDDDDDDDD
    assert obj.bit_count == 0xEE
    assert obj.reserved1 == 0xFF
    assert obj.reserved2 == 0x1111
    assert obj.pack() == raw


def test_canfd_message():
    raw = (DATA_DIR / "CAN_FD_MESSAGE.lobj").read_bytes()
    obj = CanFdMessage.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_FD_MESSAGE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.flags == 0x22
    assert obj.dlc == 0x33
    assert obj.frame_id == 0x44444444
    assert obj.frame_length == 0x55555555
    assert obj.arb_bit_count == 0x66
    assert obj.canfd_flags == 0x77
    assert obj.valid_data_bytes == 64
    assert obj.reserved1 == 0x99
    assert obj.reserved2 == 0xAAAAAAAA
    assert obj.data == bytes(range(64))
    assert obj.reserved3 == 0
    assert obj.pack() == raw


def test_canfd_message64():
    raw = (DATA_DIR / "CAN_FD_MESSAGE_64.lobj").read_bytes()
    obj = CanFdMessage64.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_FD_MESSAGE_64
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 1181363
    assert obj.channel == 1
    assert obj.dlc == 8
    assert obj.valid_data_bytes == 8
    assert obj.tx_count == 0
    assert obj.frame_id == 0xA8
    assert obj.frame_length == 104238
    assert obj.flags == 3158016
    assert isinstance(obj.flags, CanFdFlags)
    assert obj.btr_cfg_arb == 0x46500250
    assert obj.btr_cfg_data == 0x4B280150
    assert obj.time_offset_brs_ns == 68863
    assert obj.time_offset_crc_del_ns == 16638
    assert obj.bit_count == 134
    assert obj.dir == 0
    assert obj.ext_data_offset == 80
    assert obj.crc == 2147501637
    assert obj.data == b"\xb8\xda\x1f\x80\xff\x00\x00\x00"
    assert obj.btr_ext_arb == 0x20011736
    assert obj.btr_ext_data == 0x2000091C
    assert obj.pack() == raw


def test_can_driver_statistic():
    raw = (DATA_DIR / "CAN_STATISTIC.lobj").read_bytes()
    obj = CanDriverStatistic.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_STATISTIC
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
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
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_DRIVER_ERROR
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
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
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_DRIVER_ERROR_EXT
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.tx_errors == 0x22
    assert obj.rx_errors == 0x33
    assert obj.error_code == 0x44444444
    assert obj.flags == 0x55555555
    assert obj.state == 0x66
    assert obj.pack() == raw


def test_can_error_frame():
    raw = (DATA_DIR / "CAN_ERROR.lobj").read_bytes()
    obj = CanErrorFrame.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_ERROR
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.length == 0x2222
    assert obj.reserved == 0
    assert obj.pack() == raw


def test_can_error_frame_ext():
    raw = (DATA_DIR / "CAN_ERROR_EXT.lobj").read_bytes()
    obj = CanErrorFrameExt.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_ERROR_EXT
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.length == 0x2222
    assert obj.flags == 0x33333333
    assert obj.ecc == 0x44
    assert obj.position == 0x55
    assert obj.dlc == 0x66
    assert obj.reserved1 == 0x77
    assert obj.frame_length_in_ns == 0x88888888
    assert obj.frame_id == 0x99999999
    assert obj.flags_ext == 0xAAAA
    assert obj.reserved2 == 0xBBBB
    assert obj.data == b"\xcc\xdd\xee\xff\x11\x22\x33\x44"
    assert obj.pack() == raw


def test_canfd_error_frame64():
    raw = (DATA_DIR / "CAN_FD_ERROR_64.lobj").read_bytes()
    obj = CanFdErrorFrame64.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_FD_ERROR_64
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x11
    assert obj.dlc == 0x22
    assert obj.valid_data_bytes == 64
    assert obj.ecc == 0x44
    assert obj.flags == 0x5555
    assert obj.error_code_ext == 0x6666
    assert obj.ext_flags == 0x7777
    assert obj.ext_data_offset == 140
    assert obj.reserved1 == 0x99
    assert obj.frame_id == 0xAAAAAAAA
    assert obj.frame_length == 0xBBBBBBBB
    assert obj.btr_cfg_arb == 0xCCCCCCCC
    assert obj.btr_cfg_data == 0xDDDDDDDD
    assert obj.time_offset_brs_ns == 0xEEEEEEEE
    assert obj.time_offset_crc_del_ns == 0xFFFFFFFF
    assert obj.crc == 0x11111111
    assert obj.error_position == 0x2222
    assert obj.reserved2 == 0x3333
    assert obj.data == bytes(range(64))
    assert obj.btr_ext_arb == 0x11111111
    assert obj.btr_ext_data == 0x22222222
    assert obj.pack() == raw


def test_can_driver_hw_sync():
    raw = (DATA_DIR / "CAN_DRIVER_SYNC.lobj").read_bytes()
    obj = CanDriverHwSync.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_DRIVER_SYNC
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.flags == 0x22
    assert obj.reserved1 == 0x33
    assert obj.reserved2 == 0
    assert obj.pack() == raw


def test_can_overload_frame():
    raw = (DATA_DIR / "CAN_OVERLOAD.lobj").read_bytes()
    obj = CanOverloadFrame.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.CAN_OVERLOAD
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.reserved1 == 0x2222
    assert obj.reserved2 == 0
    assert obj.pack() == raw
