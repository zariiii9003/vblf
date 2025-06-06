import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from vblf.general import ObjectHeader, ObjectWithHeader


@dataclass
class LinMessage(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBB8sBBBBHB5s")
    header: ObjectHeader
    channel: int
    id: int
    dlc: int
    data: bytes
    fsm_id: int
    fsm_state: int
    header_time: int
    full_time: int
    crc: int
    dir: int
    reserved: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            lin_id,
            dlc,
            data_,
            fsm_id,
            fsm_state,
            header_time,
            full_time,
            crc,
            direction,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)
        return cls(
            header,
            channel,
            lin_id,
            dlc,
            data_,
            fsm_id,
            fsm_state,
            header_time,
            full_time,
            crc,
            direction,
            reserved,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.id,
            self.dlc,
            self.data,
            self.fsm_id,
            self.fsm_state,
            self.header_time,
            self.full_time,
            self.crc,
            self.dir,
            self.reserved,
        )


@dataclass
class LinBusEvent:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("QIH2s")
    SIZE: ClassVar[int] = _FORMAT.size
    sof: int
    event_baudrate: int
    channel: int
    reserved: bytes

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        (
            sof,
            event_baudrate,
            channel,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, offset)
        return cls(
            sof,
            event_baudrate,
            channel,
            reserved,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self._FORMAT.pack_into(
            buffer, offset, self.sof, self.event_baudrate, self.channel, self.reserved
        )


@dataclass
class LinSynchFieldEvent:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("QQ")
    SIZE: ClassVar[int] = LinBusEvent.SIZE + _FORMAT.size
    lin_bus_event: LinBusEvent
    synch_break_length: int
    synch_del_length: int

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        lin_bus_event = LinBusEvent.unpack_from(buffer, offset)
        (
            synch_break_length,
            synch_del_length,
        ) = cls._FORMAT.unpack_from(buffer, offset + LinBusEvent.SIZE)
        return cls(
            lin_bus_event,
            synch_break_length,
            synch_del_length,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self.lin_bus_event.pack_into(buffer, offset)
        self._FORMAT.pack_into(
            buffer, offset + LinBusEvent.SIZE, self.synch_break_length, self.synch_del_length
        )


@dataclass
class LinMessageDescriptor:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHBBBB")
    SIZE: ClassVar[int] = LinSynchFieldEvent.SIZE + _FORMAT.size
    lin_synch_field_event: LinSynchFieldEvent
    supplier_id: int
    message_id: int
    nad: int
    id: int
    dlc: int
    checksum_model: int

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        lin_synch_field_event = LinSynchFieldEvent.unpack_from(buffer, offset)
        (
            supplier_id,
            message_id,
            nad,
            lin_id,
            dlc,
            checksum_model,
        ) = cls._FORMAT.unpack_from(buffer, offset + LinSynchFieldEvent.SIZE)
        return cls(
            lin_synch_field_event,
            supplier_id,
            message_id,
            nad,
            lin_id,
            dlc,
            checksum_model,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self.lin_synch_field_event.pack_into(buffer, offset)
        self._FORMAT.pack_into(
            buffer,
            offset + LinSynchFieldEvent.SIZE,
            self.supplier_id,
            self.message_id,
            self.nad,
            self.id,
            self.dlc,
            self.checksum_model,
        )


@dataclass
class LinDatabyteTimestampEvent:
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("9Q")
    SIZE: ClassVar[int] = LinMessageDescriptor.SIZE + _FORMAT.size
    lin_msg_descr_event: LinMessageDescriptor
    databyte_timestamps: tuple[int]

    @classmethod
    def unpack_from(cls, buffer: bytes, offset: int = 0) -> Self:
        lin_msg_descr_event = LinMessageDescriptor.unpack_from(buffer, offset)
        databyte_timestamps = cls._FORMAT.unpack_from(buffer, offset + LinMessageDescriptor.SIZE)
        return cls(
            lin_msg_descr_event,
            databyte_timestamps,
        )

    def pack_into(self, buffer: bytearray, offset: int) -> None:
        self.lin_msg_descr_event.pack_into(buffer, offset)
        self._FORMAT.pack_into(
            buffer, offset + LinMessageDescriptor.SIZE, *self.databyte_timestamps
        )


@dataclass
class LinMessage2(ObjectWithHeader[ObjectHeader]):
    _FORMAT_V1: ClassVar[struct.Struct] = struct.Struct("8sHBBBBBBB3s")
    _FORMAT_V2: ClassVar[struct.Struct] = struct.Struct("I")
    _FORMAT_V3: ClassVar[struct.Struct] = struct.Struct("dII")
    _V1_SIZE: ClassVar[int] = ObjectHeader.SIZE + LinDatabyteTimestampEvent.SIZE + _FORMAT_V1.size
    _V2_SIZE: ClassVar[int] = _V1_SIZE + _FORMAT_V2.size
    _V3_SIZE: ClassVar[int] = _V2_SIZE + _FORMAT_V3.size

    header: ObjectHeader
    # V1
    lin_timestamp_event: LinDatabyteTimestampEvent
    data: bytes
    crc: int
    direction: int
    simulated: int
    is_etf: int
    etf_assoc_index: int
    etf_assoc_etf_id: int
    fsm_id: int
    fsm_state: int
    reserved: bytes
    # V2
    resp_baudrate: int
    # V3
    exact_header_baudrate: float
    early_stopbit_offset: int
    early_stopbit_offset_response: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        lin_timestamp_event = LinDatabyteTimestampEvent.unpack_from(buffer, ObjectHeader.SIZE)
        (
            data_,
            crc,
            direction,
            simulated,
            is_etf,
            etf_assoc_index,
            etf_assoc_etf_id,
            fsm_id,
            fsm_state,
            reserved,
        ) = cls._FORMAT_V1.unpack_from(buffer, ObjectHeader.SIZE + LinDatabyteTimestampEvent.SIZE)

        if header.base.object_size >= cls._V2_SIZE:
            (resp_baudrate,) = cls._FORMAT_V2.unpack_from(buffer, cls._V1_SIZE)
        else:
            resp_baudrate = 0

        if header.base.object_size >= cls._V3_SIZE:
            (
                exact_header_baudrate,
                early_stopbit_offset,
                early_stopbit_offset_response,
            ) = cls._FORMAT_V3.unpack_from(buffer, cls._V2_SIZE)
        else:
            exact_header_baudrate = 0
            early_stopbit_offset = 0
            early_stopbit_offset_response = 0

        return cls(
            header,
            lin_timestamp_event,
            data_,
            crc,
            direction,
            simulated,
            is_etf,
            etf_assoc_index,
            etf_assoc_etf_id,
            fsm_id,
            fsm_state,
            reserved,
            resp_baudrate,
            exact_header_baudrate,
            early_stopbit_offset,
            early_stopbit_offset_response,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self.lin_timestamp_event.pack_into(buffer, ObjectHeader.SIZE)
        self._FORMAT_V1.pack_into(
            buffer,
            ObjectHeader.SIZE + LinDatabyteTimestampEvent.SIZE,
            self.data,
            self.crc,
            self.direction,
            self.simulated,
            self.is_etf,
            self.etf_assoc_index,
            self.etf_assoc_etf_id,
            self.fsm_id,
            self.fsm_state,
            self.reserved,
        )
        if self.header.base.object_size >= self._V2_SIZE:
            self._FORMAT_V2.pack_into(buffer, self._V1_SIZE, self.resp_baudrate)
        if self.header.base.object_size >= self._V3_SIZE:
            self._FORMAT_V3.pack_into(
                buffer,
                self._V2_SIZE,
                self.exact_header_baudrate,
                self.early_stopbit_offset,
                self.early_stopbit_offset_response,
            )
        return bytes(buffer)
