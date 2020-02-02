import typing
import json
import re


ResValue = typing.Union[int, str, float]


class BenchVarValue(typing.NamedTuple):
    var_name: str
    var_value: typing.Union[int, str, float]

    def __str__(self):
        return "{} = {}".format(self.var_name, self.var_value)

    def __hash__(self):
        return hash((self.var_name, self.var_value))

    def __eq__(self, other):
        return self.var_name == other.var_name and self.var_value == other.var_value


class BenchVarValues(typing.List[BenchVarValue]):
    def __init__(self, values: typing.List[BenchVarValue]):
        self._values = values

    def __str__(self):
        str_values: typing.List[str] = [str(value) for value in self._values]
        return ", ".join(str_values)

    def __hash__(self):
        return hash(tuple(self._values))


class BenchInputs(typing.NamedTuple):
    variables: typing.List[BenchVarValue]
    subs: typing.Optional[typing.List[str]]


time_op_expr = re.compile(r'\s+([0-9\.]+) ns\/op')
allocs_op_expr = re.compile(r'\s+([0-9]+) allocs\/op')
used_op_expr = re.compile(r'\s+([0-9\.]+) ([A-Z]?)B\/op')


class BenchOutputs(typing.NamedTuple):
    runs: int
    time: float  # duration per op (expressed in nanoseconds)
    mem_allocs: typing.Optional[int]  # allocs per op
    mem_used: typing.Optional[float]  # B per op


class BenchRes(typing.NamedTuple):
    inputs: BenchInputs
    outputs: BenchOutputs

    def get_var_names(self) -> typing.List[str]:
        return list(map(lambda x: x.var_name, self.inputs.variables))

    def get_subs(self) -> typing.Optional[typing.List[str]]:
        return self.inputs.subs


class SplitRes(typing.NamedTuple):
    x: ResValue
    y: ResValue


class Benchmark:
    def __init__(self, name: str):
        self.name = name
        self._results: typing.List[BenchRes] = []

    def add_result(self, result: BenchRes):
        self._results.append(result)

    def get_var_names(self) -> typing.List[str]:
        if len(self._results) == 0:
            raise Exception("no results")
        all_v_names: typing.List[str] = []
        for res in self._results:
            v_names = res.get_var_names()
            for v_name in v_names:
                if not v_name in all_v_names:
                    all_v_names.append(v_name)
        return all_v_names

    def get_subs(self) -> typing.Optional[typing.List[str]]:
        if len(self._results) == 0:
            raise Exception("no results")
        all_subs: typing.Optional[typing.List[str]] = None
        for res in self._results:
            subs = res.get_subs()
            if subs is None:
                continue
            for sub in subs:
                if all_subs is None:
                    all_subs = []
                if not sub in all_subs:
                    all_subs.append(sub)
        return all_subs

    def split_to(self, x_name: str, y_name: str, group_by: typing.Union[typing.List[str], str], subs: typing.List[str] = []) -> typing.Dict[str, typing.List[SplitRes]]:
        if len(self._results) == 0:
            raise Exception("no results")
        all_subs = self.get_subs()
        if all_subs is not None and (len(subs) != len(all_subs)):
            raise Exception(
                "unexpected number of subs received (expected = %d, provided = %d)" % (len(all_subs), len(subs)))
        # TODO: possibly raise exception if no subs present but provided

        all_var_names = self.get_var_names()
        if isinstance(group_by, typing.List):
            for group_var_name in group_by:
                if not group_var_name in all_var_names:
                    raise Exception(
                        "%s is not a defined variable of the benchmark" % (group_var_name))
        elif isinstance(group_by, str):
            if not group_by in all_var_names:
                raise Exception(
                    "%s is not a defined variable of the benchmark" % (group_by))
        else:
            raise Exception("invalid group_by = {}".format(group_by))

        results: typing.List[BenchRes]
        if len(subs) != 0:
            results = list(
                filter(lambda x: x.inputs.subs == subs, self._results))
        else:
            results = self._results

        split_results: typing.Dict[str, typing.List[SplitRes]] = {}

        grouped_results: typing.Dict[BenchVarValues,
                                     typing.List[BenchRes]] = {}

        for res in results:
            group_vals: BenchVarValues
            if isinstance(group_by, typing.List):
                group_vals = BenchVarValues(list(
                    filter(lambda x: x.var_name in group_by, res.inputs.variables)))
            else:
                group_vals = BenchVarValues(list(
                    filter(lambda x: x.var_name == group_by, res.inputs.variables)))
            if not group_vals in grouped_results:
                grouped_results[group_vals] = [res]
            else:
                grouped_results[group_vals].append(res)

        for var_value, var_results in grouped_results.items():
            for res in var_results:
                x_var: typing.Optional[BenchVarValue] = None
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


