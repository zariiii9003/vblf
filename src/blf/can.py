import struct
from dataclasses import dataclass
from enum import IntFlag
from typing import ClassVar

from .general import ObjectHeader


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
class CanFdMessage(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "HBBIIBBBBI64sI")
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
    def deserialize(cls, data: bytes) -> "CanFdMessage64":
        # get fixed size values
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

    def serialize(self) -> bytes:
        return self.FORMAT.pack(
            self.signature,
            self.header_size,
            self.header_version,
            self.object_size,
            self.object_type,
            self.object_flags,
            self.client_index,
            self.object_version,
            self.object_time_stamp,
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
class CanFdMessage64(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "BBBBIIIIIIIHBBI")
    FORMAT_EXT: ClassVar[struct.Struct] = struct.Struct("II")
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
    def deserialize(cls, data: bytes) -> "CanFdMessage64":
        # get fixed size values
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
        ) = cls.FORMAT.unpack_from(data)

        # get ext frame data
        btr_ext_arb, btr_ext_data = 0, 0
        if object_size >= ext_data_offset + cls.FORMAT_EXT.size:
            btr_ext_arb, btr_ext_data = cls.FORMAT_EXT.unpack_from(data, ext_data_offset)

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
            data[cls.FORMAT.size : cls.FORMAT.size + valid_data_bytes],
            btr_ext_arb,
            btr_ext_data,
        )

    def serialize(self) -> bytes:
        raw = bytearray(self.object_size)

        # serialize fixed size values
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

        # serialize data
        raw[self.FORMAT.size : self.FORMAT.size + self.valid_data_bytes] = self.data

        # serialize ext frame data
        if self.object_size >= self.ext_data_offset + self.FORMAT_EXT.size:
            self.FORMAT_EXT.pack_into(
                raw, self.ext_data_offset, self.btr_ext_arb, self.btr_ext_data
            )
        return bytes(raw)


@dataclass
class CanDriverStatistic(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "HHIIIIIII")
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
    def deserialize(cls, data: bytes) -> "CanDriverStatistic":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class CanDriverError(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "HBBI")
    channel: int
    tx_errors: int
    rx_errors: int
    error_code: int

    @classmethod
    def deserialize(cls, data: bytes) -> "CanDriverError":
        return cls(*cls.FORMAT.unpack(data))

    def serialize(self) -> bytes:
        return self.FORMAT.pack(*self.__dict__.values())


@dataclass
class CanDriverErrorExt(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(ObjectHeader.FORMAT.format + "HBBIIBBH4I")
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
    def deserialize(cls, data: bytes) -> "CanDriverErrorExt":
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
        ) = cls.FORMAT.unpack(data)
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

    def serialize(self) -> bytes:
        return self.FORMAT.pack(
            self.signature,
            self.header_size,
            self.header_version,
            self.object_size,
            self.object_type,
            self.object_flags,
            self.client_index,
            self.object_version,
            self.object_time_stamp,
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
class CanFdErrorFrame64(ObjectHeader):
    FORMAT: ClassVar[struct.Struct] = struct.Struct(
        ObjectHeader.FORMAT.format + "BBBBHHHBBIIIIIIIHH"
    )
    FORMAT_EXT: ClassVar[struct.Struct] = struct.Struct("II")
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
    def deserialize(cls, data: bytes) -> "CanFdMessage64":
        # get fixed size values
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
        ) = cls.FORMAT.unpack_from(data)

        # get ext frame data
        btr_ext_arb, btr_ext_data = 0, 0
        if object_size >= ext_data_offset + cls.FORMAT_EXT.size:
            btr_ext_arb, btr_ext_data = cls.FORMAT_EXT.unpack_from(data, ext_data_offset)

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
            data[cls.FORMAT.size : cls.FORMAT.size + valid_data_bytes],
            btr_ext_arb,
            btr_ext_data,
        )

    def serialize(self) -> bytes:
        raw = bytearray(self.object_size)

        # serialize fixed size values
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

        # serialize data
        raw[self.FORMAT.size : self.FORMAT.size + self.valid_data_bytes] = self.data

        # serialize ext frame data
        if self.object_size >= self.ext_data_offset + self.FORMAT_EXT.size:
            self.FORMAT_EXT.pack_into(
                raw, self.ext_data_offset, self.btr_ext_arb, self.btr_ext_data
            )
        return bytes(raw)
