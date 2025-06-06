import datetime
import os
import time
import zlib
from contextlib import AbstractContextManager
from typing import Any, BinaryIO, Final

from vblf.constants import Compression, ObjFlags
from vblf.general import FileStatistics, HeaderWithBase, LogContainer, ObjectWithHeader, SystemTime

BYTE_ALIGNMENT: Final = 8


class BlfWriter(AbstractContextManager["BlfWriter"]):
    """Binary Log Format (BLF) file writer.

    Writes Vector BLF log files with optional compression. Handles automatic buffering
    and container creation for optimal file structure.

    :param file: Path to BLF file or file-like object
    :param compression_level: Compression level (0-9), defaults to no compression
    :param buffer_size: Size of internal buffer in bytes before flushing, defaults to 128 KiB
    :raises TypeError: If file parameter is of unsupported type
    """

    def __init__(
        self,
        file: os.PathLike[Any],
        compression_level: Compression = Compression.NONE,
        buffer_size: int = 128 * 1024,
    ) -> None:
        """Initialize BLF writer.

        See class documentation for details.
        """
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

    def write(self, obj: ObjectWithHeader[HeaderWithBase]) -> None:
        """Write an object to the BLF file.

        The object is first buffered and only written to disk when the buffer is full
        or when the file is closed.

        :param obj: Object to write
        :raises ValueError: If object size doesn't match its header
        """
        # byte alignment
        if rest := len(self._buffer) % BYTE_ALIGNMENT:
            self._buffer.extend(b"\x00" * (BYTE_ALIGNMENT - rest))
        obj_data = obj.pack()
        if len(obj_data) != obj.header.base.object_size:
            err_msg = f"Object size mismatch: {len(obj_data)} != {obj.header.base.object_size}"
            raise ValueError(err_msg)
        self._buffer.extend(obj_data)
        self._file_statistics.object_count += 1
        self._file_statistics.uncompressed_file_size += len(obj_data)
        self._time_of_last_object = time.time()

        if len(self._buffer) >= self._buffer_size:
            self._flush_container()

    def _flush_container(self) -> None:
        """Flush the internal buffer to disk.

        Creates a LogContainer with the buffered data and writes it to the file.
        Handles compression if enabled.
        """
        if not self._buffer:
            return

        # byte alignment
        if rest := self._file.tell() % BYTE_ALIGNMENT:
            self._file.write(b"\x00" * (BYTE_ALIGNMENT - rest))

        buffer, self._buffer = self._buffer[: self._buffer_size], self._buffer[self._buffer_size :]

        if self._file_statistics.compression_level > Compression.NONE:
            compressed_data = zlib.compress(buffer, level=self._file_statistics.compression_level)
        else:
            compressed_data = bytes(buffer)

        log_container = LogContainer.new(
            data=compressed_data,
            time_stamp=round((time.time() - self._measurement_start_time) * 1e9),
            flags=ObjFlags.TIME_ONE_NANS,
        )
        self._file.write(log_container.pack())
        self._file_statistics.file_size = self._file.tell()

    def _update_file_statistics(self) -> None:
        """Update file statistics and write them to the beginning of the file.

        Updates the object count, file size and timestamps in the file header.
        """
        self._file_statistics.last_object_time = SystemTime.from_datetime(
            datetime.datetime.fromtimestamp(self._time_of_last_object, datetime.timezone.utc)
        )
        self._file.seek(0)
        self._file.write(self._file_statistics.pack())

    def close(self) -> None:
        """Close the BLF file.

        Flushes any remaining buffered data and updates file statistics before closing.
        """
        if not self._file.closed:
            while self._buffer:
                self._flush_container()
            self._update_file_statistics()
            self._file.close()

    def __enter__(self) -> "BlfWriter":
        """Enter context manager.

        :returns: BlfWriter instance
        """
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Exit context manager and close file.

        :param exc_type: Exception type if an exception occurred
        :param exc_value: Exception instance if an exception occurred
        :param traceback: Traceback if an exception occurred
        """
        self.close()