bench_info_expr = re.compile(r'^(Benchmark.+?)(?:\-[0-9])?\s+$')


class BenchInfo(typing.NamedTuple):
    name: str
    inputs: BenchInputs


def var_value(parsed_val: str) -> typing.Union[str, int, float]:
    try:
        int_val = int(parsed_val)
        return int_val
    except ValueError:
        try:
            float_val = float(parsed_val)
            return float_val
        except ValueError:
            return parsed_val


def parse_out_line(line: str) -> typing.Optional[
        typing.Union[BenchInfo, BenchOutputs]]:
    bench_line = json.loads(line)
    if "Output" not in bench_line:
        return None

    output_info = bench_line["Output"]
    if output_info.startswith("Benchmark"):
        # BenchInfo
        m = bench_info_expr.match(output_info)
        if not m:
            raise Exception("unexpected bench info")

        full_name = m[1]
        name: str = ''
        subs: typing.Optional[typing.List[str]] = None
        variables: typing.List[BenchVarValue] = []

        for i, value in enumerate(full_name.split('/')):
            if i == 0:
                name = value
                continue
            split_val = value.split("=")
            if len(split_val) != 2:
                if subs is None:
                    subs = [value]
                else:
                    subs.append(value)
            else:
                variables.append(
                    BenchVarValue(var_name=split_val[0], var_value=var_value(split_val[1])))
        return BenchInfo(
            name=name,
            inputs=BenchInputs(variables=variables, subs=subs))
    elif output_info.lstrip()[0].isdigit():
        # BenchOutputs
        vals = output_info.split('\t')
        runs: int = int(vals[0])
        time: typing.Optional[float] = None
        mem_allocs: typing.Optional[int] = None
        mem_used: typing.Optional[float] = None

        for i, value in enumerate(vals, start=0):
            if i == 0:
                continue
            if time is None:
                m = time_op_expr.match(value)
                if m:
                    time = float(m[1])
            elif mem_used is None:
                m = used_op_expr.match(value)
                if m:
                    mem_used = float(m[1])
            elif mem_allocs is None:
                m = allocs_op_expr.match(value)
                if m:
                    mem_allocs = int(m[1])
        if time is not None:
            return BenchOutputs(
                runs=runs, time=time, mem_allocs=mem_allocs, mem_used=mem_used)
        else:
            raise Exception("no time found")

    return None


class BenchSuite:
    def __init__(self):
        self._benchmarks: typing.List[Benchmark] = []
        self._current_bench: typing.Optional[BenchInfo] = None

    def readline(self, line: str):
        res = parse_out_line(line)
        if res is None:
            return
        if isinstance(res, BenchInfo):
            self._current_bench = res
            return
        if isinstance(res, BenchOutputs):
            if self._current_bench is None:
                raise Exception("bench outputs provided before bench info")

            existing_bench = self.get_benchmark(self._current_bench.name)
            if existing_bench:
                existing_bench.add_result(BenchRes(
                    inputs=self._current_bench.inputs,
                    outputs=res))
            else:
                new_bench = Benchmark(self._current_bench.name)
                new_bench.add_result(BenchRes(
                    inputs=self._current_bench.inputs,
                    outputs=res))
                self._benchmarks.append(new_bench)
            self._current_bench = None

    def get_benchmark(self, name) -> typing.Optional[Benchmark]:
        for bench in self._benchmarks:
            if bench.name == name:
                return bench

        return None

    def get_benchmarks(self) -> typing.List[Benchmark]:
        return self._benchmarks
