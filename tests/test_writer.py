import tempfile
from pathlib import Path

import pytest

from blf.constants import Compression, ObjType
from blf.general import ObjectHeaderBase
from blf.reader import OBJ_MAP, BlfReader
from blf.writer import BlfWriter
from tests import DATA_DIR


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
            for obj in reader:
                roundtrip_objects.append(obj)

    assert len(original_objects) == len(roundtrip_objects)
    for written_obj, original_obj in zip(original_objects, roundtrip_objects):
        assert written_obj == original_obj
