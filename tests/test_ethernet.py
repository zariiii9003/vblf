from tests import DATA_DIR
from vblf.constants import ObjFlags, ObjType
from vblf.ethernet import EthernetFrameEx


def test_system_variable_double_array():
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
