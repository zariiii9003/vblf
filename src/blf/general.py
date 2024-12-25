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
    def deserialize(cls, data: bytes) -> "SystemTime":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
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
    def deserialize(cls, data: bytes) -> "ObjectHeaderBase":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class VarObjectHeader(ObjectHeaderBase):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase.FORMAT.format + "IHHQ")
    object_flags: int
    object_static_size: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def deserialize(cls, data: bytes) -> "VarObjectHeader":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class ObjectHeader(ObjectHeaderBase):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeaderBase.FORMAT.format + "IHHQ")
    object_flags: int
    client_index: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def deserialize(cls, data: bytes) -> "ObjectHeader":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
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
#     def deserialize(cls, data: bytes) -> "ObjectHeader2":
#         return cls(*cls.FORMAT.unpack(data))

#     def serialize(self) -> bytes:
#         return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class FileStatisticsEx:
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

    @classmethod
    def deserialize(cls, data: bytes) -> "FileStatisticsEx":
        values = cls.FORMAT.unpack(data)
        return cls(*values[:11], SystemTime(*values[11:19]), SystemTime(*values[19:27]), values[27])

    def serialize(self) -> bytes:
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
            bytes(64),
        )


@dataclass
class LogContainer(ObjectHeader):
    data: bytes

    @classmethod
    def deserialize(cls, data: bytes) -> "LogContainer":
        header_values = cls.FORMAT.unpack(data[: cls.FORMAT.size])
        data = data[cls.FORMAT.size :]
        return cls(*header_values, data)

    def serialize(self) -> bytes:
        header_values = list(self.__dict__.values())[:-1]
        print(header_values)
        return self.FORMAT.pack(*header_values) + self.data


@dataclass
class AppText(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "IIII")
    source: int
    reserved1: int
    text_length: int
    reserved2: int
    text: str

    @classmethod
    def deserialize(cls, data: bytes) -> "AppText":
        fixed_size_values = cls.FORMAT.unpack(data[: cls.FORMAT.size])
        text_length = fixed_size_values[11]
        text = data[cls.FORMAT.size : cls.FORMAT.size + text_length - 1].decode("mbcs")
        return cls(*fixed_size_values, text)

    def serialize(self) -> bytes:
        raw = bytearray(self.object_size)
        fixed_size_values = list(self.__dict__.values())[:13]
        raw[: self.FORMAT.size] = self.FORMAT.pack(*fixed_size_values)
        raw[self.FORMAT.size : self.FORMAT.size + self.text_length] = (
            self.text.encode("mbcs") + b"\x00"
        )
        return bytes(raw)
