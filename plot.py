import matplotlib.pyplot as plt
import numpy as np
import typing
import benchmark


class PlotData(typing.NamedTuple):
    x: np.ndarray
    y: np.ndarray


def bench_res_data(bench_results: typing.List[benchmark.SplitRes]) -> PlotData:
    order = len(bench_results)
    x = np.empty(order)
    y = np.empty(order)

    for i, res in enumerate(bench_results):
        x[i] = res.x
        y[i] = res.y

    return PlotData(x=x, y=y)


def plot_bench(bench: benchmark.Benchmark, group_by: typing.Union[typing.List[str], str], x_name: str, y_name: str = 'time', subs: typing.List = []):
    split_res = bench.split_to(x_name, y_name, group_by, subs)

    ax = plt.gca()
    for label, res in split_res.items():
        plot_data = bench_res_data(res)
        color = next(ax._get_lines.prop_cycler)['color']
        # data points
        plt.plot(plot_data.x, plot_data.y, '.', color=color)
        # best fit
        uniq_x = np.unique(plot_data.x)
        best_fit_fn = np.poly1d(np.polyfit(plot_data.x, plot_data.y, 1))
        plt.plot(
            uniq_x,
            best_fit_fn(uniq_x),
            label=label,
            color=color)
        plt.xlabel(x_name)
        plt.ylabel(y_name)
    plt.legend()
    plt.show()
