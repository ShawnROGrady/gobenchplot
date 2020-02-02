import unittest
import numpy as np
import benchmark
import plot


class TestBenchResData(unittest.TestCase):
    def test_bench_res_data(self):
        split_res_items = [
            benchmark.SplitRes(
                x=1, y=7.46),
            benchmark.SplitRes(
                x=2, y=8.46),
        ]

        plot_data = plot.bench_res_data(split_res_items)
        expected_plot_data = plot.PlotData(
            x=np.array([1, 2]),
            y=np.array([7.46, 8.46]))


if __name__ == '__main__':
    unittest.main()
