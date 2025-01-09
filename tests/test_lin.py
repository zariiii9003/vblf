from tests import DATA_DIR
from vblf.constants import ObjFlags, ObjType
from vblf.lin import LinMessage, LinMessage2


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
    assert obj.id == 0x22
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


def test_lin_message2():
    raw = (DATA_DIR / "LIN_MESSAGE2.lobj").read_bytes()
    obj = LinMessage2.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.LIN_MESSAGE2
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 3
    assert obj.header.object_time_stamp == 0x2222222222222222
    lin_bus_event = obj.lin_timestamp_event.lin_msg_descr_event.lin_synch_field_event.lin_bus_event
    assert lin_bus_event.sof == 0x1111111111111111
    assert lin_bus_event.event_baudrate == 0x22222222
    assert lin_bus_event.channel == 0x3333
    assert lin_bus_event.reserved == b"\x44\x44"
    lin_synch_field_event = obj.lin_timestamp_event.lin_msg_descr_event.lin_synch_field_event
    assert lin_synch_field_event.synch_break_length == 0x1111111111111111
    assert lin_synch_field_event.synch_del_length == 0x2222222222222222
    assert obj.lin_timestamp_event.lin_msg_descr_event.supplier_id == 0x1111
    assert obj.lin_timestamp_event.lin_msg_descr_event.message_id == 0x2222
    assert obj.lin_timestamp_event.lin_msg_descr_event.nad == 0x33
    assert obj.lin_timestamp_event.lin_msg_descr_event.id == 0x44
    assert obj.lin_timestamp_event.lin_msg_descr_event.dlc == 0x55
    assert obj.lin_timestamp_event.lin_msg_descr_event.checksum_model == 0x66
    assert obj.lin_timestamp_event.databyte_timestamps == (
        0x1111111111111111,
        0x2222222222222222,
        0x3333333333333333,
        0x4444444444444444,
        0x5555555555555555,
        0x6666666666666666,
        0x7777777777777777,
        0x8888888888888888,
        0x9999999999999999,
    )
    assert obj.data == b"\x11\x22\x33\x44\x55\x66\x77\x88"
    assert obj.crc == 0x9999
    assert obj.direction == 0xAA
    assert obj.simulated == 0xBB
    assert obj.is_etf == 0xCC
    assert obj.etf_assoc_index == 0xDD
    assert obj.etf_assoc_etf_id == 0xEE
    assert obj.fsm_id == 0xFF
    assert obj.fsm_state == 0x11
    assert obj.reserved == b"\x22\x33\x33"
    assert obj.resp_baudrate == 0x44444444
    assert obj.exact_header_baudrate == 5.0
    assert obj.early_stopbit_offset == 0x66666666
    assert obj.early_stopbit_offset_response == 0x77777777
    assert obj.pack() == raw
