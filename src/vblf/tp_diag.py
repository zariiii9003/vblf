import struct
from dataclasses import dataclass
from typing import ClassVar

from typing_extensions import Self

from vblf.general import ObjectHeader, ObjectWithHeader


@dataclass
class DiagRequestInterpretation(ObjectWithHeader[ObjectHeader]):
    _FORMAT: ClassVar[struct.Struct] = struct.Struct("IIIIII")
    diag_description_handle: int
    diag_variant_handle: int
    diag_service_handle: int
    ecu_qualifier_length: int
    variant_qualifier_length: int
    service_qualifier_length: int
    ecu_qualifier: str
    variant_qualifier: str
    service_qualifier: str

    @classmethod
    def unpack(cls, buffer: bytes) -> Self:
        header = ObjectHeader.unpack_from(buffer, 0)
        (
            diag_description_handle,
            diag_variant_handle,
            diag_service_handle,
            ecu_qualifier_length,
            variant_qualifier_length,
            service_qualifier_length,
        ) = cls._FORMAT.unpack_from(buffer, ObjectHeader.SIZE)

        ecu_qualifier_offset = ObjectHeader.SIZE + cls._FORMAT.size
        variant_qualifier_offset = ecu_qualifier_offset + ecu_qualifier_length
        service_qualifier_offset = variant_qualifier_offset + variant_qualifier_length

        ecu_qualifier = buffer[
            ecu_qualifier_offset : ecu_qualifier_offset + ecu_qualifier_length
        ].decode("utf-8")
        variant_qualifier = buffer[
            variant_qualifier_offset : variant_qualifier_offset + variant_qualifier_length
        ].decode("utf-8")
        service_qualifier = buffer[
            service_qualifier_offset : service_qualifier_offset + service_qualifier_length
        ].decode("utf-8")

        return cls(
            header,
            diag_description_handle,
            diag_variant_handle,
            diag_service_handle,
            ecu_qualifier_length,
            variant_qualifier_length,
            service_qualifier_length,
            ecu_qualifier,
            variant_qualifier,
            service_qualifier,
        )

    def pack(self) -> bytes:
        buffer = bytearray(self.header.base.object_size)
        self.header.pack_into(buffer, 0)
        self._FORMAT.pack_into(
            buffer,
            ObjectHeader.SIZE,
            self.diag_description_handle,
            self.diag_variant_handle,
            self.diag_service_handle,
            self.ecu_qualifier_length,
            self.variant_qualifier_length,
            self.service_qualifier_length,
        )

        ecu_qualifier_offset = ObjectHeader.SIZE + self._FORMAT.size
        variant_qualifier_offset = ecu_qualifier_offset + self.ecu_qualifier_length
        service_qualifier_offset = variant_qualifier_offset + self.variant_qualifier_length

        buffer[ecu_qualifier_offset : ecu_qualifier_offset + self.ecu_qualifier_length] = (
            self.ecu_qualifier.encode("utf-8")
        )
        buffer[
            variant_qualifier_offset : variant_qualifier_offset + self.variant_qualifier_length
        ] = self.variant_qualifier.encode("utf-8")
        buffer[
            service_qualifier_offset : service_qualifier_offset + self.service_qualifier_length
        ] = self.service_qualifier.encode("utf-8")

        return bytes(buffer)
