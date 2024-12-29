import struct
from dataclasses import dataclass
from enum import IntFlag
from typing import ClassVar

from typing_extensions import Self

from .general import ObjectHeader, ObjectWithHeader


@dataclass
class CanMessage(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBBI8s")
    header: ObjectHeader
    channel: int
    flags: int
    dlc: int
    frame_id: int
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            flags,
            dlc,
            frame_id,
            data_,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            flags,
            dlc,
            frame_id,
            data_,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.flags,
            self.dlc,
            self.frame_id,
            self.data,
        )


@dataclass
class CanMessage2(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBBI8sIBBH")
    header: ObjectHeader
    channel: int
    flags: int
    dlc: int
    frame_id: int
    data: bytes
    frame_length: int
    bit_count: int
    reserved1: int
    reserved2: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            flags,
            dlc,
            frame_id,
            data_,
            frame_length,
            bit_count,
            reserved1,
            reserved2,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            flags,
            dlc,
            frame_id,
            data_,
            frame_length,
            bit_count,
            reserved1,
            reserved2,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.flags,
            self.dlc,
            self.frame_id,
            self.data,
            self.frame_length,
            self.bit_count,
            self.reserved1,
            self.reserved2,
        )


class CanFdMessage64Flags(IntFlag):
    NERR = 0x0004
    HIGH_VOLTAGE_WAKE_UP = 0x0008
    REMOTE_FRAME = 0x0010
    TX_ACKNOWLEDGE = 0x0040
    TX_REQUEST = 0x0080
    SRR = 0x0200
    R0 = 0x0400
    R1 = 0x0800
    FDF = 0x1000
    BRS = 0x2000
    ESI = 0x4000
    FRAME_PART_OF_BURST = 0x20000
    SINGLE_SHOT_MODE_NOT_TRANSMITTED = 0x40000
    SINGLE_SHOT_MODE_REASON = 0x80000  # 0 = arbitration lost, 1 = frame disturbed


@dataclass
class CanFdMessage(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBBIIBBBBI64sI")
    header: ObjectHeader
    channel: int
    flags: int
    dlc: int
    frame_id: int
    frame_length: int
    arb_bit_count: int
    canfd_flags: int
    valid_data_bytes: int
    reserved1: int
    reserved2: int
    data: bytes
    reserved3: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            flags,
            dlc,
            frame_id,
            frame_length,
            arb_bit_count,
            canfd_flags,
            valid_data_bytes,
            reserved1,
            reserved2,
            data_,
            reserved3,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            flags,
            dlc,
            frame_id,
            frame_length,
            arb_bit_count,
            canfd_flags,
            valid_data_bytes,
            reserved1,
            reserved2,
            data_,
            reserved3,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.flags,
            self.dlc,
            self.frame_id,
            self.frame_length,
            self.arb_bit_count,
            self.canfd_flags,
            self.valid_data_bytes,
            self.reserved1,
            self.reserved2,
            self.data,
            self.reserved3,
        )


