import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from vblf.general import ObjectHeader, ObjectWithHeader


@dataclass
class FlexrayVFrReceiveMsgEx(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("HHHHIIHHHHHHIIIIIIHHH26s")
    header: ObjectHeader
    channel: int
    version: int
    channel_mask: int
    dir_flags: int
    client_index: int
    cluster_no: int
    frame_id: int
    header_crc1: int
    header_crc2: int
    byte_count: int
    data_count: int
    cycle: int
    tag: int
    data: int
    frame_flags: int
    app_parameter: int
    frame_crc: int
    frame_length_ns: int
    frame_id1: int
    pdu_offset: int
    blf_log_mask: int
    reserved: bytes
    data_bytes: bytes

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            channel,
            version,
            channel_mask,
            dir_flags,
            client_index,
            cluster_no,
            frame_id,
            header_crc1,
            header_crc2,
            byte_count,
            data_count,
            cycle,
            tag,
            data,
            frame_flags,
            app_parameter,
            frame_crc,
            frame_length_ns,
            frame_id1,
            pdu_offset,
            blf_log_mask,
            reserved,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        # get data_bytes
        data_offset = ObjectHeader.SIZE + cls._FORMAT.size
        available_bytes = min(data_count, len(buffer) - data_offset)
        data_bytes = buffer[data_offset : data_offset + available_bytes]

        return cls(
            header,
            channel,
            version,
            channel_mask,
            dir_flags,
            client_index,
            cluster_no,
            frame_id,
            header_crc1,
            header_crc2,
            byte_count,
            data_count,
            cycle,
            tag,
            data,
            frame_flags,
            app_parameter,
            frame_crc,
            frame_length_ns,
            frame_id1,
            pdu_offset,
            blf_log_mask,
            reserved,
            data_bytes,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            ObjectHeader.SIZE,
            self.channel,
            self.version,
            self.channel_mask,
            self.dir_flags,
            self.client_index,
            self.cluster_no,
            self.frame_id,
            self.header_crc1,
            self.header_crc2,
            self.byte_count,
            self.data_count,
            self.cycle,
            self.tag,
            self.data,
            self.frame_flags,
            self.app_parameter,
            self.frame_crc,
            self.frame_length_ns,
            self.frame_id1,
            self.pdu_offset,
            self.blf_log_mask,
            self.reserved,
        )

        # pack data_bytes
        data_offset = ObjectHeader.SIZE + self._FORMAT.size
        buffer[data_offset : data_offset + len(self.data_bytes)] = self.data_bytes

        return bytes(buffer)
