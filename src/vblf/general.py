import datetime
import struct
from dataclasses import dataclass
from typing import ClassVar, Generic, Optional, TypeVar, Union

from typing_extensions import Self

from vblf import __version__
from vblf.constants import (
    FILE_SIGNATURE,
    OBJ_SIGNATURE,
    AppId,
    AppTextSource,
    BusType,
    Compression,
    FunctionBusType,
    ObjFlags,
    ObjType,
    SysVarType,
    TriggerConditionStatus,
    TriggerFlag,
)

HeaderType = TypeVar("HeaderType", bound="HeaderWithBase")


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

    @classmethod
    def from_datetime(cls, dt: Optional[datetime.datetime] = None) -> Self:
        if not dt:
            dt = datetime.datetime.now(tz=datetime.timezone.utc)
        return cls(
            dt.year,
            dt.month,
            (dt.weekday() + 1) % 7,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            min(999, round(dt.microsecond / 1000.0)),
        )


@dataclass
class ObjectHeaderBase:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("4sHHII")
    SIZE: ClassVar[int] = _FORMAT.size
    signature: bytes
    header_size: int
    header_version: int
    object_size: int
    object_type: ObjType

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
            ObjType.from_int(object_type),
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
            ObjType.from_int(object_type),
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
    SIZE: ClassVar[int] = ObjectHeaderBase.SIZE + _FORMAT.size
    object_flags: ObjFlags
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
    SIZE: ClassVar[int] = ObjectHeaderBase.SIZE + _FORMAT.size
    object_flags: ObjFlags
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

    @classmethod
    def new(
        cls,
        object_size: int,
        object_type: ObjType,
        object_flags: ObjFlags,
        object_version: int,
        object_time_stamp: int,
    ) -> Self:
        base = ObjectHeaderBase(
            signature=OBJ_SIGNATURE,
            header_size=cls.SIZE,
            header_version=1,
            object_size=object_size,
            object_type=object_type,
        )
        header = cls(
            base,
            object_flags,
            0,
            object_version,
            object_time_stamp,
        )
        return header


# @dataclass
# class ObjectHeader2(ObjectHeaderBase):
#     _FORMAT: ClassVar[struct.Struct] = struct.Struct("IBBHQQ")
#     SIZE: ClassVar[int] = ObjectHeaderBase.SIZE + _FORMAT.size
#     object_flags: int
#     time_stamp_status: int
#     reserved1: int
#     object_version: int
#     object_time_stamp: int
#     original_time_stamp: int


@dataclass
class ObjectWithHeader(Generic[HeaderType]):
    header: HeaderType

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        raise NotImplementedError

    def pack(self) -> bytes:
        raise NotImplementedError


@dataclass
class NotImplementedObject(ObjectWithHeader[HeaderWithBase]):
    header: HeaderWithBase
    buffer: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        base = ObjectHeaderBase.unpack_from(buffer, 0)
        header = HeaderWithBase(base)
        return cls(header, buffer)

    def pack(self) -> bytes:
        return self.buffer


@dataclass
class FileStatistics:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("4sIIBBBBQQII32xQ64s")
    SIZE: ClassVar[int] = _FORMAT.size
    signature: bytes
    statistics_size: int
    api_number: int
    application_id: AppId
    compression_level: Union[int, Compression]
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
            Compression.from_int(compression_level),
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
    def new(cls) -> Self:
        major_version, minor_version, *_ = __version__.split(".")
        return cls(
            signature=FILE_SIGNATURE,
            statistics_size=FileStatistics.SIZE,
            api_number=0x3E4630,
            application_id=AppId.UNKNOWN,
            compression_level=Compression.DEFAULT,
            application_major=int(major_version),
            application_minor=int(minor_version),
            file_size=FileStatistics.SIZE,
            uncompressed_file_size=FileStatistics.SIZE,
            object_count=0,
            application_build=0,
            measurement_start_time=SystemTime.from_datetime(),
            last_object_time=SystemTime.from_datetime(),
            restore_points_offset=0,
            reserved=bytes(64),
        )