@dataclass
class CanFdMessage64(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("BBBBIIIIIIIHBBI")
    _FORMAT_EXT: ClassVar[struct.Struct] = struct.Struct("II")
    header: ObjectHeader
    channel: int
    dlc: int
    valid_data_bytes: int
    tx_count: int
    frame_id: int
    frame_length: int
    flags: CanFdMessage64Flags
    btr_cfg_arb: int
    btr_cfg_data: int
    time_offset_brs_ns: int
    time_offset_crc_del_ns: int
    bit_count: int
    dir: int
    ext_data_offset: int
    crc: int
    data: bytes
    btr_ext_arb: int
    btr_ext_data: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        # get fixed size values
        (
            channel,
            dlc,
            valid_data_bytes,
            tx_count,
            frame_id,
            frame_length,
            flags,
            btr_cfg_arb,
            btr_cfg_data,
            time_offset_brs_ns,
            time_offset_crc_del_ns,
            bit_count,
            dir,
            ext_data_offset,
            crc,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)

        # get data
        data_offset = header.header_size + cls._FORMAT.size
        data = buffer[data_offset : data_offset + valid_data_bytes]

        # get ext frame data
        btr_ext_arb, btr_ext_data = 0, 0
        if header.object_size >= ext_data_offset + cls._FORMAT_EXT.size:
            btr_ext_arb, btr_ext_data = cls._FORMAT_EXT.unpack_from(buffer, ext_data_offset)

        return cls(
            header,
            channel,
            dlc,
            valid_data_bytes,
            tx_count,
            frame_id,
            frame_length,
            CanFdMessage64Flags(flags),
            btr_cfg_arb,
            btr_cfg_data,
            time_offset_brs_ns,
            time_offset_crc_del_ns,
            bit_count,
            dir,
            ext_data_offset,
            crc,
            data,
            btr_ext_arb,
            btr_ext_data,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.object_size)

        # pack header
        self.header.pack_into(buffer, 0)

        # pack fixed size values
        self._FORMAT.pack_into(
            buffer,
            self.header.header_size,
            self.channel,
            self.dlc,
            self.valid_data_bytes,
            self.tx_count,
            self.frame_id,
            self.frame_length,
            self.flags,
            self.btr_cfg_arb,
            self.btr_cfg_data,
            self.time_offset_brs_ns,
            self.time_offset_crc_del_ns,
            self.bit_count,
            self.dir,
            self.ext_data_offset,
            self.crc,
        )

        # pack data
        data_offset = self.header.header_size + self._FORMAT.size
        buffer[data_offset : data_offset + self.valid_data_bytes] = self.data

        # pack ext frame data
        if self.header.object_size >= self.ext_data_offset + self._FORMAT_EXT.size:
            self._FORMAT_EXT.pack_into(
                buffer, self.ext_data_offset, self.btr_ext_arb, self.btr_ext_data
            )
        return bytes(buffer)


@dataclass
class CanDriverStatistic(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHIIIIIII")
    header: ObjectHeader
    channel: int
    bus_load: int
    standard_data_frames: int
    extended_data_frames: int
    standard_remote_frames: int
    extended_remote_frames: int
    error_frames: int
    overload_frames: int
    reserved: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            bus_load,
            standard_data_frames,
            extended_data_frames,
            standard_remote_frames,
            extended_remote_frames,
            error_frames,
            overload_frames,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            bus_load,
            standard_data_frames,
            extended_data_frames,
            standard_remote_frames,
            extended_remote_frames,
            error_frames,
            overload_frames,
            reserved,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.bus_load,
            self.standard_data_frames,
            self.extended_data_frames,
            self.standard_remote_frames,
            self.extended_remote_frames,
            self.error_frames,
            self.overload_frames,
            self.reserved,
        )


@dataclass
class CanDriverError(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBBI")
    header: ObjectHeader
    channel: int
    tx_errors: int
    rx_errors: int
    error_code: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            tx_errors,
            rx_errors,
            error_code,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            tx_errors,
            rx_errors,
            error_code,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.tx_errors,
            self.rx_errors,
            self.error_code,
        )


@dataclass
class CanDriverErrorExt(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBBIIBBH4I")
    header: ObjectHeader
    channel: int
    tx_errors: int
    rx_errors: int
    error_code: int
    flags: int
    state: int
    reserved1: int
    reserved2: int
    reserved3: list[int]

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            tx_errors,
            rx_errors,
            error_code,
            flags,
            state,
            reserved1,
            reserved2,
            reserved3_0,
            reserved3_1,
            reserved3_2,
            reserved3_3,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            tx_errors,
            rx_errors,
            error_code,
            flags,
            state,
            reserved1,
            reserved2,
            [reserved3_0, reserved3_1, reserved3_2, reserved3_3],
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.tx_errors,
            self.rx_errors,
            self.error_code,
            self.flags,
            self.state,
            self.reserved1,
            self.reserved2,
            self.reserved3[0],
            self.reserved3[1],
            self.reserved3[2],
            self.reserved3[3],
        )


@dataclass
class CanErrorFrame(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHI")
    header: ObjectHeader
    channel: int
    length: int
    reserved: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        channel, length, reserved = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(header, channel, length, reserved)

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(self.channel, self.length, self.reserved)


@dataclass
class CanErrorFrameExt(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHIBBBBIIHH8s")
    header: ObjectHeader
    channel: int
    length: int
    flags: int
    ecc: int
    position: int
    dlc: int
    reserved1: int
    frame_length_in_ns: int
    frame_id: int
    flags_ext: int
    reserved2: int
    data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)
        (
            channel,
            length,
            flags,
            ecc,
            position,
            dlc,
            reserverd1,
            frame_length_in_ns,
            frame_id,
            flags_ext,
            reserved2,
            data,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)
        return cls(
            header,
            channel,
            length,
            flags,
            ecc,
            position,
            dlc,
            reserverd1,
            frame_length_in_ns,
            frame_id,
            flags_ext,
            reserved2,
            data,
        )

    def pack(self) -> bytes:
        return self.header.pack() + self._FORMAT.pack(
            self.channel,
            self.length,
            self.flags,
            self.ecc,
            self.position,
            self.dlc,
            self.reserved1,
            self.frame_length_in_ns,
            self.frame_id,
            self.flags_ext,
            self.reserved2,
            self.data,
        )


@dataclass
class CanFdErrorFrame64(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("BBBBHHHBBIIIIIIIHH")
    _FORMAT_EXT: ClassVar[struct.Struct] = struct.Struct("II")
    header: ObjectHeader
    channel: int
    dlc: int
    valid_data_bytes: int
    ecc: int
    flags: int
    error_code_ext: int
    ext_flags: int
    ext_data_offset: int
    reserved1: int
    frame_id: int
    frame_length: int
    btr_cfg_arb: int
    btr_cfg_data: int
    time_offset_brs_ns: int
    time_offset_crc_del_ns: int
    crc: int
    error_position: int
    reserved2: int
    data: bytes
    btr_ext_arb: int
    btr_ext_data: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer)

        # get fixed size values
        (
            channel,
            dlc,
            valid_data_bytes,
            ecc,
            flags,
            error_code_ext,
            ext_flags,
            ext_data_offset,
            reserved1,
            frame_id,
            frame_length,
            btr_cfg_arb,
            btr_cfg_data,
            time_offset_brs_ns,
            time_offset_crc_del_ns,
            crc,
            error_position,
            reserved2,
        ) = cls._FORMAT.unpack_from(buffer, header.header_size)

        # get data
        data_offset = header.header_size + cls._FORMAT.size
        data = buffer[data_offset : data_offset + valid_data_bytes]

        # get ext frame data
        btr_ext_arb, btr_ext_data = 0, 0
        if header.object_size >= ext_data_offset + cls._FORMAT_EXT.size:
            btr_ext_arb, btr_ext_data = cls._FORMAT_EXT.unpack_from(buffer, ext_data_offset)

        return cls(
            header,
            channel,
            dlc,
            valid_data_bytes,
            ecc,
            flags,
            error_code_ext,
            ext_flags,
            ext_data_offset,
            reserved1,
            frame_id,
            frame_length,
            btr_cfg_arb,
            btr_cfg_data,
            time_offset_brs_ns,
            time_offset_crc_del_ns,
            crc,
            error_position,
            reserved2,
            data,
            btr_ext_arb,
            btr_ext_data,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.object_size)

        # pack header
        self.header.pack_into(buffer, 0)

        # pack fixed size values
        self._FORMAT.pack_into(
            buffer,
            self.header.header_size,
            self.channel,
            self.dlc,
            self.valid_data_bytes,
            self.ecc,
            self.flags,
            self.error_code_ext,
            self.ext_flags,
            self.ext_data_offset,
            self.reserved1,
            self.frame_id,
            self.frame_length,
            self.btr_cfg_arb,
            self.btr_cfg_data,
            self.time_offset_brs_ns,
            self.time_offset_crc_del_ns,
            self.crc,
            self.error_position,
            self.reserved2,
        )

        # pack data
        data_offset = self.header.header_size + self._FORMAT.size
        buffer[data_offset : data_offset + self.valid_data_bytes] = self.data

        # pack ext frame data
        if self.header.object_size >= self.ext_data_offset + self._FORMAT_EXT.size:
            self._FORMAT_EXT.pack_into(
                buffer, self.ext_data_offset, self.btr_ext_arb, self.btr_ext_data
            )
        return bytes(buffer)
