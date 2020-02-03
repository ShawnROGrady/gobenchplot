import copy
import matplotlib.pyplot as plt
import numpy as np
import typing
import benchmark


class PlotData(typing.NamedTuple):
    x: np.ndarray
    y: np.ndarray

    def x_type(self):
        return self.x[0].dtype

    def y_type(self):
        return self.y[0].dtype


def bench_res_data(bench_results: typing.List[benchmark.SplitRes]) -> PlotData:
    order = len(bench_results)
    x = np.empty(order, dtype=type(bench_results[0].x))
    y = np.empty(order, dtype=type(bench_results[0].y))

    for i, res in enumerate(bench_results):
        x[i] = res.x
        y[i] = res.y

    return PlotData(x=x, y=y)


def plot_line(data: typing.Dict[str, PlotData]):
    ax = plt.gca()
    for label, plot_data in data.items():
        color = next(ax._get_lines.prop_cycler)['color']
        # data points
        plt.plot(plot_data.x, plot_data.y, '.', color=color)
        # best fit - TODO: allow different functions
        uniq_x = np.unique(plot_data.x)
        best_fit_fn = np.poly1d(np.polyfit(plot_data.x, plot_data.y, 1))
        plt.plot(
            uniq_x,
            best_fit_fn(uniq_x),
            label=label,
            color=color)

    plt.legend()


def plot_bar(data: typing.Dict[str, PlotData]):
    ax = plt.gca()
    x = np.arange(len(data))

    y_means = np.empty(len(data))
    for i, plot_data in enumerate(data.values()):
        y_means[i] = np.mean(plot_data.y)

    plt.bar(x, y_means)
    ax.set_xticks(x)
    ax.set_xticklabels(data.keys())


def plot_data(data: typing.Dict[str, PlotData]):
    x_type = list(data.values())[0].x_type()
    y_type = list(data.values())[0].y_type()

    if 'str' in y_type.name or 'bool' in y_type.name:
        raise Exception("unsupported y-axis data type: %s" % (y_type.name))

    if 'str' in x_type.name or 'bool' in x_type.name:
        plot_bar(data)
    else:
        plot_line(data)


def plot_bench(bench: benchmark.Benchmark, group_by: typing.Union[typing.List[str], str], x_name: str, y_name: str = 'time', subs: typing.List = None, filter_vars: typing.List[str] = None):
    if subs is None or len(subs) == 0:
        plt.title(bench.name)
    else:
        plt.title("%s/%s" % (bench.name, "/".join(subs)))

    filter_exprs = benchmark.build_filter_exprs(subs, filter_vars)
    filtered: benchmark.BenchResults = copy.deepcopy(bench.results)
    for expr in filter_exprs:
        filtered = expr(filtered)

    if len(filtered) == 0:
        raise Exception("no results to plot")

    split_res: benchmark.SplitResults = filtered.group_by(
        group_by).split_to(x_name, y_name)

    data: typing.Dict[str, PlotData] = {}
    for label, res in split_res.items():
        data[label] = bench_res_data(res)

    plt.xlabel(x_name)
    plt.ylabel(y_name)

    plot_data(data)

    plt.show()
