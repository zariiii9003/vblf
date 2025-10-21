import logging
import os
import zlib
from collections.abc import Iterator
from contextlib import AbstractContextManager
from io import BytesIO
from types import TracebackType
from typing import Any, BinaryIO, Final, Optional, Union

from vblf.can import (
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
from vblf.constants import FILE_SIGNATURE, OBJ_SIGNATURE, OBJ_SIGNATURE_SIZE, ObjType
from vblf.ethernet import EthernetFrameEx, EthernetStatistic
from vblf.flexray import FlexrayVFrReceiveMsgEx
from vblf.general import (
    AppText,
    AppTrigger,
    DriverOverrun,
    EnvironmentVariable,
    EventComment,
    FileStatistics,
    FunctionBus,
    GlobalMarker,
    LogContainer,
    NotImplementedObject,
    ObjectHeaderBase,
    ObjectWithHeader,
    RealTimeClock,
    SystemVariable,
    TriggerCondition,
)
from vblf.lin import LinMessage, LinMessage2
from vblf.tp_diag import DiagRequestInterpretation

LOG = logging.getLogger("vblf")


class BlfReader(AbstractContextManager["BlfReader"]):
    """Binary Log Format (BLF) file reader.

    Reads Vector BLF log files and provides an iterator interface to access
    the contained objects. Handles automatic decompression of log containers.

    :param file: Path to BLF file or file-like object
    :raises TypeError: If file parameter is of unsupported type
    :raises ValueError: If file format is invalid

    :ivar file_statistics: Statistics about the BLF file
    :type file_statistics: FileStatistics
    """

    def __init__(self, file: Union[str, bytes, os.PathLike[Any], BinaryIO]):
        """Initialize BLF reader.

        See class documentation for details.
        """
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
        if len(obj_data) < FileStatistics.SIZE or not obj_data.startswith(FILE_SIGNATURE):
            err_msg = "Unexpected file format"
            raise ValueError(err_msg)

        self.file_statistics = FileStatistics.unpack(obj_data)

        self._incomplete_data: bytes = b""
        self._generator = self._generate_objects(self._file)

    def _generate_objects(self, stream: BinaryIO) -> Iterator[ObjectWithHeader[Any]]:
        """Generate objects from the BLF stream.

        :param stream: Binary stream containing BLF data
        :returns: Iterator yielding parsed BLF objects
        """
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
            obj_class: type[ObjectWithHeader[Any]] = (
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

    def read_object(self) -> Optional[ObjectWithHeader[Any]]:
        """Retrieve the next parsed object from the BLF file.

        This method fetches the next object from the underlying generator that
        parses the BLF file. If there are no more objects to read, it returns `None`.

        :returns: The next parsed BLF object or `None` if the end of the file is reached.
        """
        return next(self._generator, None)

    def __iter__(self) -> Iterator[ObjectWithHeader[Any]]:
        """Iterate over objects in the BLF file.

        :returns: Iterator yielding parsed BLF objects
        """
        return self._generator.__iter__()

    def __enter__(self) -> "BlfReader":
        """Enter context manager.

        :returns: BlfReader instance
        """
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """Exit context manager and close file.

        :param exc_type: Exception type if an exception occurred
        :param exc_value: Exception instance if an exception occurred
        :param traceback: Traceback if an exception occurred
        """
        self._file.close()


OBJ_MAP: Final[dict[ObjType, Optional[type[ObjectWithHeader[Any]]]]] = {
    ObjType.UNKNOWN: None,
    ObjType.CAN_MESSAGE: CanMessage,
    ObjType.CAN_ERROR: CanErrorFrame,
    ObjType.CAN_OVERLOAD: CanOverloadFrame,
    ObjType.CAN_STATISTIC: CanDriverStatistic,
    ObjType.APP_TRIGGER: AppTrigger,
    ObjType.ENV_INTEGER: EnvironmentVariable,
    ObjType.ENV_DOUBLE: EnvironmentVariable,
    ObjType.ENV_STRING: EnvironmentVariable,
    ObjType.ENV_DATA: EnvironmentVariable,
    ObjType.LOG_CONTAINER: LogContainer,
    ObjType.LIN_MESSAGE: LinMessage,
    ObjType.LIN_CRC_ERROR: None,
    ObjType.LIN_DLC_INFO: None,
    ObjType.LIN_RCV_ERROR: None,
    ObjType.LIN_SND_ERROR: None,
    ObjType.LIN_SLV_TIMEOUT: None,
    ObjType.LIN_SCHED_MODCH: None,
    ObjType.LIN_SYN_ERROR: None,
    ObjType.LIN_BAUDRATE: None,
    ObjType.LIN_SLEEP: None,
    ObjType.LIN_WAKEUP: None,
    ObjType.MOST_SPY: None,
    ObjType.MOST_CTRL: None,
    ObjType.MOST_LIGHTLOCK: None,
    ObjType.MOST_STATISTIC: None,
    ObjType.reserved_1: None,
    ObjType.reserved_2: None,
    ObjType.reserved_3: None,
    ObjType.FLEXRAY_DATA: None,
    ObjType.FLEXRAY_SYNC: None,
    ObjType.CAN_DRIVER_ERROR: CanDriverError,
    ObjType.MOST_PKT: None,
    ObjType.MOST_PKT2: None,
    ObjType.MOST_HWMODE: None,
    ObjType.MOST_REG: None,
    ObjType.MOST_GENREG: None,
    ObjType.MOST_NETSTATE: None,
    ObjType.MOST_DATALOST: None,
    ObjType.MOST_TRIGGER: None,
    ObjType.FLEXRAY_CYCLE: None,
    ObjType.FLEXRAY_MESSAGE: None,
    ObjType.LIN_CHECKSUM_INFO: None,
    ObjType.LIN_SPIKE_EVENT: None,
    ObjType.CAN_DRIVER_SYNC: CanDriverHwSync,
    ObjType.FLEXRAY_STATUS: None,
    ObjType.GPS_EVENT: None,
    ObjType.FR_ERROR: None,
    ObjType.FR_STATUS: None,
    ObjType.FR_STARTCYCLE: None,
    ObjType.FR_RCVMESSAGE: None,
    ObjType.REALTIMECLOCK: RealTimeClock,
    ObjType.AVAILABLE2: None,
    ObjType.AVAILABLE3: None,
    ObjType.LIN_STATISTIC: None,
    ObjType.J1708_MESSAGE: None,
    ObjType.J1708_VIRTUAL_MSG: None,
    ObjType.LIN_MESSAGE2: LinMessage2,
    ObjType.LIN_SND_ERROR2: None,
    ObjType.LIN_SYN_ERROR2: None,
    ObjType.LIN_CRC_ERROR2: None,
    ObjType.LIN_RCV_ERROR2: None,
    ObjType.LIN_WAKEUP2: None,
    ObjType.LIN_SPIKE_EVENT2: None,
    ObjType.LIN_LONG_DOM_SIG: None,
    ObjType.APP_TEXT: AppText,
    ObjType.FR_RCVMESSAGE_EX: FlexrayVFrReceiveMsgEx,
    ObjType.MOST_STATISTICEX: None,
    ObjType.MOST_TXLIGHT: None,
    ObjType.MOST_ALLOCTAB: None,
    ObjType.MOST_STRESS: None,
    ObjType.ETHERNET_FRAME: None,
    ObjType.SYS_VARIABLE: SystemVariable,
    ObjType.CAN_ERROR_EXT: CanErrorFrameExt,
    ObjType.CAN_DRIVER_ERROR_EXT: CanDriverErrorExt,
    ObjType.LIN_LONG_DOM_SIG2: None,
    ObjType.MOST_150_MESSAGE: None,
    ObjType.MOST_150_PKT: None,
    ObjType.MOST_ETHERNET_PKT: None,
    ObjType.MOST_150_MESSAGE_FRAGMENT: None,
    ObjType.MOST_150_PKT_FRAGMENT: None,
    ObjType.MOST_ETHERNET_PKT_FRAGMENT: None,
    ObjType.MOST_SYSTEM_EVENT: None,
    ObjType.MOST_150_ALLOCTAB: None,
    ObjType.MOST_50_MESSAGE: None,
    ObjType.MOST_50_PKT: None,
    ObjType.CAN_MESSAGE2: CanMessage2,
    ObjType.LIN_UNEXPECTED_WAKEUP: None,
    ObjType.LIN_SHORT_OR_SLOW_RESPONSE: None,
    ObjType.LIN_DISTURBANCE_EVENT: None,
    ObjType.SERIAL_EVENT: None,
    ObjType.OVERRUN_ERROR: DriverOverrun,
    ObjType.EVENT_COMMENT: EventComment,
    ObjType.WLAN_FRAME: None,
    ObjType.WLAN_STATISTIC: None,
    ObjType.MOST_ECL: None,
    ObjType.GLOBAL_MARKER: GlobalMarker,
    ObjType.AFDX_FRAME: None,
    ObjType.AFDX_STATISTIC: None,
    ObjType.KLINE_STATUSEVENT: None,
    ObjType.CAN_FD_MESSAGE: CanFdMessage,
    ObjType.CAN_FD_MESSAGE_64: CanFdMessage64,
    ObjType.ETHERNET_RX_ERROR: None,
    ObjType.ETHERNET_STATUS: None,
    ObjType.CAN_FD_ERROR_64: CanFdErrorFrame64,
    ObjType.LIN_SHORT_OR_SLOW_RESPONSE2: None,
    ObjType.AFDX_STATUS: None,
    ObjType.AFDX_BUS_STATISTIC: None,
    ObjType.reserved_4: None,
    ObjType.AFDX_ERROR_EVENT: None,
    ObjType.A429_ERROR: None,
    ObjType.A429_STATUS: None,
    ObjType.A429_BUS_STATISTIC: None,
    ObjType.A429_MESSAGE: None,
    ObjType.ETHERNET_STATISTIC: EthernetStatistic,
    ObjType.reserved_5: None,
    ObjType.reserved_6: None,
    ObjType.reserved_7: None,
    ObjType.TEST_STRUCTURE: None,
    ObjType.DIAG_REQUEST_INTERPRETATION: DiagRequestInterpretation,
    ObjType.ETHERNET_FRAME_EX: EthernetFrameEx,
    ObjType.ETHERNET_FRAME_FORWARDED: None,
    ObjType.ETHERNET_ERROR_EX: None,
    ObjType.ETHERNET_ERROR_FORWARDED: None,
    ObjType.FUNCTION_BUS: FunctionBus,
    ObjType.DATA_LOST_BEGIN: None,
    ObjType.DATA_LOST_END: None,
    ObjType.WATER_MARK_EVENT: None,
    ObjType.TRIGGER_CONDITION: TriggerCondition,
}
