import unittest
import numpy as np
import benchmark
import plot


class TesSplitTo(unittest.TestCase):
    sample_bench_results = [
        benchmark.BenchRes(
            inputs=benchmark.BenchInputs(
                subs=["first_bench"],
                variables=[
                    benchmark.BenchVarValue(var_name='first_var',
                                            var_value='some_name'),
                    benchmark.BenchVarValue(
                        var_name='second_var', var_value=1),
                    benchmark.BenchVarValue(
                        var_name='third_var', var_value=1.00),
                ]),
            outputs=benchmark.BenchOutputs(
                runs=161651562, time=7.46, mem_used=0.0, mem_allocs=0),
        ),
        benchmark.BenchRes(
            inputs=benchmark.BenchInputs(
                subs=["first_bench"],
                variables=[
                    benchmark.BenchVarValue(var_name='first_var',
                                            var_value='some_name'),
                    benchmark.BenchVarValue(
                        var_name='second_var', var_value=2),
                    benchmark.BenchVarValue(
                        var_name='third_var', var_value=1.01),
                ]),
            outputs=benchmark.BenchOutputs(
                runs=181651562, time=8.46, mem_used=0.0, mem_allocs=0),
        ),
    ]

    def test_split_to(self):
        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = self.sample_bench_results
        grouped_res: benchmark.GroupedResults = {
            group_vals: [group_res[0], group_res[1]],
        }

        res = plot.split_to(grouped_res, 'second_var', 'time')

        expected_split_res = {
            "first_var = some_name": [
                plot.SplitRes(
                    x=1, y=7.46),
                plot.SplitRes(
                    x=2, y=8.46),
            ]
        }

        self.assertEqual(expected_split_res, res)


class TestBenchResData(unittest.TestCase):
    def test_bench_res_data(self):
        split_res_items = [
            plot.SplitRes(
                x=1, y=7.46),
            plot.SplitRes(
                x=2, y=8.46),
        ]

        plot_data = plot.bench_res_data(split_res_items)
        expected_plot_data = plot.PlotData(
            x=np.array([1, 2]),
            y=np.array([7.46, 8.46]))


if __name__ == '__main__':
    unittest.main()
