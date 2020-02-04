import unittest
import numpy as np
import benchmark
import inputs
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

    def test_avg_over_x(self):
        TestCase = namedtuple(
            'TestCase', 'data expected_averaged')
        test_cases = {
            'no_work_needed': TestCase(
                data=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46])),
                expected_averaged=plot.PlotData(
                    x=np.array([1, 2]),
                    y=np.array([7.46, 8.46]))),
            '3_duplicates': TestCase(
                data=plot.PlotData(
                    x=np.array([1, 1, 1, 2, 2, 2, 3, 3, 3]),
                    y=np.array([1, 2, 3, 1, 2, 3, 1, 2, 3])),
                expected_averaged=plot.PlotData(
                    x=np.array([1, 2, 3]),
                    y=np.array([2, 2, 2]))),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                avged = test_case.data.avg_over_x()
                self.assertEqual(test_case.expected_averaged, avged)


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


class TestBuildPlotFn(unittest.TestCase):
    def test_build_plot_fn(self):
        TestCase = namedtuple(
            'TestCase', 'data x_name y_name plots expected_plotfn_names')
        test_cases = {
            'numeric_x_no_plots_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array([1, 2]),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots=None,
                expected_plotfn_names=[plot.plot_scatter.__name__, plot.plot_avg_line.__name__]),
            'numeric_x_1_plot_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array([1, 2]),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots=plot.BEST_FIT_LINE_TYPE,
                expected_plotfn_names=[plot.plot_best_fit_line.__name__]),
            'non_numeric_x_no_plots_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array(['foo', 'bar'], dtype=np.dtype('<U1')),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots=None,
                expected_plotfn_names=[plot.plot_bar.__name__]),
            'non_numeric_x_1_plot_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array(['foo', 'bar'], dtype=np.dtype('<U1')),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots=plot.BAR_TYPE,
                expected_plotfn_names=[plot.plot_bar.__name__]),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                plot_fn = plot.build_plot_fn(
                    test_case.data,
                    test_case.x_name, y_name=test_case.y_name,
                    plots=test_case.plots)
                plot_fn_names = []
                if isinstance(plot_fn, list):
                    plot_fn_names = list(map(lambda x: x.__name__, plot_fn))
                else:
                    plot_fn_names = [plot_fn.__name__]
                self.assertEqual(
                    test_case.expected_plotfn_names, plot_fn_names)

    def test_build_plot_fn_raises(self):
        TestCase = namedtuple(
            'TestCase', 'data x_name y_name plots expected_err_type')
        test_cases = {
            'numeric_x_invalid_plot_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array([1, 2]),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots="unknown",
                expected_err_type=inputs.InvalidInputError),
            'non_numeric_x_unsupported_plot_type_specified': TestCase(
                data={
                    "first_var = some_name": plot.PlotData(
                        x=np.array(['foo', 'bar'], dtype=np.dtype('<U1')),
                        y=np.array([7.46, 8.46])),
                },
                x_name='first_var',
                y_name='time',
                plots=plot.AVG_LINE_TYPE,
                expected_err_type=inputs.InvalidInputError),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                with self.assertRaises(test_case.expected_err_type):
                    plot_fn = plot.build_plot_fn(
                        test_case.data,
                        test_case.x_name, y_name=test_case.y_name,
                        plots=test_case.plots)
