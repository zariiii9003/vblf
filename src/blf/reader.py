import logging
import os
import zlib
from collections.abc import Iterator
from contextlib import AbstractContextManager
from io import BytesIO
from types import TracebackType
from typing import BinaryIO, Final, Optional, Union

from blf.can import (
    CanDriverError,
    CanDriverErrorExt,
    CanDriverStatistic,
    CanErrorFrame,
    CanErrorFrameExt,
    CanFdErrorFrame64,
    CanFdMessage,
    CanFdMessage64,
    CanMessage,
    CanMessage2,
)
from blf.constants import OBJ_SIGNATURE, OBJ_SIGNATURE_SIZE, ObjTypeEnum
from blf.general import (
    AppText,
    FileStatistics,
    LogContainer,
    ObjectHeaderBase,
    ObjectWithHeader,
)

LOG = logging.getLogger("blf")
_OBJ_HEADER_BASE_SIZE: Final = ObjectHeaderBase.calc_size()
_FILE_STATISTICS_SIZE: Final = FileStatistics.calc_size()


class BlfReader(AbstractContextManager):
    def __init__(self, file: Union[str, bytes, os.PathLike, BinaryIO]):
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

        obj_data = self._file.read(_FILE_STATISTICS_SIZE)
        if len(obj_data) < _FILE_STATISTICS_SIZE or not obj_data.startswith(b"LOGG"):
            err_msg = "Unexpected file format"
            raise ValueError(err_msg)

        self.file_statistics = FileStatistics.unpack(self._file.read(_FILE_STATISTICS_SIZE))

        self._incomplete_data: bytes = b""
        self._generator = self._generate_objects(self._file)

    def _generate_objects(self, stream: BinaryIO) -> Iterator[ObjectWithHeader]:
        while True:
            signature = stream.read(OBJ_SIGNATURE_SIZE)
            if len(signature) != OBJ_SIGNATURE_SIZE:
                self._incomplete_data = signature
                break
            if signature != OBJ_SIGNATURE:
                # skip padding byte and try again
                stream.seek(1 - OBJ_SIGNATURE_SIZE, os.SEEK_CUR)
                continue

            header_base_data = signature + stream.read(_OBJ_HEADER_BASE_SIZE - OBJ_SIGNATURE_SIZE)
            if len(header_base_data) < _OBJ_HEADER_BASE_SIZE:
                self._incomplete_data = header_base_data
                break

            # read object data
            header_base = ObjectHeaderBase.unpack(header_base_data)
            obj_data = header_base_data + stream.read(
                header_base.object_size - _OBJ_HEADER_BASE_SIZE
            )
            if len(obj_data) < header_base.object_size:
                self._incomplete_data = obj_data
                break

            # interpret object data
            obj_class = OBJ_MAP.get(header_base.object_type)
            if not obj_class:
                try:
                    object_type = ObjTypeEnum(header_base.object_type).name
                except ValueError:
                    object_type = str(header_base.object_type)

                LOG.info("BLF object type '%s' is not implemented.", object_type)
                continue

            if obj_class is LogContainer:
                # decompress data
                container = LogContainer.unpack(obj_data)
                uncompressed = (
                    zlib.decompress(container.data)
                    if self.file_statistics.compression_level
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


OBJ_MAP: Final[dict[int, Optional[type[ObjectWithHeader]]]] = {
    ObjTypeEnum.UNKNOWN.value: None,
    ObjTypeEnum.CAN_MESSAGE.value: CanMessage,
    ObjTypeEnum.CAN_ERROR.value: CanErrorFrame,
    ObjTypeEnum.CAN_OVERLOAD.value: None,
    ObjTypeEnum.CAN_STATISTIC.value: CanDriverStatistic,
    ObjTypeEnum.APP_TRIGGER.value: None,
    ObjTypeEnum.ENV_INTEGER.value: None,
    ObjTypeEnum.ENV_DOUBLE.value: None,
    ObjTypeEnum.ENV_STRING.value: None,
    ObjTypeEnum.ENV_DATA.value: None,
    ObjTypeEnum.LOG_CONTAINER.value: LogContainer,
    ObjTypeEnum.LIN_MESSAGE.value: None,
    ObjTypeEnum.LIN_CRC_ERROR.value: None,
    ObjTypeEnum.LIN_DLC_INFO.value: None,
    ObjTypeEnum.LIN_RCV_ERROR.value: None,
    ObjTypeEnum.LIN_SND_ERROR.value: None,
    ObjTypeEnum.LIN_SLV_TIMEOUT.value: None,
    ObjTypeEnum.LIN_SCHED_MODCH.value: None,
    ObjTypeEnum.LIN_SYN_ERROR.value: None,
    ObjTypeEnum.LIN_BAUDRATE.value: None,
    ObjTypeEnum.LIN_SLEEP.value: None,
    ObjTypeEnum.LIN_WAKEUP.value: None,
    ObjTypeEnum.MOST_SPY.value: None,
    ObjTypeEnum.MOST_CTRL.value: None,
    ObjTypeEnum.MOST_LIGHTLOCK.value: None,
    ObjTypeEnum.MOST_STATISTIC.value: None,
    ObjTypeEnum.reserved_1.value: None,
    ObjTypeEnum.reserved_2.value: None,
    ObjTypeEnum.reserved_3.value: None,
    ObjTypeEnum.FLEXRAY_DATA.value: None,
    ObjTypeEnum.FLEXRAY_SYNC.value: None,
    ObjTypeEnum.CAN_DRIVER_ERROR.value: CanDriverError,
    ObjTypeEnum.MOST_PKT.value: None,
    ObjTypeEnum.MOST_PKT2.value: None,
    ObjTypeEnum.MOST_HWMODE.value: None,
    ObjTypeEnum.MOST_REG.value: None,
    ObjTypeEnum.MOST_GENREG.value: None,
    ObjTypeEnum.MOST_NETSTATE.value: None,
    ObjTypeEnum.MOST_DATALOST.value: None,
    ObjTypeEnum.MOST_TRIGGER.value: None,
    ObjTypeEnum.FLEXRAY_CYCLE.value: None,
    ObjTypeEnum.FLEXRAY_MESSAGE.value: None,
    ObjTypeEnum.LIN_CHECKSUM_INFO.value: None,
    ObjTypeEnum.LIN_SPIKE_EVENT.value: None,
    ObjTypeEnum.CAN_DRIVER_SYNC.value: None,
    ObjTypeEnum.FLEXRAY_STATUS.value: None,
    ObjTypeEnum.GPS_EVENT.value: None,
    ObjTypeEnum.FR_ERROR.value: None,
    ObjTypeEnum.FR_STATUS.value: None,
    ObjTypeEnum.FR_STARTCYCLE.value: None,
    ObjTypeEnum.FR_RCVMESSAGE.value: None,
    ObjTypeEnum.REALTIMECLOCK.value: None,
    ObjTypeEnum.AVAILABLE2.value: None,
    ObjTypeEnum.AVAILABLE3.value: None,
    ObjTypeEnum.LIN_STATISTIC.value: None,
    ObjTypeEnum.J1708_MESSAGE.value: None,
    ObjTypeEnum.J1708_VIRTUAL_MSG.value: None,
    ObjTypeEnum.LIN_MESSAGE2.value: None,
    ObjTypeEnum.LIN_SND_ERROR2.value: None,
    ObjTypeEnum.LIN_SYN_ERROR2.value: None,
    ObjTypeEnum.LIN_CRC_ERROR2.value: None,
    ObjTypeEnum.LIN_RCV_ERROR2.value: None,
    ObjTypeEnum.LIN_WAKEUP2.value: None,
    ObjTypeEnum.LIN_SPIKE_EVENT2.value: None,
    ObjTypeEnum.LIN_LONG_DOM_SIG.value: None,
    ObjTypeEnum.APP_TEXT.value: AppText,
    ObjTypeEnum.FR_RCVMESSAGE_EX.value: None,
    ObjTypeEnum.MOST_STATISTICEX.value: None,
    ObjTypeEnum.MOST_TXLIGHT.value: None,
    ObjTypeEnum.MOST_ALLOCTAB.value: None,
    ObjTypeEnum.MOST_STRESS.value: None,
    ObjTypeEnum.ETHERNET_FRAME.value: None,
    ObjTypeEnum.SYS_VARIABLE.value: None,
    ObjTypeEnum.CAN_ERROR_EXT.value: CanErrorFrameExt,
    ObjTypeEnum.CAN_DRIVER_ERROR_EXT.value: CanDriverErrorExt,
    ObjTypeEnum.LIN_LONG_DOM_SIG2.value: None,
    ObjTypeEnum.MOST_150_MESSAGE.value: None,
    ObjTypeEnum.MOST_150_PKT.value: None,
    ObjTypeEnum.MOST_ETHERNET_PKT.value: None,
    ObjTypeEnum.MOST_150_MESSAGE_FRAGMENT.value: None,
    ObjTypeEnum.MOST_150_PKT_FRAGMENT.value: None,
    ObjTypeEnum.MOST_ETHERNET_PKT_FRAGMENT.value: None,
    ObjTypeEnum.MOST_SYSTEM_EVENT.value: None,
    ObjTypeEnum.MOST_150_ALLOCTAB.value: None,
    ObjTypeEnum.MOST_50_MESSAGE.value: None,
    ObjTypeEnum.MOST_50_PKT.value: None,
    ObjTypeEnum.CAN_MESSAGE2.value: CanMessage2,
    ObjTypeEnum.LIN_UNEXPECTED_WAKEUP.value: None,
    ObjTypeEnum.LIN_SHORT_OR_SLOW_RESPONSE.value: None,
    ObjTypeEnum.LIN_DISTURBANCE_EVENT.value: None,
    ObjTypeEnum.SERIAL_EVENT.value: None,
    ObjTypeEnum.OVERRUN_ERROR.value: None,
    ObjTypeEnum.EVENT_COMMENT.value: None,
    ObjTypeEnum.WLAN_FRAME.value: None,
    ObjTypeEnum.WLAN_STATISTIC.value: None,
    ObjTypeEnum.MOST_ECL.value: None,
    ObjTypeEnum.GLOBAL_MARKER.value: None,
    ObjTypeEnum.AFDX_FRAME.value: None,
    ObjTypeEnum.AFDX_STATISTIC.value: None,
    ObjTypeEnum.KLINE_STATUSEVENT.value: None,
    ObjTypeEnum.CAN_FD_MESSAGE.value: CanFdMessage,
    ObjTypeEnum.CAN_FD_MESSAGE_64.value: CanFdMessage64,
    ObjTypeEnum.ETHERNET_RX_ERROR.value: None,
    ObjTypeEnum.ETHERNET_STATUS.value: None,
    ObjTypeEnum.CAN_FD_ERROR_64.value: CanFdErrorFrame64,
    ObjTypeEnum.LIN_SHORT_OR_SLOW_RESPONSE2.value: None,
    ObjTypeEnum.AFDX_STATUS.value: None,
    ObjTypeEnum.AFDX_BUS_STATISTIC.value: None,
    ObjTypeEnum.reserved_4.value: None,
    ObjTypeEnum.AFDX_ERROR_EVENT.value: None,
    ObjTypeEnum.A429_ERROR.value: None,
    ObjTypeEnum.A429_STATUS.value: None,
    ObjTypeEnum.A429_BUS_STATISTIC.value: None,
    ObjTypeEnum.A429_MESSAGE.value: None,
    ObjTypeEnum.ETHERNET_STATISTIC.value: None,
    ObjTypeEnum.reserved_5.value: None,
    ObjTypeEnum.reserved_6.value: None,
    ObjTypeEnum.reserved_7.value: None,
    ObjTypeEnum.TEST_STRUCTURE.value: None,
    ObjTypeEnum.DIAG_REQUEST_INTERPRETATION.value: None,
    ObjTypeEnum.ETHERNET_FRAME_EX.value: None,
    ObjTypeEnum.ETHERNET_FRAME_FORWARDED.value: None,
    ObjTypeEnum.ETHERNET_ERROR_EX.value: None,
    ObjTypeEnum.ETHERNET_ERROR_FORWARDED.value: None,
    ObjTypeEnum.FUNCTION_BUS.value: None,
    ObjTypeEnum.DATA_LOST_BEGIN.value: None,
    ObjTypeEnum.DATA_LOST_END.value: None,
    ObjTypeEnum.WATER_MARK_EVENT.value: None,
    ObjTypeEnum.TRIGGER_CONDITION.value: None,
}
