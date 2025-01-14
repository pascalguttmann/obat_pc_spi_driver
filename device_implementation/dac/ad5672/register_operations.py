from __future__ import annotations

from typing import Any, Optional
from bitarray import bitarray
from util import reverse_string, concat_bitarray
from spi_operation import SingleTransferOperation


# AD5672 WORD == 24 bit


class Ad5672SingleTransferOperation(SingleTransferOperation):
    """SingleTransferOperation of Ad5672 with its structure."""

    def __init__(
        self,
        op: bitarray | None = None,
        addr: bitarray | None = None,
        data: bitarray | None = None,
        response: Optional[bitarray] = None,
        response_required: bool = True,
    ):
        if not op:
            op = bitarray(reverse_string("0000"))
        if not addr:
            addr = bitarray(reverse_string("0000"))
        if not data:
            data = bitarray(reverse_string("0000 00000000"))

        data_fill = bitarray(reverse_string("0000"))

        super().__init__(
            command=concat_bitarray(
                data_fill,
                self.check_data(data),
                self.check_addr(addr),
                self.check_op(op),
            ),
            response=response,
            response_required=response_required,
        )

    def _parse_response(self, rsp: bitarray) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        Implements the default _parse_response() method for all
        Ad5672SingleTransferOperation to return 'None'. Should be
        overwritten, by operations that require response parsing.

        :param rsp: bitarray response of spi transfer.
        :return: None
        """
        if not len(rsp) == 24:
            raise ValueError(
                f"Ad5672SingleTransferOperation expected 24-Bit response, but got {rsp=}"
            )

        return None

    def check_op(self, op: bitarray):
        if len(op) != 4:
            raise ValueError(f"Expected 4-bit op, but got {op=}")
        return op

    def check_addr(self, addr: bitarray):
        if len(addr) != 4:
            raise ValueError(f"Expected 4-bit addr, but got {addr=}")
        if addr[3] == 1:
            raise ValueError(
                f"Unknown DAC channel address {addr}. Address should be in the range 0x0 to 0x7."
            )
        return addr

    def check_data(self, data: bitarray):
        if len(data) != 12:
            raise ValueError(f"Expected 12-bit data, but got {data=}")
        return data


class Nop(Ad5672SingleTransferOperation):
    """No operation"""

    def __init__(self):
        super().__init__(response_required=False)


class WriteInputRegister(Ad5672SingleTransferOperation):
    def __init__(self, addr: bitarray, data: bitarray):
        """Write data to the input register of the dac channel specified by the address.

        :param addr: 4-bit addr of dac channel, Valid range 0x0 to 0x7.
        :param data: 12-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("0001")),
            addr=addr,
            data=data,
            response_required=False,
        )


class UpdateDacRegisters(Ad5672SingleTransferOperation):
    def __init__(self, data: bitarray):
        """Update the dac register with contents of input register for the dac
        channel(s) specified by the bits data[0:8]. Setting a bit in data[0:8]
        selects the dac channel to be updated. Bits data[8:12] are ignored.

        :param data: 12-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("0010")),
            data=data,
            response_required=False,
        )


class InputAndDacRegister(Ad5672SingleTransferOperation):
    def __init__(self, addr: bitarray, data: bitarray):
        """Write data to the input register of the dac channel specified by the
        address and directly update the dac register to output the value.

        :param addr: 4-bit addr of dac channel, Valid range 0x0 to 0x7.
        :param data: 12-bit data
        """

        super().__init__(
            op=bitarray(reverse_string("0011")),
            addr=addr,
            data=data,
            response_required=False,
        )


class SetDcEnMode(Ad5672SingleTransferOperation):
    def __init__(self):
        """Set daisychain enable mode (DCEN MODE) of Ad5672."""
        super().__init__(
            op=bitarray(reverse_string("1000")),
            data=bitarray(reverse_string("00000000 00000001")),
            response_required=False,
        )


class ReadDacRegister(Ad5672SingleTransferOperation):
    def __init__(self, addr: bitarray):
        """Read data from the dac register of the dac channel specified by the
        address.

        :param addr: 4-bit addr of dac channel, Valid range 0x0 to 0x7.
        """
        super().__init__(op=bitarray(reverse_string("1001")), response_required=True)

    def _parse_response(self, rsp: bitarray) -> Any:
        return rsp[0:16]
