import unittest
import inputs
from collections import namedtuple


class TestInvalidInputError(unittest.TestCase):
    def test_str(self):
        TestCase = namedtuple(
            'TestCase', 'reason input_names input_val expected_str')
        test_cases = {
            'no_input_val': TestCase(
                reason="it's missing",
                input_names=inputs.X_NAME,
                input_val=None,
                expected_str="InvalidInputError: invalid %s: it's missing" % (inputs.X_NAME)),
            'with_input_val': TestCase(
                reason="it's bad",
                input_names=inputs.Y_NAME,
                input_val='something_invalid',
                expected_str="InvalidInputError: invalid %s - 'something_invalid': it's bad" % (inputs.Y_NAME)),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                err = inputs.InvalidInputError(
                    test_case.reason,
                    test_case.input_names,
                    test_case.input_val)
                self.assertEqual(test_case.expected_str, str(err))
