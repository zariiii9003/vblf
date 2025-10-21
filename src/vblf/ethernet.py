import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from vblf.general import ObjectHeader, ObjectWithHeader


@dataclass
class EthernetFrameEx(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHHHQIHHII")
    header: ObjectHeader
    struct_length: int
    flags: int
    channel: int
    hardware_channel: int
    frame_duration: int
    frame_checksum: int
    dir: int
    frame_length: int
    frame_handle: int
    reserved: int
    frame_data: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            struct_length,
            flags,
            channel,
            hardware_channel,
            frame_duration,
            frame_checksum,
            direction,
            frame_length,
            frame_handle,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        # get data_bytes
        data_offset = ObjectHeader.SIZE + cls._FORMAT.size
        available_bytes = min(frame_length, len(buffer) - data_offset)
        data_bytes = buffer[data_offset : data_offset + available_bytes]

        return cls(
            header,
            struct_length,
            flags,
            channel,
            hardware_channel,
            frame_duration,
            frame_checksum,
            direction,
            frame_length,
            frame_handle,
            reserved,
            data_bytes,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            ObjectHeader.SIZE,
            self.struct_length,
            self.flags,
            self.channel,
            self.hardware_channel,
            self.frame_duration,
            self.frame_checksum,
            self.dir,
            self.frame_length,
            self.frame_handle,
            self.reserved,
        )

        # pack data_bytes
        data_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[data_offset : data_offset + len(self.frame_data)] = self.frame_data

        return bytes(buffer)


@dataclass
class EthernetStatistic(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHIQQQQQQQhHI")
    channel: int
    reserved_1: int
    reserved_2: int
    rcv_ok_hw: int
    xmit_ok_hw: int
    rcv_error_hw: int
    xmit_error_hw: int
    rcv_bytes_hw: int
    xmit_bytes_hw: int
    rcv_no_buffer_hw: int
    sqi: int
    hardware_channel: int
    reserved_3: int

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            channel,
            reserved_1,
            reserved_2,
            rcv_ok_hw,
            xmit_ok_hw,
            rcv_error_hw,
            xmit_error_hw,
            rcv_bytes_hw,
            xmit_bytes_hw,
            rcv_no_buffer_hw,
            sqi,
            hardware_channel,
            reserved_3,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        return cls(
            header,
            channel,
            reserved_1,
            reserved_2,
            rcv_ok_hw,
            xmit_ok_hw,
            rcv_error_hw,
            xmit_error_hw,
            rcv_bytes_hw,
            xmit_bytes_hw,
            rcv_no_buffer_hw,
            sqi,
            hardware_channel,
            reserved_3,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            ObjectHeader.SIZE,
            self.channel,
            self.reserved_1,
            self.reserved_2,
            self.rcv_ok_hw,
            self.xmit_ok_hw,
            self.rcv_error_hw,
            self.xmit_error_hw,
            self.rcv_bytes_hw,
            self.xmit_bytes_hw,
            self.rcv_no_buffer_hw,
            self.sqi,
            self.hardware_channel,
            self.reserved_3,
        )
        return bytes(buffer)
