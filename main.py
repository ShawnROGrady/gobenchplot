import sys
import argparse
import typing
import plot
import benchmark


def plot_bench(bench: benchmark.Benchmark, group_by: typing.Union[typing.List[str], str], x_name: str, y_name: str = 'time', subs: typing.List = []):
    plot.plot_bench(bench, group_by, x_name, y_name, subs)


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Plots the results of a go benchmark')
    parser.add_argument(
        'file',
        nargs='?',
        help="file containing bench results (if empty or '-' stdin is assumed)")
    parser.add_argument(
        '--bench',
        dest='bench',
        nargs='?',
        help="the name of the benchmark to plot")
    parser.add_argument(
        '--x',
        dest='x',
        nargs='?',
        help="the name of the x-axis variable (an input to the benchmark)")
    available_y_vals = benchmark.BenchOutputs.__dict__['_fields']
    parser.add_argument(
        '--y',
        dest='y',
        nargs='?',
        default='time',
        help="the name of the y-axis variable (one of: %s)" % (', '.join(available_y_vals)))
    parser.add_argument(
        '--group-by',
        dest='group_by',
        nargs='+',
        help='the variables to group results by (an input to the benchmark)')
    parser.add_argument(
        '--subs',
        dest='subs',
        nargs='+',
        help="the sub-benchmark(s) to plot")

    args = parser.parse_args()

    suite = benchmark.BenchSuite()
    if args.file is None or args.file == "" or args.file == "-":
        for line in sys.stdin:
            suite.readline(line)
    else:
        with open(args.file) as f:
            for line in f:
                suite.readline(line)

    if args.bench is not None:
        bench = suite.get_benchmark(args.bench)
        if bench is None:
            print("no bench '%s' found" % (args.bench), file=sys.stderr)
            return 1

        if args.subs is not None:
            plot_bench(bench, args.group_by, args.x,
                       y_name=args.y, subs=args.subs)
        else:
            plot_bench(bench, args.group_by, args.x, y_name=args.y)
    else:
        # TODO: should just plot all benchmarks
        print("need to provide benchmark name", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
