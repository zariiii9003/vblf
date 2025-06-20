import tempfile
from pathlib import Path

import pytest

from tests import DATA_DIR
from vblf.can import CanFdMessage64
from vblf.constants import Compression, ObjType
from vblf.general import ObjectHeaderBase
from vblf.reader import OBJ_MAP, BlfReader
from vblf.writer import BlfWriter


@pytest.mark.parametrize(
    "compression_level",
    [Compression.NONE, Compression.SPEED, Compression.DEFAULT, Compression.MAX],
)
def test_roundtrip(compression_level: Compression):
    # Read original objects and compare
    original_objects = []
    roundtrip_objects = []

    for fp in DATA_DIR.rglob("*.lobj"):
        obj_data = fp.read_bytes()
        base = ObjectHeaderBase.unpack_from(obj_data)
        if base.object_type is ObjType.LOG_CONTAINER:
            # BlfReader does not return LogContainer instances, so a comparison is not possible
            continue
        obj_class = OBJ_MAP.get(base.object_type)
        if not obj_class:
            continue
        obj = obj_class.unpack(obj_data)
        original_objects.append(obj)

    # Write objects to BLF file
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "test_output.blf"
        with BlfWriter(output_file, compression_level=compression_level) as writer:
            for obj in original_objects:
                writer.write(obj)
        # Read objects from BLF file and compare
        with BlfReader(output_file) as reader:
            roundtrip_objects.extend(reader)

    assert len(original_objects) == len(roundtrip_objects)
    for original_obj, written_obj in zip(original_objects, roundtrip_objects):
        assert written_obj == original_obj


@pytest.mark.parametrize(
    "compression_level",
    [Compression.NONE, Compression.SPEED, Compression.DEFAULT, Compression.MAX],
)
def test_writer_buffer(compression_level: Compression):
    lobj_path = DATA_DIR / f"{ObjType.CAN_FD_MESSAGE_64.name}.lobj"
    lobj_data = lobj_path.read_bytes()
    original_obj = CanFdMessage64.unpack(lobj_data)

    # written data shall be greater than buffer size
    buffer_size = 128 * 1024  # 128 KiB
    write_count = round(5.0 * buffer_size / len(lobj_data))

    with tempfile.TemporaryDirectory() as temp_dir:
        # write object to file repeatedly
        output_file = Path(temp_dir) / "test_output.blf"
        with BlfWriter(output_file, compression_level=compression_level) as writer:
            for _ in range(write_count):
                writer.write(original_obj)

        # read objects and compare
        with BlfReader(output_file) as reader:
            read_count = 0
            while written_obj := reader.read_object():
                read_count += 1
                assert written_obj == original_obj
            assert read_count == write_count
