import logging
import os
import zlib
from collections.abc import Iterator
from contextlib import AbstractContextManager
from io import BytesIO
from types import TracebackType
from typing import Any, BinaryIO, Final, Optional, Union

from blf.can import (
    CanDriverError,
    CanDriverErrorExt,
    CanDriverHwSync,
    CanDriverStatistic,
    CanErrorFrame,
    CanErrorFrameExt,
    CanFdErrorFrame64,
    CanFdMessage,
    CanFdMessage64,
    CanMessage,
    CanMessage2,
    CanOverloadFrame,
)
from blf.constants import OBJ_SIGNATURE, OBJ_SIGNATURE_SIZE, ObjTypeEnum
from blf.general import (
    AppText,
    AppTrigger,
    DriverOverrun,
    EnvironmentVariable,
    EventComment,
    FileStatistics,
    GlobalMarker,
    LogContainer,
    NotImplementedObject,
    ObjectHeaderBase,
    ObjectWithHeader,
    RealTimeClock,
    SystemVariable,
)

LOG = logging.getLogger("blf")


class BlfReader(AbstractContextManager["BlfReader"]):
    def __init__(self, file: Union[str, bytes, os.PathLike[Any], BinaryIO]):
        self._file: BinaryIO
        if isinstance(file, (str, bytes, os.PathLike)):
            self._file = open(file, "rb")  # noqa: SIM115
        elif isinstance(file, bytes):
            self._file = BytesIO(file)
        elif hasattr(file, "read"):
            self._file = file
        else:
            err_msg = "Unsupported type {type(file)}"
            raise TypeError(err_msg)

        obj_data = self._file.read(FileStatistics.SIZE)
        if len(obj_data) < FileStatistics.SIZE or not obj_data.startswith(b"LOGG"):
            err_msg = "Unexpected file format"
            raise ValueError(err_msg)

        self.file_statistics = FileStatistics.unpack(obj_data)

        self._incomplete_data: bytes = b""
        self._generator = self._generate_objects(self._file)

    def _generate_objects(self, stream: BinaryIO) -> Iterator[ObjectWithHeader]:
        while True:
            # find start of next object (search for b"LOBJ")
            signature = stream.read(OBJ_SIGNATURE_SIZE)
            if len(signature) != OBJ_SIGNATURE_SIZE:
                self._incomplete_data = signature
                break
            if signature != OBJ_SIGNATURE:
                # skip padding byte and try again
                stream.seek(1 - OBJ_SIGNATURE_SIZE, os.SEEK_CUR)
                continue

            # parse base header of object
            header_base_data = signature + stream.read(ObjectHeaderBase.SIZE - OBJ_SIGNATURE_SIZE)
            if len(header_base_data) < ObjectHeaderBase.SIZE:
                self._incomplete_data = header_base_data
                break
            else:
                header_base = ObjectHeaderBase.unpack(header_base_data)

            # read object data
            obj_data = header_base_data + stream.read(
                header_base.object_size - ObjectHeaderBase.SIZE
            )
            if len(obj_data) < header_base.object_size:
                self._incomplete_data = obj_data
                break

            # find class for given object_type
            obj_class: type[ObjectWithHeader] = (
                OBJ_MAP.get(header_base.object_type) or NotImplementedObject
            )

            if obj_class is LogContainer:
                # decompress data
                container = LogContainer.unpack(obj_data)
                uncompressed = (
                    zlib.decompress(container.data)
                    if self.file_statistics.compression_level > 0
                    else container.data
                )

                # prepend incomplete data of previous container
                uncompressed = self._incomplete_data + uncompressed
                self._incomplete_data = b""

                # parse LogContainer data
                yield from self._generate_objects(BytesIO(uncompressed))

            else:
                yield obj_class.unpack(obj_data)

    def __iter__(self) -> Iterator[ObjectWithHeader]:
        return self._generator.__iter__()

    def __enter__(self) -> "BlfReader":
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._file.close()


