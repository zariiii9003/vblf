from tests import DATA_DIR
from vblf.constants import ObjFlags, ObjType
from vblf.flexray import FlexrayVFrReceiveMsgEx


def test_flexray_v_fr_receive_msg_ex():
    raw = (DATA_DIR / "FR_RCVMESSAGE_EX.lobj").read_bytes()
    obj = FlexrayVFrReceiveMsgEx.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.FR_RCVMESSAGE_EX
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.channel == 0x1111
    assert obj.version == 0x2222
    assert obj.channel_mask == 0x3333
    assert obj.dir_flags == 0x4444
    assert obj.client_index == 0x55555555
    assert obj.cluster_no == 0x66666666
    assert obj.frame_id == 0x7777
    assert obj.header_crc1 == 0x8888
    assert obj.header_crc2 == 0x9999
    assert obj.byte_count == 0xAAAA
    assert obj.data_count == 254
    assert obj.cycle == 0xCCCC
    assert obj.tag == 0xDDDDDDDD
    assert obj.data == 0xEEEEEEEE
    assert obj.frame_flags == 0xFFFFFFFF
    assert obj.app_parameter == 0x11111111
    assert obj.frame_crc == 0x22222222
    assert obj.frame_length_ns == 0x33333333
    assert obj.frame_id1 == 0x4444
    assert obj.pdu_offset == 0x5555
    assert obj.blf_log_mask == 0x6666
    assert obj.reserved == (
        b"\x77\x77"
        b"\x88\x88\x88\x88\x99\x99\x99\x99\xaa\xaa\xaa\xaa"
        b"\xbb\xbb\xbb\xbb\xcc\xcc\xcc\xcc\xdd\xdd\xdd\xdd"
    )
    assert obj.pack() == raw
