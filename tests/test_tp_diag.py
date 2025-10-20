from tests import DATA_DIR
from vblf.constants import ObjFlags, ObjType
from vblf.tp_diag import DiagRequestInterpretation


def test_diag_request_interpretation():
    raw = (DATA_DIR / "DIAG_REQUEST_INTERPRETATION.lobj").read_bytes()
    obj = DiagRequestInterpretation.unpack(raw)
    assert obj.header.base.signature == b"LOBJ"
    assert obj.header.base.header_size == 32
    assert obj.header.base.header_version == 1
    assert obj.header.base.object_size == len(raw)
    assert obj.header.base.object_type is ObjType.DIAG_REQUEST_INTERPRETATION
    assert obj.header.object_flags is ObjFlags.TIME_ONE_NANS
    assert obj.header.client_index == 0x1111
    assert obj.header.object_version == 0
    assert obj.header.object_time_stamp == 0x2222222222222222
    assert obj.diag_description_handle == 0x11111111
    assert obj.diag_variant_handle == 0x22222222
    assert obj.diag_service_handle == 0x33333333
    assert obj.ecu_qualifier_length == 3
    assert obj.variant_qualifier_length == 3
    assert obj.service_qualifier_length == 3
    assert obj.ecu_qualifier == "xyz"
    assert obj.variant_qualifier == "xyz"
    assert obj.service_qualifier == "xyz"
    assert obj.pack() == raw
