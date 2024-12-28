import logging
import os
import zlib
from collections.abc import Iterator
from contextlib import AbstractContextManager
from io import BytesIO
from types import TracebackType
from typing import BinaryIO, Final, Optional, Union

from blf.can import (
    CanDriverError,
    CanDriverErrorExt,
    CanDriverStatistic,
    CanFdErrorFrame64,
    CanFdMessage,
    CanFdMessage64,
)
from blf.constants import OBJ_SIGNATURE, OBJ_SIGNATURE_SIZE, ObjTypeEnum
from blf.general import (
    AppText,
    FileStatisticsEx,
    LogContainer,
    ObjectHeaderBase,
)

LOG = logging.getLogger("blf")


class BlfReader(AbstractContextManager):
    def __init__(self, file: Union[str, bytes, os.PathLike, BinaryIO]):
        self._file: BinaryIO
        if isinstance(file, (str, bytes, os.PathLike)):
            self._file = open(file, "rb")  # noqa: SIM115
        elif isinstance(file, bytes):
            self._file = BytesIO(file)
        elif hasattr(file, "read"):
            self._file = file
        else:
            err_msg = "Unsupported type {type(file)}"
            raise TypeError(err_msg)

        obj_data = self._file.read(FileStatisticsEx.FORMAT.size)
        if len(obj_data) < FileStatisticsEx.FORMAT.size or not obj_data.startswith(b"LOGG"):
            err_msg = "Unexpected file format"
            raise ValueError(err_msg)

        self.file_statistics = FileStatisticsEx.deserialize(
            self._file.read(FileStatisticsEx.FORMAT.size)
        )

        self._incomplete_data: bytes = b""
        self._generator = self._generate_objects(self._file)

    def _generate_objects(self, stream: BinaryIO) -> Iterator[ObjectHeaderBase]:
        while True:
            signature = stream.read(OBJ_SIGNATURE_SIZE)
            if len(signature) != OBJ_SIGNATURE_SIZE:
                self._incomplete_data = signature
                break
            if signature != OBJ_SIGNATURE:
                # skip padding byte and try again
                stream.seek(1 - OBJ_SIGNATURE_SIZE, os.SEEK_CUR)
                continue

            header_base_data = signature + stream.read(
                ObjectHeaderBase.FORMAT.size - OBJ_SIGNATURE_SIZE
            )
            if len(header_base_data) < ObjectHeaderBase.FORMAT.size:
                self._incomplete_data = header_base_data
                break

            # read object data
            header_base = ObjectHeaderBase.deserialize(header_base_data)
            obj_data = header_base_data + stream.read(
                header_base.object_size - ObjectHeaderBase.FORMAT.size
            )
            if len(obj_data) < header_base.object_size:
                self._incomplete_data = obj_data
                break

            # interpret object data
            obj_class = OBJ_MAP.get(header_base.object_type)
            if not obj_class:
                try:
                    object_type = ObjTypeEnum(header_base.object_type).name
                except ValueError:
                    object_type = str(header_base.object_type)

                LOG.info("BLF object type '%s' is not implemented.", object_type)
                continue

            if obj_class is LogContainer:
                # decompress data
                container = LogContainer.deserialize(obj_data)
                uncompressed = (
                    zlib.decompress(container.data)
                    if self.file_statistics.compression_level
                    else container.data
                )

                # prepend incomplete data of previous container
                uncompressed = self._incomplete_data + uncompressed
                self._incomplete_data = b""

                # parse LogContainer data
                yield from self._generate_objects(BytesIO(uncompressed))

            else:
                yield obj_class.deserialize(obj_data)

    def __iter__(self) -> Iterator[ObjectHeaderBase]:
        return self._generator.__iter__()

    def __enter__(self) -> "BlfReader":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._file.close()


OBJ_MAP: Final[dict[int, type[ObjectHeaderBase]]] = {
    ObjTypeEnum.CAN_STATISTIC.value: CanDriverStatistic,
    ObjTypeEnum.LOG_CONTAINER.value: LogContainer,
    ObjTypeEnum.CAN_DRIVER_ERROR.value: CanDriverError,
    ObjTypeEnum.APP_TEXT.value: AppText,
    ObjTypeEnum.CAN_DRIVER_ERROR_EXT.value: CanDriverErrorExt,
    ObjTypeEnum.CAN_FD_MESSAGE.value: CanFdMessage,
    ObjTypeEnum.CAN_FD_MESSAGE_64.value: CanFdMessage64,
    ObjTypeEnum.CAN_FD_ERROR_64.value: CanFdErrorFrame64,
}