@dataclass
class LogContainer(ObjectWithHeader[ObjectHeader]):
    header: ObjectHeader
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        return cls(header, buffer[ObjectHeader.SIZE :])

    def pack(self) -> bytes:
        return self.header.pack() + self.data

    @classmethod
    def new(
        cls,
        data: bytes,
        time_stamp: int,
        flags: ObjFlags = ObjFlags.TIME_ONE_NANS,
        client_index: int = 0,
    ) -> Self:
        base = ObjectHeaderBase(
            signature=OBJ_SIGNATURE,
            header_size=ObjectHeader.SIZE,
            header_version=1,
            object_size=ObjectHeader.SIZE + len(data),
            object_type=ObjType.LOG_CONTAINER,
        )
        header = ObjectHeader(
            base=base,
            object_flags=flags,
            client_index=client_index,
            object_version=0,
            object_time_stamp=time_stamp,
        )
        return cls(
            header=header,
            data=data,
        )


@dataclass
class AppText(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIII")
    header: ObjectHeader
    source: AppTextSource
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
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
        text_offset = ObjectHeader.SIZE + cls._FORMAT.size
        text = buffer[text_offset : text_offset + text_length - 1].decode("cp1252")
        return cls(
            header,
            AppTextSource(source),
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
            ObjectHeader.SIZE,
            self.source,
            self.reserved1,
            self.text_length,
            self.reserved2,
        )
        encoded_text = self.text.encode("cp1252") + b"\x00"
        text_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[text_offset : text_offset + self.text_length] = encoded_text
        return bytes(buffer)


@dataclass
class AppTrigger(ObjectWithHeader[ObjectHeader]):
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
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
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
class EnvironmentVariable(ObjectWithHeader[ObjectHeader]):
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
        (name_length, data_length, reserved) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        # get name
        name_offset = ObjectHeader.SIZE + cls._FORMAT.size
        name = buffer[name_offset : name_offset + name_length].decode("cp1252")

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
            ObjectHeader.SIZE,
            self.name_length,
            self.data_length,
            self.reserved,
        )

        # write name
        name_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[name_offset : name_offset + self.name_length] = self.name.encode("cp1252")

        # write data
        data_offset = name_offset + self.name_length
        buffer[data_offset : data_offset + self.data_length] = self.data

        return bytes(buffer)


