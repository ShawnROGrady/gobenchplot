import matplotlib.pyplot as plt
import numpy as np
import typing
import benchmark


class SplitRes(typing.NamedTuple):
    x: benchmark.ResValue
    y: benchmark.ResValue


SplitResults = typing.Dict[str, typing.List[SplitRes]]


def split_to(grouped_results: benchmark.GroupedResults, x_name: str, y_name: str) -> SplitResults:
    split_results: SplitResults = {}
    for var_value, var_results in grouped_results.items():
        for res in var_results:
            x_var: typing.Optional[benchmark.BenchVarValue] = None
            for var in res.inputs.variables:
                if var.var_name == x_name:
                    x_var = var
                    break

            if x_var is None:
                raise Exception(
                    "%s is not a defined variable of the benchmark" % (x_name))
            if not str(var_value) in split_results:
                split_results[str(var_value)] = []

            try:
                y_val = getattr(res.outputs, y_name)
                split_results[str(var_value)].append(
                    SplitRes(x=x_var.var_value, y=y_val))
            except AttributeError:
                raise Exception(
                    "%s is not a defined output of the benchmark" % (y_name))
    return split_results


class PlotData(typing.NamedTuple):
    x: np.ndarray
    y: np.ndarray


def bench_res_data(bench_results: typing.List[SplitRes]) -> PlotData:
    order = len(bench_results)
    x = np.empty(order)
    y = np.empty(order)

    for i, res in enumerate(bench_results):
        x[i] = res.x
        y[i] = res.y

    return PlotData(x=x, y=y)


def plot_bench(bench: benchmark.Benchmark, group_by: typing.Union[typing.List[str], str], x_name: str, y_name: str = 'time', subs: typing.List = []):
    split_res: SplitResults = split_to(
        bench.grouped_results(group_by, subs),
        x_name, y_name)

    if len(subs) == 0:
        plt.title(bench.name)
    else:
        plt.title("%s/%s" % (bench.name, "/".join(subs)))

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
