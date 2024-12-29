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
    CanErrorFrame,
    CanErrorFrameExt,
    CanFdErrorFrame64,
    CanFdMessage,
    CanFdMessage64,
    CanMessage,
    CanMessage2,
)
from blf.constants import OBJ_SIGNATURE, OBJ_SIGNATURE_SIZE, ObjTypeEnum
from blf.general import (
    AppText,
    FileStatistics,
    LogContainer,
    ObjectHeaderBase,
    ObjectWithHeader,
)

LOG = logging.getLogger("blf")
_OBJ_HEADER_BASE_SIZE: Final = ObjectHeaderBase.calc_size()
_FILE_STATISTICS_SIZE: Final = FileStatistics.calc_size()


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

        obj_data = self._file.read(_FILE_STATISTICS_SIZE)
        if len(obj_data) < _FILE_STATISTICS_SIZE or not obj_data.startswith(b"LOGG"):
            err_msg = "Unexpected file format"
            raise ValueError(err_msg)

        self.file_statistics = FileStatistics.unpack(self._file.read(_FILE_STATISTICS_SIZE))

        self._incomplete_data: bytes = b""
        self._generator = self._generate_objects(self._file)

    def _generate_objects(self, stream: BinaryIO) -> Iterator[ObjectWithHeader]:
        while True:
            signature = stream.read(OBJ_SIGNATURE_SIZE)
            if len(signature) != OBJ_SIGNATURE_SIZE:
                self._incomplete_data = signature
                break
            if signature != OBJ_SIGNATURE:
                # skip padding byte and try again
                stream.seek(1 - OBJ_SIGNATURE_SIZE, os.SEEK_CUR)
                continue

            header_base_data = signature + stream.read(_OBJ_HEADER_BASE_SIZE - OBJ_SIGNATURE_SIZE)
            if len(header_base_data) < _OBJ_HEADER_BASE_SIZE:
                self._incomplete_data = header_base_data
                break

            # read object data
            header_base = ObjectHeaderBase.unpack(header_base_data)
            obj_data = header_base_data + stream.read(
                header_base.object_size - _OBJ_HEADER_BASE_SIZE
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
                container = LogContainer.unpack(obj_data)
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
                yield obj_class.unpack(obj_data)

    def __iter__(self) -> Iterator[ObjectWithHeader]:
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


OBJ_MAP: Final[dict[int, type[ObjectWithHeader]]] = {
    ObjTypeEnum.CAN_MESSAGE.value: CanMessage,
    ObjTypeEnum.CAN_ERROR.value: CanErrorFrame,
    ObjTypeEnum.CAN_STATISTIC.value: CanDriverStatistic,
    ObjTypeEnum.LOG_CONTAINER.value: LogContainer,
    ObjTypeEnum.CAN_DRIVER_ERROR.value: CanDriverError,
    ObjTypeEnum.APP_TEXT.value: AppText,
    ObjTypeEnum.CAN_ERROR_EXT.value: CanErrorFrameExt,
    ObjTypeEnum.CAN_DRIVER_ERROR_EXT.value: CanDriverErrorExt,
    ObjTypeEnum.CAN_MESSAGE2.value: CanMessage2,
    ObjTypeEnum.CAN_FD_MESSAGE.value: CanFdMessage,
    ObjTypeEnum.CAN_FD_MESSAGE_64.value: CanFdMessage64,
    ObjTypeEnum.CAN_FD_ERROR_64.value: CanFdErrorFrame64,
}
