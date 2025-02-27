from copy import deepcopy
import unittest

from bitarray import bitarray

from util import reverse_string
from single_transfer_operation import SingleTransferOperation
from sequence_transfer_operation import SequenceTransferOperation


class TestSequenceTransferOperation(unittest.TestCase):
    op_cmd_10_bit = bitarray(reverse_string("0001000100"))
    op_rsp_10_bit = bitarray(reverse_string("1000100010"))
    single_op = SingleTransferOperation(
        op_cmd_10_bit, op_rsp_10_bit, response_required=True
    )

    def test_init_001(self):
        multi_op = SequenceTransferOperation([self.single_op])
        self.assertIsInstance(multi_op._operations, list)
        self.assertEqual(len(multi_op._operations), 1)
        self.assertIsInstance(multi_op._operations[0], SingleTransferOperation)
        self.assertIsNot(multi_op._operations[0], self.single_op)
        self.assertEqual(multi_op._operations[0], self.single_op)

    def test_init_002(self):
        with self.assertRaises(ValueError):
            _ = SequenceTransferOperation([])

    def test_len_001(self):
        multi_op = SequenceTransferOperation([self.single_op, self.single_op])
        self.assertEqual(len(multi_op), 2)

    def test_len_002(self):
        multi_op = SequenceTransferOperation(
            [
                self.single_op,
                SequenceTransferOperation(
                    [
                        self.single_op,
                        self.single_op,
                        SequenceTransferOperation(
                            [
                                self.single_op,
                            ]
                        ),
                    ]
                ),
                self.single_op,
            ]
        )
        self.assertEqual(len(multi_op), 5)

    def test_eq(self):
        op = SequenceTransferOperation([self.single_op])
        op_eq = SequenceTransferOperation([self.single_op])
        op_neq = SequenceTransferOperation(
            [SequenceTransferOperation([self.single_op])]
        )
        self.assertIsNot(op, op_eq)
        self.assertEqual(op, op_eq)
        self.assertIsNot(op, op_neq)
        self.assertNotEqual(op, op_neq)

    def test_get_single_transfer_operations_001(self):
        multi_op = SequenceTransferOperation([self.single_op])
        list_op = multi_op.get_single_transfer_operations()
        self.assertIsInstance(list_op, list)
        self.assertEqual(len(list_op), 1)
        self.assertIsInstance(list_op[0], SingleTransferOperation)
        self.assertIsNot(list_op[0], self.single_op)
        self.assertEqual(list_op[0], self.single_op)

    def test_get_single_transfer_operations_002(self):
        multi_op = SequenceTransferOperation(
            [
                self.single_op,
                SequenceTransferOperation(
                    [
                        self.single_op,
                        self.single_op,
                        SequenceTransferOperation(
                            [
                                self.single_op,
                            ]
                        ),
                    ]
                ),
                self.single_op,
            ]
        )
        list_op = multi_op.get_single_transfer_operations()
        self.assertIsInstance(list_op, list)
        self.assertEqual(len(list_op), len(multi_op))
        for single_op in list_op:
            self.assertIsInstance(single_op, SingleTransferOperation)
            self.assertIsNot(single_op, self.single_op)
            self.assertEqual(single_op, self.single_op)

    def test_get_parsed_response_001(self):
        with self.assertRaises(NotImplementedError):

            def _parse_response(rsp: bitarray):
                _, _ = self, rsp
                ans: int = 1
                return ans

            single_op_with_response_parse = deepcopy(self.single_op)
            single_op_with_response_parse._parse_response = _parse_response

            op = SequenceTransferOperation([single_op_with_response_parse])
            _ = op.get_parsed_response()

    def test_get_parsed_response_002(self):
        with self.assertRaises(ValueError):
            op = SequenceTransferOperation(
                [SingleTransferOperation(self.op_cmd_10_bit, response_required=True)]
            )
            _ = op.get_parsed_response()

    def test_get_parsed_response_003(self):
        def _parse_response(rsp: bitarray):
            _, _ = self, rsp
            return None

        single_op_with_response_parse = deepcopy(self.single_op)
        single_op_with_response_parse._parse_response = _parse_response

        op = SequenceTransferOperation([single_op_with_response_parse])
        parsed_rsp = op.get_parsed_response()

        self.assertIs(parsed_rsp, None)