@dataclass
class SystemVariable(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIQIIQ")
    header: ObjectHeader
    type: SysVarType
    representation: int
    reserved1: int
    name_length: int
    data_length: int
    reserved2: int
    name: str
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            type_,
            representation,
            reserved1,
            name_length,
            data_length,
            reserved2,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        # get name
        name_offset = ObjectHeader.SIZE + cls._FORMAT.size
        name = buffer[name_offset : name_offset + name_length].decode("cp1252")

        # get data
        data_offset = name_offset + name_length
        data = buffer[data_offset : data_offset + data_length]

        return cls(
            header,
            SysVarType(type_),
            representation,
            reserved1,
            name_length,
            data_length,
            reserved2,
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
            ObjectHeader.SIZE,
            self.type,
            self.representation,
            self.reserved1,
            self.name_length,
            self.data_length,
            self.reserved2,
        )

        # write name
        name_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[name_offset : name_offset + self.name_length] = self.name.encode("cp1252")

        # write data
        data_offset = name_offset + self.name_length
        buffer[data_offset : data_offset + self.data_length] = self.data

        return bytes(buffer)


@dataclass
class RealTimeClock(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("QQ")
    header: ObjectHeader
    time: int
    logging_offset: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        time, logging_offset = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
        return cls(header, time, logging_offset)

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(self.time, self.logging_offset)


@dataclass
class DriverOverrun(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IHH")
    header: ObjectHeader
    bus_type: BusType
    channel: int
    reserved: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            bus_type,
            channel,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
        return cls(
            header,
            BusType(bus_type),
            channel,
            reserved,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.bus_type,
            self.channel,
            self.reserved,
        )


@dataclass
class EventComment(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIQ")
    header: ObjectHeader
    commented_event_type: int
    text_length: int
    reserved: int
    text: str

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            commented_event_type,
            text_length,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
        text_offset = ObjectHeader.SIZE + cls._FORMAT.size
        text = buffer[text_offset : text_offset + text_length].decode("cp1252")
        return cls(
            header,
            commented_event_type,
            text_length,
            reserved,
            text,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            ObjectHeader.SIZE,
            self.commented_event_type,
            self.text_length,
            self.reserved,
        )
        encoded_text = self.text.encode("cp1252")
        text_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[text_offset : text_offset + self.text_length] = encoded_text
        return bytes(buffer)


@dataclass
class GlobalMarker(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIIBBHIIIIQ")
    header: ObjectHeader
    commented_event_type: int
    foreground_color: int
    background_color: int
    is_relocatable: int
    reserved1: int
    reserved2: int
    group_name_length: int
    marker_name_length: int
    description_length: int
    reserved3: int
    reserved4: int
    group_name: str
    marker_name: str
    description: str

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            commented_event_type,
            foreground_color,
            background_color,
            is_relocatable,
            reserved1,
            reserved2,
            group_name_length,
            marker_name_length,
            description_length,
            reserved3,
            reserved4,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        # get group_name
        group_name_offset = ObjectHeader.SIZE + cls._FORMAT.size
        _group_name = buffer[group_name_offset : group_name_offset + group_name_length]
        group_name = _group_name.decode("cp1252")

        # get marker_name
        marker_name_offset = group_name_offset + group_name_length
        _marker_name = buffer[marker_name_offset : marker_name_offset + marker_name_length]
        marker_name = _marker_name.decode("cp1252")

        # get marker_name
        description_offset = marker_name_offset + marker_name_length
        _description = buffer[description_offset : description_offset + description_length]
        description = _description.decode("cp1252")

        return cls(
            header,
            commented_event_type,
            foreground_color,
            background_color,
            is_relocatable,
            reserved1,
            reserved2,
            group_name_length,
            marker_name_length,
            description_length,
            reserved3,
            reserved4,
            group_name,
            marker_name,
            description,
        )

    def pack(self) -> bytes:
        return (
            self.header.pack()
            + self._FORMAT.pack(
                self.commented_event_type,
                self.foreground_color,
                self.background_color,
                self.is_relocatable,
                self.reserved1,
                self.reserved2,
                self.group_name_length,
                self.marker_name_length,
                self.description_length,
                self.reserved3,
                self.reserved4,
            )
            + self.group_name.encode("cp1252")
            + self.marker_name.encode("cp1252")
            + self.description.encode("cp1252")
        )


@dataclass
class FunctionBus(ObjectWithHeader[VarObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIII")
    header: VarObjectHeader
    object_type: FunctionBusType
    ve_type: int
    name_length: int
    data_length: int
    name: str
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = VarObjectHeader.unpack_from(buffer, 0)
        (
            object_type,
            ve_type,
            name_length,
            data_length,
        ) = cls._FORMAT.unpack_from(buffer, VarObjectHeader.SIZE)

        # get name
        name_offset = ObjectHeader.SIZE + cls._FORMAT.size
        _name = buffer[name_offset : name_offset + name_length]
        name = _name.decode("cp1252")

        # get data
        data_offset = name_offset + name_length
        data = buffer[data_offset : data_offset + data_length]

        return cls(
            header,
            FunctionBusType(object_type),
            ve_type,
            name_length,
            data_length,
            name,
            data,
        )

    def pack(self) -> bytes:
        return (
            self.header.pack()
            + self._FORMAT.pack(
                self.object_type,
                self.ve_type,
                self.name_length,
                self.data_length,
            )
            + self.name.encode("cp1252")
            + self.data
        )


@dataclass
class TriggerCondition(ObjectWithHeader[VarObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("III")
    header: VarObjectHeader
    state: TriggerConditionStatus
    trigger_block_name_length: int
    trigger_condition_length: int
    trigger_block_name: str
    trigger_condition: str

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = VarObjectHeader.unpack_from(buffer, 0)
        (
            state,
            trigger_block_name_length,
            trigger_condition_length,
        ) = cls._FORMAT.unpack_from(buffer, VarObjectHeader.SIZE)

        # get trigger_block_name
        trigger_block_name_offset = ObjectHeader.SIZE + cls._FORMAT.size
        _trigger_block_name = buffer[
            trigger_block_name_offset : trigger_block_name_offset + trigger_block_name_length
        ]
        trigger_block_name = _trigger_block_name.decode("cp1252")

        # get trigger_condition
        trigger_condition_offset = trigger_block_name_offset + trigger_block_name_length
        _trigger_condition = buffer[
            trigger_condition_offset : trigger_condition_offset + trigger_condition_length
        ]
        trigger_condition = _trigger_condition.decode("cp1252")

        return cls(
            header,
            TriggerConditionStatus(state),
            trigger_block_name_length,
            trigger_condition_length,
            trigger_block_name,
            trigger_condition,
        )

    def pack(self) -> bytes:
        return (
            self.header.pack()
            + self._FORMAT.pack(
                self.state,
                self.trigger_block_name_length,
                self.trigger_condition_length,
            )
            + self.trigger_block_name.encode("cp1252")
            + self.trigger_condition.encode("cp1252")
        )
