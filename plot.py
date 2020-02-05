import copy
import matplotlib.pyplot as plt
import numpy as np
import typing
import benchmark
import inputs

BAR_TYPE = 'bar'
SCATTER_TYPE = 'scatter'
AVG_LINE_TYPE = 'avg_line'
BEST_FIT_LINE_TYPE = 'best_fit_line'


class PlotData(typing.NamedTuple):
    x: np.ndarray
    y: np.ndarray

    def x_type(self):
        return self.x[0].dtype

    def y_type(self):
        return self.y[0].dtype

    def __eq__(self, other):
        if not isinstance(other, PlotData):
            return False

        return np.array_equal(self.x, other.x) and np.array_equal(self.y, other.y)

    def avg_over_x(self) -> 'PlotData':
        uniq_x = np.unique(self.x)
        y_means = np.empty(len(uniq_x), dtype=self.y_type())
        for i, uniq_x_val in enumerate(uniq_x):
            indices = list(
                filter(lambda x: x is not None,
                       map(lambda x:  x[0] if x[1] == uniq_x_val else None,  enumerate(self.x))))

            y_vals = np.empty(len(indices), dtype=self.y_type())
            for j, index in enumerate(indices):
                y_vals[j] = self.y[index]
            y_means[i] = np.mean(y_vals)

        return PlotData(x=uniq_x, y=y_means)


def bench_res_data(bench_results: typing.List[benchmark.SplitRes]) -> PlotData:
    order = len(bench_results)
    x = np.empty(order, dtype=type(bench_results[0].x))
    y = np.empty(order, dtype=type(bench_results[0].y))

    for i, res in enumerate(bench_results):
        x[i] = res.x
        y[i] = res.y

    return PlotData(x=x, y=y)


def plot_scatter(data: typing.Dict[str, PlotData], include_label):
    for label, plot_data in data.items():
        if include_label:
            plt.plot(plot_data.x, plot_data.y, '.', label=label)
        else:
            plt.plot(plot_data.x, plot_data.y, '.')


def plot_avg_line(data: typing.Dict[str, PlotData], include_label):
    for label, plot_data in data.items():
        uniq_x, y_means = plot_data.avg_over_x()
        if include_label:
            plt.plot(uniq_x, y_means, label=label)
        else:
            plt.plot(uniq_x, y_means)


def plot_best_fit_line(data: typing.Dict[str, PlotData], include_label):
    for label, plot_data in data.items():
        uniq_x = np.unique(plot_data.x)
        best_fit_fn = np.poly1d(np.polyfit(plot_data.x, plot_data.y, 1))
        if include_label:
            plt.plot(
                uniq_x,
                best_fit_fn(uniq_x),
                label=label)
        else:
            plt.plot(
                uniq_x,
                best_fit_fn(uniq_x))


def get_bar_spacing_adjustment(plotnum: int, num_plots: int) -> typing.Union[int, float]:
    if num_plots == 0:
        return 0
    # produce even spacing without colliding with others
    return (1/num_plots) * (2*plotnum - (num_plots-1))


def get_bar_widths(uniq_x: np.ndarray, num_plots: int)->typing.Union[float, np.ndarray]:
    if non_numeric_dtype(uniq_x[0].dtype):
        # for non numeric plots we can control the spacing so just use default width
        return 0.8

    # NOTE: this is assuming each of the num_plots has the same uniq_x
    base_width = 0.8/num_plots
    if len(uniq_x) == 1:
        return base_width

    widths = np.empty(len(uniq_x), dtype=np.float64)
    for index, x in np.ndenumerate(uniq_x):
        i = index[0]  # just dealing w/ 1D arrays
        if i == 0:
            continue
        # just enough spacing
        if i >= 2:
            widths[i-1] = min(base_width * (x - uniq_x[i-1]),
                              base_width * (uniq_x[i-1] - uniq_x[i-2]))
        else:
            widths[i-1] = base_width * (x - uniq_x[i-1])
    widths[len(uniq_x)-1] = widths[len(uniq_x)-2]
    return widths


def plot_bar(data: typing.Dict[str, PlotData], include_label):
    x_type = list(data.values())[0].x_type()
    ax = plt.gca()
    if non_numeric_dtype(x_type):
        x = np.arange(len(data))
        y_means = np.empty(len(data))
        for i, plot_data in enumerate(data.values()):
            y_means[i] = np.mean(plot_data.y)

        if include_label:
            # TODO come up with an actual label, just doing this to prevent legend() error
            plt.bar(x, y_means, label='')
        else:
            plt.bar(x, y_means)
        ax.set_xticks(x)
        ax.set_xticklabels(data.keys())
        return
    else:
        num_plots = len(data)
        # TODO: this is a guestimate, should be determined programatically
        i = 0
        for label, plot_data in data.items():
            uniq_x, y_means = plot_data.avg_over_x()
            widths = get_bar_widths(uniq_x, num_plots)
            adjustment = get_bar_spacing_adjustment(i, num_plots)
            if include_label:
                plt.bar(uniq_x-widths*adjustment, y_means, widths, label=label)
            else:
                plt.bar(uniq_x-widths*adjustment, y_means, widths)
            i += 1
            ax.set_xticks(uniq_x)
            ax.set_xticklabels(uniq_x)


