from typing import Any, List

from bitarray import bitarray

from spi_operation import SequenceTransferOperation
import device_implementation.dac.ad5672.register_operations as op
from util.util_str import reverse_string


class Initialize(SequenceTransferOperation):
    """Initialize the Ad5672R dac."""

    def __init__(self):
        """Initialize the dac for operation in daisychain with 0V to 5V output range."""
        ops = []

        ops.append(
            [
                op.SoftwareReset(),
                op.SetDcEnMode(),
                op.WriteLoadDacMaskRegister(data=bitarray(reverse_string("11111111"))),
                op.InternalReferenceSetup(),
            ]
        )
        super().__init__(ops)

    def _parse_response(self, operations_rsp: List[Any]) -> Any:
        """This method is used to parse the response of type bitarray into the
        desired datatype, which is appropriate for the SingleTransferOperation.

        :param operations_rsp: List of get_parsed_response() of sub Operations
        of self (SequenceTransferOperation).
        :return: None
        """
        if not len(operations_rsp) == 4:
            raise ValueError(
                f"Initialize expected list of 4 responses, but got {operations_rsp=}"
            )
        return None

    # TODO: Add write (to input register)
    # TODO: Add load (all channels, input register to dac register)
    # TODO: Add the above structure to dac_base
