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