def plot_fn_from_type(plots: typing.Optional[typing.Union[typing.List[str], str]]):
    if plots is None:
        return None

    if isinstance(plots, list):
        fn = list(map(lambda x: plot_fn_from_type(x), plots))
        return fn

    if plots == BAR_TYPE:
        return plot_bar
    elif plots == SCATTER_TYPE:
        return plot_scatter
    elif plots == AVG_LINE_TYPE:
        return plot_avg_line
    elif plots == BEST_FIT_LINE_TYPE:
        return plot_best_fit_line
    else:
        raise inputs.InvalidInputError(
            'unknown plot type',
            inputs.PLOTS_NAME,
            input_val=plots)
    return


def non_numeric_dtype(dtype) -> bool:
    if ('str' in dtype.name) or ('bool' in dtype.name) or ('bytes' in dtype.name):
        return True
    return False


def build_plot_fn(
        data: typing.Dict[str, PlotData],
        x_name: str, y_name: str = 'time',
        plots=None):
    x_type = list(data.values())[0].x_type()
    y_type = list(data.values())[0].y_type()

    if non_numeric_dtype(y_type):
        raise inputs.InvalidInputError(
            "unsupported data type '%s'" % (y_type.name),
            inputs.Y_NAME,
            input_val=y_name)

    if non_numeric_dtype(x_type):
        if plots is None or plots == BAR_TYPE:
            return plot_fn_from_type(BAR_TYPE)
        elif (isinstance(plots, str) and plots == BAR_TYPE) or (isinstance(plots, list) and BAR_TYPE in plots):
            return plot_fn_from_type(plots)
        else:
            raise inputs.InvalidInputError(
                "unsupported data type '%s' for plot type '%s'" % (
                    x_type.name, plots),
                inputs.X_NAME,
                input_val=x_name)
    else:
        if plots is None:
            return plot_fn_from_type([SCATTER_TYPE, AVG_LINE_TYPE])
        else:
            return plot_fn_from_type(plots)


def run_plot_fns(data: typing.Dict[str, PlotData], plot_fns):
    # can't show average bar on same figure as others
    non_avg_bar_fns = list(
        filter(lambda x: x.__name__ != plot_bar.__name__, plot_fns))
    if len(non_avg_bar_fns) != len(plot_fns):
        if len(non_avg_bar_fns) != 0:
            plt.subplot(212)
        for plot_fn in plot_fns:
            if plot_fn.__name__ == plot_bar.__name__:
                plot_fn(data, include_label=True)
                break
        if len(non_avg_bar_fns) != 0:
            plt.subplot(211)
    ax = plt.gca()
    for i, fn in enumerate(non_avg_bar_fns):
        ax.set_prop_cycle(None)
        if i == 0:
            fn(data, include_label=True)
        else:
            fn(data, include_label=False)


def plot_data(data: typing.Dict[str, PlotData], x_name: str, y_name: str = 'time', plots=None):
    plot_fn = build_plot_fn(data, x_name, y_name=y_name, plots=plots)
    # NOTE: for now assuming all plots can be shown on figure
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    if isinstance(plot_fn, list):
        run_plot_fns(data, plot_fn)
    else:
        plot_fn(data, include_label=True)


def plot_bench(
        bench: benchmark.Benchmark,
        group_by: typing.Union[typing.List[str], str],
        x_name: str, y_name: str = 'time',
        subs: typing.List = None,
        filter_vars: typing.List[str] = None,
        plots=None):

    filter_exprs = benchmark.build_filter_exprs(subs, filter_vars)
    filtered: benchmark.BenchResults = copy.deepcopy(bench.results)
    for expr in filter_exprs:
        filtered = expr(filtered)

    if len(filtered) == 0:
        raise inputs.InvalidInputError(
            "no results remain",
            [inputs.FILTER_BY_NAME, inputs.SUBS_NAME],
            [filter_vars, subs])

    split_res: benchmark.SplitResults = filtered.group_by(
        group_by).split_to(x_name, y_name)

    data: typing.Dict[str, PlotData] = {}
    for label, res in split_res.items():
        data[label] = bench_res_data(res)

    if subs is None or len(subs) == 0:
        plt.title(bench.name)
    else:
        plt.title("%s/%s" % (bench.name, "/".join(subs)))

    plot_data(data, x_name, y_name=y_name, plots=plots)
    plt.legend()
    plt.show()
