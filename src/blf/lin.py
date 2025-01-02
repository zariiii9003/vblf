import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from blf.general import ObjectHeader, ObjectWithHeader


@dataclass
class LinMessage(ObjectWithHeader):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HBB8sBBBBHB5s")
    header: ObjectHeader
    channel: int
    frame_id: int
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
            frame_id,
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
            frame_id,
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
            self.frame_id,
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
