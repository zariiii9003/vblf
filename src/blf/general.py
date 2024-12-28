import struct
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class SystemTime:
    FORMAT: ClassVar[struct.Struct] = struct.Struct("HHHHHHHH")
    year: int
    month: int
    day_of_week: int
    day: int
    hour: int
    minute: int
    second: int
    milliseconds: int

    @classmethod
    def unpack(cls, data: bytes) -> "SystemTime":
        return cls(*cls.FORMAT.unpack(data))

    def pack(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class ObjectHeaderBase:
    FORMAT: ClassVar[struct.Struct] = struct.Struct("4sHHII")
    signature: bytes
    header_size: int
    header_version: int
    object_size: int
    object_type: int

    @classmethod
    def unpack(cls, data: bytes) -> "ObjectHeaderBase":
        return cls(*cls.FORMAT.unpack(data))

    def pack(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class VarObjectHeader(ObjectHeaderBase):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase.FORMAT.format + "IHHQ")
    object_flags: int
    object_static_size: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def unpack(cls, data: bytes) -> "VarObjectHeader":
        return cls(*cls.FORMAT.unpack(data))

    def pack(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class ObjectHeader(ObjectHeaderBase):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase.FORMAT.format + "IHHQ")
    object_flags: int
    client_index: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def unpack(cls, data: bytes) -> "ObjectHeader":
        return cls(*cls.FORMAT.unpack(data))

    def pack(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


# @dataclass
# class ObjectHeader2(ObjectHeaderBase):
#     FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase.FORMAT.format + "IBBHQQ")
#     object_flags: int
#     time_stamp_status: int
#     reserved1: int
#     object_version: int
#     object_time_stamp: int
#     original_time_stamp: int

#     @classmethod
#     def unpack(cls, data: bytes) -> "ObjectHeader2":
#         return cls(*cls.FORMAT.unpack(data))

#     def pack(self) -> bytes:
#         return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class FileStatistics:
    FORMAT: ClassVar[struct.Struct] = struct.Struct(
        "4sIIBBBBQQII" + SystemTime.FORMAT.format + SystemTime.FORMAT.format + "Q64s"
    )
    signature: bytes  # offset: 0x00
    statistics_size: int  # offset: 0x04
    api_number: int  # offset: 0x08
    application_id: int  # offset: 0x0C
    compression_level: int  # offset: 0x0D
    application_major: int  # offset: 0x0E
    application_minor: int  # offset: 0x0F
    file_size: int  # offset: 0x10
    uncompressed_file_size: int  # offset: 0x18
    object_count: int  # offset: 0x20
    application_build: int  # offset: 0x24
    measurement_start_time: SystemTime  # offset: 0x28
    last_object_time: SystemTime  # offset: 0x38
    restore_points_offset: int  # offset: 0x48
    reserved: bytes

    @classmethod
    def unpack(cls, data: bytes) -> "FileStatistics":
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
            measurement_start_time_year,
            measurement_start_time_month,
            measurement_start_time_day_of_week,
            measurement_start_time_day,
            measurement_start_time_hour,
            measurement_start_time_minute,
            measurement_start_time_second,
            measurement_start_time_milliseconds,
            last_object_time_year,
            last_object_time_month,
            last_object_time_day_of_week,
            last_object_time_day,
            last_object_time_hour,
            last_object_time_minute,
            last_object_time_second,
            last_object_time_milliseconds,
            restore_points_offset,
            reserved,
        ) = cls.FORMAT.unpack(data)
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
            SystemTime(
                measurement_start_time_year,
                measurement_start_time_month,
                measurement_start_time_day_of_week,
                measurement_start_time_day,
                measurement_start_time_hour,
                measurement_start_time_minute,
                measurement_start_time_second,
                measurement_start_time_milliseconds,
            ),
            SystemTime(
                last_object_time_year,
                last_object_time_month,
                last_object_time_day_of_week,
                last_object_time_day,
                last_object_time_hour,
                last_object_time_minute,
                last_object_time_second,
                last_object_time_milliseconds,
            ),
            restore_points_offset,
            reserved,
        )

    def pack(self) -> bytes:
        return self.FORMAT.pack(
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
            *self.measurement_start_time.__dict__.values(),
            *self.last_object_time.__dict__.values(),
            self.restore_points_offset,
            self.reserved,
        )


@dataclass
class LogContainer(ObjectHeader):
    data: bytes

    @classmethod
    def unpack(cls, data: bytes) -> "LogContainer":
        (
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
        ) = cls.FORMAT.unpack_from(data)
        return cls(
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
            data[header_size:],
        )

    def pack(self) -> bytes:
        return super().pack() + self.data


@dataclass
class AppText(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "IIII")
    source: int
    reserved1: int
    text_length: int
    reserved2: int
    text: str

    @classmethod
    def unpack(cls, data: bytes) -> "AppText":
        (
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
            source,
            reserved1,
            text_length,
            reserved2,
        ) = cls.FORMAT.unpack_from(data)
        text = data[cls.FORMAT.size : cls.FORMAT.size + text_length - 1].decode("mbcs")
        return cls(
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
            source,
            reserved1,
            text_length,
            reserved2,
            text,
        )

    def pack(self) -> bytes:
        raw = bytearray(self.object_size)
        self.FORMAT.pack_into(
            raw,
            0,
            self.signature,
            self.header_size,
            self.header_version,
            self.object_size,
            self.object_type,
            self.object_flags,
            self.client_index,
            self.object_version,
            self.object_time_stamp,
            self.source,
            self.reserved1,
            self.text_length,
            self.reserved2,
        )
        encoded_text = self.text.encode("mbcs") + b"\x00"
        raw[self.FORMAT.size : self.FORMAT.size + self.text_length] = encoded_text
        return bytes(raw)
