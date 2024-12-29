import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self


@dataclass
class SystemTime:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHHHHHHH")
    year: int
    month: int
    day_of_week: int
    day: int
    hour: int
    minute: int
    second: int
    milliseconds: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        return cls(*cls._FORMAT.unpack(buffer))

    def pack(self) -> bytes:
        return self._FORMAT.pack(*self.__dict__.values())

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        return cls(*cls._FORMAT.unpack_from(buffer, offset))

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        return self._FORMAT.pack_into(buffer, offset, *self.__dict__.values())


@dataclass
class ObjectHeaderBase:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("4sHHII")
    signature: bytes
    header_size: int
    header_version: int
    object_size: int
    object_type: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        return cls(*cls._FORMAT.unpack(buffer))

    def pack(self) -> bytes:
        return self._FORMAT.pack(*self.__dict__.values())

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        return cls(*cls._FORMAT.unpack_from(buffer, offset))

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        return self._FORMAT.pack_into(buffer, offset, *self.__dict__.values())

    @classmethod
    def calc_size(cls) -> int:
        return cls._FORMAT.size


@dataclass
class VarObjectHeader(ObjectHeaderBase):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase._FORMAT.format + "IHHQ")
    object_flags: int
    object_static_size: int
    object_version: int
    object_time_stamp: int


@dataclass
class ObjectHeader(ObjectHeaderBase):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase._FORMAT.format + "IHHQ")
    object_flags: int
    client_index: int
    object_version: int
    object_time_stamp: int


# @dataclass
# class ObjectHeader2(ObjectHeaderBase):
#     _FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase._FORMAT.format + "IBBHQQ")
#     object_flags: int
#     time_stamp_status: int
#     reserved1: int
#     object_version: int
#     object_time_stamp: int
#     original_time_stamp: int


@dataclass
class ObjectWithHeader:
    header: ObjectHeaderBase

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        raise NotImplementedError

    def pack(self) -> bytes:
        raise NotImplementedError


@dataclass
class FileStatistics:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("4sIIBBBBQQII32xQ64s")
    signature: bytes
    statistics_size: int
    api_number: int
    application_id: int
    compression_level: int
    application_major: int
    application_minor: int
    file_size: int
    uncompressed_file_size: int
    object_count: int
    application_build: int
    measurement_start_time: SystemTime
    last_object_time: SystemTime
    restore_points_offset: int
    reserved: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> "FileStatistics":
        (
            signature,
            statistics_size,
            api_number,
            application_id,
            compression_level,
            application_major,
            application_minor,
            file_size,
            uncompressed_file_size,
            object_count,
            application_build,
            restore_points_offset,
            reserved,
        ) = cls._FORMAT.unpack(buffer)
        measurement_start_time = SystemTime.unpack_from(buffer, 40)
        last_object_time = SystemTime.unpack_from(buffer, 56)
        return cls(
            signature,
            statistics_size,
            api_number,
            application_id,
            compression_level,
            application_major,
            application_minor,
            file_size,
            uncompressed_file_size,
            object_count,
            application_build,
            measurement_start_time,
            last_object_time,
            restore_points_offset,
            reserved,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self._FORMAT.size)
        self._FORMAT.pack_into(
            buffer,
            0,
            self.signature,
            self.statistics_size,
            self.api_number,
            self.application_id,
            self.compression_level,
            self.application_major,
            self.application_minor,
            self.file_size,
            self.uncompressed_file_size,
            self.object_count,
            self.application_build,
            self.restore_points_offset,
            self.reserved,
        )
        self.measurement_start_time.pack_into(buffer, 40)
        self.last_object_time.pack_into(buffer, 56)
        return bytes(buffer)

    @classmethod
    def calc_size(cls) -> int:
        return cls._FORMAT.size


@dataclass
class LogContainer(ObjectWithHeader):
    header: ObjectHeader
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        return cls(header, buffer[header.header_size :])

    def pack(self) -> bytes:
        return self.header.pack() + self.data


@dataclass
class AppText(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIII")
    header: ObjectHeader
    source: int
    reserved1: int
    text_length: int
    reserved2: int
    text: str

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            source,
            reserved1,
            text_length,
            reserved2,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        text_offset = header.header_size + cls._FORMAT.size
        text = buffer[text_offset : text_offset + text_length - 1].decode("mbcs")
        return cls(
            header,
            source,
            reserved1,
            text_length,
            reserved2,
            text,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            self.header.header_size,
            self.source,
            self.reserved1,
            self.text_length,
            self.reserved2,
        )
        encoded_text = self.text.encode("mbcs") + b"\x00"
        text_offset = self.header.header_size + self._FORMAT.size
        buffer[text_offset : text_offset + self.text_length] = encoded_text
        return bytes(buffer)
