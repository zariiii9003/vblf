import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from blf.constants import AppId, ObjFlags, ObjTypeEnum, TriggerFlag


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
    SIZE: ClassVar[int] = _FORMAT.size
    signature: bytes
    header_size: int
    header_version: int
    object_size: int
    object_type: ObjTypeEnum

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        (
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
        ) = cls._FORMAT.unpack(buffer)
        return cls(
            signature,
            header_size,
            header_version,
            object_size,
            ObjTypeEnum.from_int(object_type),
        )

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        (
            signature,
            header_size,
            header_version,
            object_size,
            object_type,
        ) = cls._FORMAT.unpack_from(buffer, offset)
        return cls(
            signature,
            header_size,
            header_version,
            object_size,
            ObjTypeEnum.from_int(object_type),
        )

    def pack(self) -> bytes:
        return self._FORMAT.pack(*self.__dict__.values())

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self._FORMAT.pack_into(buffer, offset, *self.__dict__.values())


@dataclass
class HeaderWithBase:
    base: ObjectHeaderBase

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        raise NotImplementedError

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        raise NotImplementedError

    def pack(self) -> bytes:
        raise NotImplementedError

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        raise NotImplementedError


@dataclass
class VarObjectHeader(HeaderWithBase):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IHHQ")
    object_flags: int
    object_static_size: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        base = ObjectHeaderBase.unpack_from(buffer, 0)
        (
            object_flags,
            object_static_size,
            object_version,
            object_time_stamp,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeaderBase.SIZE)
        return cls(
            base,
            ObjFlags(object_flags),
            object_static_size,
            object_version,
            object_time_stamp,
        )

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        base = ObjectHeaderBase.unpack_from(buffer, 0)
        (
            object_flags,
            object_static_size,
            object_version,
            object_time_stamp,
        ) = cls._FORMAT.unpack_from(buffer, offset + ObjectHeaderBase.SIZE)
        return cls(
            base,
            ObjFlags(object_flags),
            object_static_size,
            object_version,
            object_time_stamp,
        )

    def pack(self) -> bytes:
        return self.base.pack() + self._FORMAT.pack(
            self.object_flags,
            self.object_static_size,
            self.object_version,
            self.object_time_stamp,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self.base.pack_into(buffer, offset)
        self._FORMAT.pack_into(
            buffer,
            offset + ObjectHeaderBase.SIZE,
            self.object_flags,
            self.object_static_size,
            self.object_version,
            self.object_time_stamp,
        )


@dataclass
class ObjectHeader(HeaderWithBase):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IHHQ")
    object_flags: int
    client_index: int
    object_version: int
    object_time_stamp: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        base = ObjectHeaderBase.unpack_from(buffer, 0)
        (
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeaderBase.SIZE)
        return cls(
            base,
            ObjFlags(object_flags),
            client_index,
            object_version,
            object_time_stamp,
        )

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        base = ObjectHeaderBase.unpack_from(buffer, offset)
        (
            object_flags,
            client_index,
            object_version,
            object_time_stamp,
        ) = cls._FORMAT.unpack_from(buffer, offset + ObjectHeaderBase.SIZE)
        return cls(
            base,
            ObjFlags(object_flags),
            client_index,
            object_version,
            object_time_stamp,
        )

    def pack(self) -> bytes:
        return self.base.pack() + self._FORMAT.pack(
            self.object_flags,
            self.client_index,
            self.object_version,
            self.object_time_stamp,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self.base.pack_into(buffer, offset)
        self._FORMAT.pack_into(
            buffer,
            offset + ObjectHeaderBase.SIZE,
            self.object_flags,
            self.client_index,
            self.object_version,
            self.object_time_stamp,
        )


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
    header: HeaderWithBase

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        raise NotImplementedError

    def pack(self) -> bytes:
        raise NotImplementedError


@dataclass
class FileStatistics:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("4sIIBBBBQQII32xQ64s")
    SIZE: ClassVar[int] = _FORMAT.size
    signature: bytes
    statistics_size: int
    api_number: int
    application_id: AppId
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
            AppId.from_int(application_id),
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
        return cls(header, buffer[header.base.header_size :])

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
        ) = cls._FORMAT.unpack_from(buffer, header.base.header_size)
        text_offset = header.base.header_size + cls._FORMAT.size
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
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            self.header.base.header_size,
            self.source,
            self.reserved1,
            self.text_length,
            self.reserved2,
        )
        encoded_text = self.text.encode("mbcs") + b"\x00"
        text_offset = self.header.base.header_size + self._FORMAT.size
        buffer[text_offset : text_offset + self.text_length] = encoded_text
        return bytes(buffer)


@dataclass
class AppTrigger(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("QQHHI")
    header: ObjectHeader
    pre_trigger_time: int
    post_trigger_time: int
    channel: int
    flags: TriggerFlag
    app_specific: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            pre_trigger_time,
            post_trigger_time,
            channel,
            flags,
            app_specific,
        ) = cls._FORMAT.unpack_from(buffer, header.base.header_size)
        return cls(
            header,
            pre_trigger_time,
            post_trigger_time,
            channel,
            TriggerFlag(flags),
            app_specific,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.pre_trigger_time,
            self.post_trigger_time,
            self.channel,
            self.flags,
            self.app_specific,
        )


@dataclass
class EnvironmentVariable(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIQ")
    header: ObjectHeader
    name_length: int
    data_length: int
    reserved: int
    name: str
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (name_length, data_length, reserved) = cls._FORMAT.unpack_from(
            buffer, header.base.header_size
        )

        # get name
        name_offset = header.base.header_size + cls._FORMAT.size
        name = buffer[name_offset : name_offset + name_length].decode("mbcs")

        # get data
        data_offset = name_offset + name_length
        data = buffer[data_offset : data_offset + data_length]

        return cls(
            header,
            name_length,
            data_length,
            reserved,
            name,
            data,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)

        # write header
        self.header.pack_into(buffer, 0)

        # write fixed size values
        self._FORMAT.pack_into(
            buffer,
            self.header.base.header_size,
            self.name_length,
            self.data_length,
            self.reserved,
        )

        # write name
        name_offset = self.header.base.header_size + self._FORMAT.size
        buffer[name_offset : name_offset + self.name_length] = self.name.encode("mbcs")

        # write data
        data_offset = name_offset + self.name_length
        buffer[data_offset : data_offset + self.data_length] = self.data

        return bytes(buffer)
