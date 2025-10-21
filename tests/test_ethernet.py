from tests import DATA_DIR
from vblf.constants import ObjFlags, ObjType
from vblf.ethernet import EthernetFrameEx, EthernetStatistic


def test_ethernet_frame_ex():
    raw = (DATA_DIR / "ETHERNET_FRAME_EX.lobj").read_bytes()
    obj = EthernetFrameEx.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ETHERNET_FRAME_EX
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.struct_length == 30  # ?
    assert obj.flags == 0x1111
    assert obj.channel == 0x2222
    assert obj.hardware_channel == 0x3333
    assert obj.frame_duration == 0x4444444444444444
    assert obj.frame_checksum == 0x55555555
    assert obj.dir == 0x6666
    assert obj.frame_length == 3
    assert obj.frame_handle == 0x88888888
    assert obj.reserved == 0x99999999
    assert obj.frame_data == b"\xaa\xbb\xcc"
    assert obj.pack() == raw


def test_ethernet_statistic():
    raw = (DATA_DIR / "ETHERNET_STATISTIC.lobj").read_bytes()
    obj = EthernetStatistic.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.ETHERNET_STATISTIC
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.reserved_1 == 0x0
    assert obj.reserved_2 == 0x0
    assert obj.rcv_ok_hw == 0x2222222222222222
    assert obj.xmit_ok_hw == 0x3333333333333333
    assert obj.rcv_error_hw == 0x4444444444444444
    assert obj.xmit_error_hw == 0x5555555555555555
    assert obj.rcv_bytes_hw == 0x6666666666666666
    assert obj.xmit_bytes_hw == 0x7777777777777777
    assert obj.rcv_no_buffer_hw == 0x8888888888888888
    assert obj.sqi == 0x7999
    assert obj.hardware_channel == 0xAAAA
    assert obj.reserved_3 == 0x0
    assert obj.pack() == raw
