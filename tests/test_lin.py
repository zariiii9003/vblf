from blf.constants import ObjFlags, ObjType
from blf.lin import LinMessage
from tests import DATA_DIR


def test_lin_message():
    raw = (DATA_DIR / "LIN_MESSAGE.lobj").read_bytes()
    obj = LinMessage.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.LIN_MESSAGE
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.frame_id == 0x22
    assert obj.dlc == 0x33
    assert obj.data == b"\x44\x55\x66\x77\x88\x99\xaa\xbb"
    assert obj.fsm_id == 0xCC
    assert obj.fsm_state == 0xDD
    assert obj.header_time == 0xEE
    assert obj.full_time == 0xFF
    assert obj.crc == 0x1111
    assert obj.dir == 0x22
    assert obj.reserved == b"\x33\x00\x00\x00\x00"
    assert obj.pack() == raw