OBJ_MAP: Final[dict[ObjTypeEnum, Optional[type[ObjectWithHeader]]]] = {
    ObjTypeEnum.UNKNOWN: None,
    ObjTypeEnum.CAN_MESSAGE: CanMessage,
    ObjTypeEnum.CAN_ERROR: CanErrorFrame,
    ObjTypeEnum.CAN_OVERLOAD: CanOverloadFrame,
    ObjTypeEnum.CAN_STATISTIC: CanDriverStatistic,
    ObjTypeEnum.APP_TRIGGER: AppTrigger,
    ObjTypeEnum.ENV_INTEGER: EnvironmentVariable,
    ObjTypeEnum.ENV_DOUBLE: EnvironmentVariable,
    ObjTypeEnum.ENV_STRING: EnvironmentVariable,
    ObjTypeEnum.ENV_DATA: EnvironmentVariable,
    ObjTypeEnum.LOG_CONTAINER: LogContainer,
    ObjTypeEnum.LIN_MESSAGE: None,
    ObjTypeEnum.LIN_CRC_ERROR: None,
    ObjTypeEnum.LIN_DLC_INFO: None,
    ObjTypeEnum.LIN_RCV_ERROR: None,
    ObjTypeEnum.LIN_SND_ERROR: None,
    ObjTypeEnum.LIN_SLV_TIMEOUT: None,
    ObjTypeEnum.LIN_SCHED_MODCH: None,
    ObjTypeEnum.LIN_SYN_ERROR: None,
    ObjTypeEnum.LIN_BAUDRATE: None,
    ObjTypeEnum.LIN_SLEEP: None,
    ObjTypeEnum.LIN_WAKEUP: None,
    ObjTypeEnum.MOST_SPY: None,
    ObjTypeEnum.MOST_CTRL: None,
    ObjTypeEnum.MOST_LIGHTLOCK: None,
    ObjTypeEnum.MOST_STATISTIC: None,
    ObjTypeEnum.reserved_1: None,
    ObjTypeEnum.reserved_2: None,
    ObjTypeEnum.reserved_3: None,
    ObjTypeEnum.FLEXRAY_DATA: None,
    ObjTypeEnum.FLEXRAY_SYNC: None,
    ObjTypeEnum.CAN_DRIVER_ERROR: CanDriverError,
    ObjTypeEnum.MOST_PKT: None,
    ObjTypeEnum.MOST_PKT2: None,
    ObjTypeEnum.MOST_HWMODE: None,
    ObjTypeEnum.MOST_REG: None,
    ObjTypeEnum.MOST_GENREG: None,
    ObjTypeEnum.MOST_NETSTATE: None,
    ObjTypeEnum.MOST_DATALOST: None,
    ObjTypeEnum.MOST_TRIGGER: None,
    ObjTypeEnum.FLEXRAY_CYCLE: None,
    ObjTypeEnum.FLEXRAY_MESSAGE: None,
    ObjTypeEnum.LIN_CHECKSUM_INFO: None,
    ObjTypeEnum.LIN_SPIKE_EVENT: None,
    ObjTypeEnum.CAN_DRIVER_SYNC: CanDriverHwSync,
    ObjTypeEnum.FLEXRAY_STATUS: None,
    ObjTypeEnum.GPS_EVENT: None,
    ObjTypeEnum.FR_ERROR: None,
    ObjTypeEnum.FR_STATUS: None,
    ObjTypeEnum.FR_STARTCYCLE: None,
    ObjTypeEnum.FR_RCVMESSAGE: None,
    ObjTypeEnum.REALTIMECLOCK: RealTimeClock,
    ObjTypeEnum.AVAILABLE2: None,
    ObjTypeEnum.AVAILABLE3: None,
    ObjTypeEnum.LIN_STATISTIC: None,
    ObjTypeEnum.J1708_MESSAGE: None,
    ObjTypeEnum.J1708_VIRTUAL_MSG: None,
    ObjTypeEnum.LIN_MESSAGE2: None,
    ObjTypeEnum.LIN_SND_ERROR2: None,
    ObjTypeEnum.LIN_SYN_ERROR2: None,
    ObjTypeEnum.LIN_CRC_ERROR2: None,
    ObjTypeEnum.LIN_RCV_ERROR2: None,
    ObjTypeEnum.LIN_WAKEUP2: None,
    ObjTypeEnum.LIN_SPIKE_EVENT2: None,
    ObjTypeEnum.LIN_LONG_DOM_SIG: None,
    ObjTypeEnum.APP_TEXT: AppText,
    ObjTypeEnum.FR_RCVMESSAGE_EX: None,
    ObjTypeEnum.MOST_STATISTICEX: None,
    ObjTypeEnum.MOST_TXLIGHT: None,
    ObjTypeEnum.MOST_ALLOCTAB: None,
    ObjTypeEnum.MOST_STRESS: None,
    ObjTypeEnum.ETHERNET_FRAME: None,
    ObjTypeEnum.SYS_VARIABLE: SystemVariable,
    ObjTypeEnum.CAN_ERROR_EXT: CanErrorFrameExt,
    ObjTypeEnum.CAN_DRIVER_ERROR_EXT: CanDriverErrorExt,
    ObjTypeEnum.LIN_LONG_DOM_SIG2: None,
    ObjTypeEnum.MOST_150_MESSAGE: None,
    ObjTypeEnum.MOST_150_PKT: None,
    ObjTypeEnum.MOST_ETHERNET_PKT: None,
    ObjTypeEnum.MOST_150_MESSAGE_FRAGMENT: None,
    ObjTypeEnum.MOST_150_PKT_FRAGMENT: None,
    ObjTypeEnum.MOST_ETHERNET_PKT_FRAGMENT: None,
    ObjTypeEnum.MOST_SYSTEM_EVENT: None,
    ObjTypeEnum.MOST_150_ALLOCTAB: None,
    ObjTypeEnum.MOST_50_MESSAGE: None,
    ObjTypeEnum.MOST_50_PKT: None,
    ObjTypeEnum.CAN_MESSAGE2: CanMessage2,
    ObjTypeEnum.LIN_UNEXPECTED_WAKEUP: None,
    ObjTypeEnum.LIN_SHORT_OR_SLOW_RESPONSE: None,
    ObjTypeEnum.LIN_DISTURBANCE_EVENT: None,
    ObjTypeEnum.SERIAL_EVENT: None,
    ObjTypeEnum.OVERRUN_ERROR: DriverOverrun,
    ObjTypeEnum.EVENT_COMMENT: EventComment,
    ObjTypeEnum.WLAN_FRAME: None,
    ObjTypeEnum.WLAN_STATISTIC: None,
    ObjTypeEnum.MOST_ECL: None,
    ObjTypeEnum.GLOBAL_MARKER: GlobalMarker,
    ObjTypeEnum.AFDX_FRAME: None,
    ObjTypeEnum.AFDX_STATISTIC: None,
    ObjTypeEnum.KLINE_STATUSEVENT: None,
    ObjTypeEnum.CAN_FD_MESSAGE: CanFdMessage,
    ObjTypeEnum.CAN_FD_MESSAGE_64: CanFdMessage64,
    ObjTypeEnum.ETHERNET_RX_ERROR: None,
    ObjTypeEnum.ETHERNET_STATUS: None,
    ObjTypeEnum.CAN_FD_ERROR_64: CanFdErrorFrame64,
    ObjTypeEnum.LIN_SHORT_OR_SLOW_RESPONSE2: None,
    ObjTypeEnum.AFDX_STATUS: None,
    ObjTypeEnum.AFDX_BUS_STATISTIC: None,
    ObjTypeEnum.reserved_4: None,
    ObjTypeEnum.AFDX_ERROR_EVENT: None,
    ObjTypeEnum.A429_ERROR: None,
    ObjTypeEnum.A429_STATUS: None,
    ObjTypeEnum.A429_BUS_STATISTIC: None,
    ObjTypeEnum.A429_MESSAGE: None,
    ObjTypeEnum.ETHERNET_STATISTIC: None,
    ObjTypeEnum.reserved_5: None,
    ObjTypeEnum.reserved_6: None,
    ObjTypeEnum.reserved_7: None,
    ObjTypeEnum.TEST_STRUCTURE: None,
    ObjTypeEnum.DIAG_REQUEST_INTERPRETATION: None,
    ObjTypeEnum.ETHERNET_FRAME_EX: None,
    ObjTypeEnum.ETHERNET_FRAME_FORWARDED: None,
    ObjTypeEnum.ETHERNET_ERROR_EX: None,
    ObjTypeEnum.ETHERNET_ERROR_FORWARDED: None,
    ObjTypeEnum.FUNCTION_BUS: None,
    ObjTypeEnum.DATA_LOST_BEGIN: None,
    ObjTypeEnum.DATA_LOST_END: None,
    ObjTypeEnum.WATER_MARK_EVENT: None,
    ObjTypeEnum.TRIGGER_CONDITION: None,
}
