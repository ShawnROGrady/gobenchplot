import sys
import argparse
import gobenchplot.plot as plot
import gobenchplot.benchmark as benchmark
import gobenchplot.inputs as inputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Plots the results of a go benchmark')
    parser.add_argument(
        'file',
        nargs='?',
        help=(
            "file containing bench results\n" +
            "if empty or '-' stdin is assumed"))
    parser.add_argument(
        '--bench',
        dest='bench',
        nargs='?',
        help="the name of the benchmark to plot")
    parser.add_argument(
        '--%s' % (inputs.X_NAME),
        dest='x',
        nargs='?',
        help="the name of the x-axis variable (an input to the benchmark)")
    available_y_vals = benchmark.BenchOutputs.__dict__['_fields']
    parser.add_argument(
        '--%s' % (inputs.Y_NAME),
        dest='y',
        nargs='?',
        default='time',
        help=(
            "the name of the y-axis variable. " +
            "One of: %s" % (', '.join(available_y_vals))))
    parser.add_argument(
        '--%s' % (inputs.GROUP_BY_NAME),
        dest='group_by',
        nargs='+',
        help='the variables to group results by (an input to the benchmark)')
    parser.add_argument(
        '--%s' % (inputs.SUBS_NAME),
        dest='subs',
        nargs='+',
        help="the sub-benchmark(s) to plot")
    parser.add_argument(
        '--%s' % (inputs.FILTER_BY_NAME),
        dest='filter_vars',
        nargs='+',
        help=(
            'the variables to filter results by. ' +
            'Form: \'var_name==var_value\'. ' +
            'Available comparisons: %s' % (', '.join([
                str(benchmark.Comparison.EQ),
                str(benchmark.Comparison.NE),
                str(benchmark.Comparison.LT),
                str(benchmark.Comparison.GT),
                str(benchmark.Comparison.LE),
                str(benchmark.Comparison.GE),
            ])))),
    parser.add_argument(
        '--%s' % (inputs.PLOTS_NAME),
        dest='plots',
        nargs='+',
        help=(
            'which plots to show (options: \'%s\'). ' % ('\', \''.join([
                plot.BAR_TYPE,
                plot.SCATTER_TYPE,
                plot.AVG_LINE_TYPE,
                plot.BEST_FIT_LINE_TYPE])) +
            'Defaults to \'%s\' if x corresponds to a non numeric type, ' % (
                plot.BAR_TYPE) +
            '[\'%s\'] otherwise' % ('\', \''.join([
                plot.SCATTER_TYPE,
                plot.AVG_LINE_TYPE,
            ]))))

    args = parser.parse_args()

    suite: benchmark.BenchSuite
    if args.file is None or args.file == "" or args.file == "-":
        suite = benchmark.parse_bench_output(sys.stdin)
    else:
        with open(args.file) as f:
            suite = benchmark.parse_bench_output(f)

    if args.bench is not None:
        bench = suite.get_benchmark(args.bench)
        if bench is None:
            print("no bench '%s' found" % (args.bench), file=sys.stderr)
            return 1

        else:
            try:
                plot.plot_bench(bench, args.group_by, args.x, y_name=args.y,
                                subs=args.subs, filter_vars=args.filter_vars,
                                plots=args.plots)
            except inputs.InvalidInputError as e:
                print(str(e), file=sys.stderr)
                return 1
    else:
        # TODO: should just plot all benchmarks
        print("need to provide benchmark name", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
