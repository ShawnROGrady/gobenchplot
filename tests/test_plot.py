import unittest
import numpy as np
import benchmark
import plot
from collections import namedtuple


class TestPlotData(unittest.TestCase):
    def test_eq(self):
        TestCase = namedtuple(
            'TestCase', 'a b expect_eq')
        test_cases = {
            'equal_cases': TestCase(
                a=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                b=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                expect_eq=True),
            'not_eq': TestCase(
                a=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                b=plot.PlotData(
                    x=np.array([1, 2, 3]),
                    y=np.array([7.46, 8.46, 9.46])),
                expect_eq=False),
            'b_not_plot_data': TestCase(
                a=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                b={
                    'x': [1, 2, 3],
                    'y': [7.46, 8.46, 9.46],
                },
                expect_eq=False),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                is_eq = test_case.a == test_case.b
                self.assertEqual(test_case.expect_eq, is_eq)


class TestBenchResData(unittest.TestCase):
    def test_bench_res_data(self):
        TestCase = namedtuple(
            'TestCase', ['split_res_items', 'expected_plot_data', 'expected_x_type', 'expected_y_type'])
        test_cases = {
            'int_x_float_y': TestCase(
                split_res_items=[
                    benchmark.SplitRes(
                        x=1, y=7.46),
                    benchmark.SplitRes(
                        x=2, y=8.46),
                ],
                expected_plot_data=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                expected_x_type=np.dtype(int),
                expected_y_type=np.dtype(float)),
            'bool_x_float_y': TestCase(
                split_res_items=[
                    benchmark.SplitRes(
                        x=True, y=7.46),
                    benchmark.SplitRes(
                        x=False, y=8.46),
                ],
                expected_plot_data=plot.PlotData(
                    x=np.array([True, False]),
                    y=np.array([7.46, 8.46])),
                expected_x_type=np.dtype(bool),
                expected_y_type=np.dtype(float)),
            'string_x_int_y': TestCase(
                split_res_items=[
                    benchmark.SplitRes(
                        x='foo', y=1),
                    benchmark.SplitRes(
                        x='bar', y=2),
                ],
                expected_plot_data=plot.PlotData(
                    x=np.array(['foo', 'bar'], dtype=np.dtype('<U1')),
                    y=np.array([1, 2])),
                expected_x_type=np.dtype('<U1'),
                expected_y_type=np.dtype(int)),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                plot_data = plot.bench_res_data(test_case.split_res_items)
                self.assertEqual(test_case.expected_plot_data, plot_data)
                self.assertEqual(test_case.expected_x_type,
                                 plot_data.x_type())
                self.assertEqual(test_case.expected_y_type,
                                 plot_data.y_type())
