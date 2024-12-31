import datetime
import os
import time
import zlib
from contextlib import AbstractContextManager
from typing import Any, BinaryIO

from blf.constants import Compression, ObjFlags
from blf.general import FileStatistics, LogContainer, ObjectWithHeader, SystemTime


class BlfWriter(AbstractContextManager["BlfWriter"]):
    def __init__(
        self,
        file: os.PathLike[Any],
        compression_level: Compression = Compression.NONE,
        buffer_size: int = 1024,
    ) -> None:
        self._buffer_size = buffer_size
        self._buffer = bytearray()
        self._measurement_start_time = time.time()
        self._time_of_last_object = self._measurement_start_time

        self._file: BinaryIO
        if isinstance(file, (str, bytes, os.PathLike)):
            self._file = open(file, "wb")  # noqa: SIM115
        elif hasattr(file, "write"):
            self._file = file
        else:
            err_msg = f"Unsupported type {type(file)}"
            raise TypeError(err_msg)

        # write file statistics
        self._file_statistics = FileStatistics.new()
        self._file_statistics.compression_level = compression_level
        self._file.write(self._file_statistics.pack())

    def write(self, obj: ObjectWithHeader) -> None:
        obj_data = obj.pack()
        self._buffer.extend(obj_data)
        self._file_statistics.object_count += 1
        self._file_statistics.uncompressed_file_size += len(obj_data)
        self._time_of_last_object = time.time()

        if len(self._buffer) >= self._buffer_size:
            self._flush_buffer()

    def _flush_buffer(self) -> None:
        if not self._buffer:
            return

        if self._file_statistics.compression_level > Compression.NONE:
            compressed_data = zlib.compress(
                self._buffer, level=self._file_statistics.compression_level
            )
        else:
            compressed_data = self._buffer

        log_container = LogContainer.new(
            data=compressed_data,
            time_stamp=round((time.time() - self._measurement_start_time) * 1e9),
            flags=ObjFlags.TIME_ONE_NANS,
        )

        self._file.write(log_container.pack())
        self._buffer.clear()

    def _update_file_statistics(self) -> None:
        self._file_statistics.last_object_time = SystemTime.from_datetime(
            datetime.datetime.fromtimestamp(self._time_of_last_object, datetime.timezone.utc)
        )
        self._file.seek(0)
        self._file.write(self._file_statistics.pack())

    def close(self) -> None:
        if not self._file.closed:
            self._flush_buffer()
            self._update_file_statistics()
            self._file.close()

    def __enter__(self) -> "BlfWriter":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
