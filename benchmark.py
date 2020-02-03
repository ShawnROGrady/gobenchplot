import typing
import json
from functools import singledispatch
import re
import inputs


ResValue = typing.Union[int, str, float, bool]


class BenchVarValue(typing.NamedTuple):
    var_name: str
    var_value: ResValue

    def __str__(self):
        return "{} = {}".format(self.var_name, self.var_value)

    def __hash__(self):
        return hash((self.var_name, self.var_value))

    def __eq__(self, other):
        if not isinstance(other, BenchVarValue):
            return False
        return self.var_name == other.var_name and self.var_value == other.var_value


class BenchVarValues(typing.List[BenchVarValue]):
    def __init__(self, values: typing.List[BenchVarValue]):
        self._values = values

    def __str__(self):
        str_values: typing.List[str] = [str(value) for value in self._values]
        return ", ".join(str_values)

    def __hash__(self):
        return hash(tuple(self._values))

    def __contains__(self, other) -> bool:
        return other in self._values


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


SplitResults = typing.Dict[str, typing.List[SplitRes]]


class GroupedResults(dict):
    def __init__(self, initdata: typing.Dict[BenchVarValues, 'BenchResults'] = None):
        if initdata is None:
            dict.__init__(self, {})
        else:
            dict.__init__(self, initdata)

    def __getitem__(self, key: BenchVarValues):
        return dict.__getitem__(self, key)

    def __setitem__(self, key: BenchVarValues, val: 'BenchResults'):
        dict.__setitem__(self, key, val)

    def items(self):
        return dict.items(self)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def filtered_by_subs(self, subs: typing.List[str]) -> 'GroupedResults':
        filtered: typing.Dict[BenchVarValues, 'BenchResults'] = {}
        for k, v in self.items():
            filtered_results: BenchResults
            if isinstance(v, BenchResults):
                filtered_results = v.filtered_by_subs(subs)
            else:
                filtered_results = BenchResults(v).filtered_by_subs(subs)

            if len(filtered_results) != 0:
                filtered[k] = filtered_results

        return GroupedResults(initdata=filtered)

    def filtered_by_var_value(self, value: BenchVarValue) -> 'GroupedResults':
        filtered: typing.Dict[BenchVarValues, 'BenchResults'] = {}
        for k, v in self.items():
            filtered_results: BenchResults
            if isinstance(v, BenchResults):
                filtered_results = v.filtered_by_var_value(value)
            else:
                filtered_results = BenchResults(v).filtered_by_var_value(value)

            if len(filtered_results) != 0:
                filtered[k] = filtered_results

        return GroupedResults(initdata=filtered)

    def split_to(self, x_name: str, y_name: str) -> SplitResults:
        split_results: SplitResults = {}
        for var_value, var_results in dict.items(self):
            for res in var_results:
                x_var: typing.Optional[BenchVarValue] = None
                for var in res.inputs.variables:
                    if var.var_name == x_name:
                        x_var = var
                        break

                if x_var is None:
                    raise inputs.InvalidInputError(
                        'no variable with that name', inputs.X_NAME, input_val=x_name)
                if not str(var_value) in split_results:
                    split_results[str(var_value)] = []

                try:
                    y_val = getattr(res.outputs, y_name)
                    split_results[str(var_value)].append(
                        SplitRes(x=x_var.var_value, y=y_val))
                except AttributeError:
                    raise inputs.InvalidInputError(
                        'no output with that name', inputs.Y_NAME, input_val=y_name)
        return split_results


class BenchResults:
    def __init__(self, initdata: typing.List[BenchRes]):
        self._data = initdata

    def __getitem__(self, key: int) -> BenchRes:
        return self._data[key]

    def __setitem__(self, key: int, val: BenchRes):
        self._data[key] = val

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()

    def __contains__(self, item: BenchRes):
        return self._data.__contains__(item)

    def append(self, item: BenchRes):
        return self._data.append(item)

    def __delitem__(self, key: int):
        self._data.__delitem__(key)

    def list(self) -> typing.List[BenchRes]:
        return self._data

    def __eq__(self, other) -> bool:
        if isinstance(other, list):
            return other == self._data
        if isinstance(other, BenchResults):
            return list(other) == self._data
        return False

    def get_var_names(self) -> typing.List[str]:
        all_v_names: typing.List[str] = []
        for res in self._data:
            v_names = res.get_var_names()
            for v_name in v_names:
                if not v_name in all_v_names:
                    all_v_names.append(v_name)
        return all_v_names

    def get_subs(self) -> typing.Optional[typing.List[str]]:
        all_subs: typing.Optional[typing.List[str]] = None
        for res in self._data:
            subs = res.get_subs()
            if subs is None:
                continue
            for sub in subs:
                if all_subs is None:
                    all_subs = []
                if not sub in all_subs:
                    all_subs.append(sub)
        return all_subs

    def filtered_by_subs(self, subs: typing.List[str]) -> 'BenchResults':
        filtered_results: typing.List[BenchRes]
        filtered_results = list(
            filter(lambda x: x.inputs.subs == subs, self._data))
        return BenchResults(filtered_results)

    def filtered_by_var_value(self, value: BenchVarValue) -> 'BenchResults':
        filtered_results: typing.List[BenchRes]
        filtered_results = list(
            filter(lambda x: value in x.inputs.variables, self._data))
        return BenchResults(filtered_results)

    def group_by(
            self,
            group_by: typing.Union[typing.List[str], str]) -> GroupedResults:
        all_var_names = self.get_var_names()
        if len(self._data) == 0:
            return GroupedResults()

        # TODO: validate subs
        if isinstance(group_by, typing.List):
            for group_var_name in group_by:
                if not group_var_name in all_var_names:
                    raise inputs.InvalidInputError(
                        'no variable with that name', inputs.GROUP_BY_NAME, input_val=group_var_name)
        elif isinstance(group_by, str):
            if not group_by in all_var_names:
                raise inputs.InvalidInputError(
                    'no variable with that name', inputs.GROUP_BY_NAME, input_val=group_by)
        else:
            raise inputs.InvalidInputError(
                'invalid type %s' % (type(group_by)), inputs.GROUP_BY_NAME, input_val=group_by)

        grouped_results: GroupedResults = GroupedResults()

        for res in self._data:
            group_vals: BenchVarValues
            if isinstance(group_by, typing.List):
                group_vals = BenchVarValues(list(
                    filter(lambda x: x.var_name in group_by, res.inputs.variables)))
            else:
                group_vals = BenchVarValues(list(
                    filter(lambda x: x.var_name == group_by, res.inputs.variables)))
            if not group_vals in grouped_results:
                grouped_results[group_vals] = BenchResults([res])
            else:
                grouped_results[group_vals].append(res)

        return grouped_results


class Benchmark:
    def __init__(self, name: str):
        self.name = name
        self._results: BenchResults = BenchResults([])

    def add_result(self, result: BenchRes):
        self._results.append(result)

    def get_var_names(self) -> typing.List[str]:
        return self._results.get_var_names()

    def get_subs(self) -> typing.Optional[typing.List[str]]:
        return self._results.get_subs()

    @property
    def results(self) -> BenchResults:
        return self._results


@singledispatch
def filter_results(filter_by, res: typing.Union[GroupedResults, BenchResults]) -> typing.Union[GroupedResults, BenchResults]:
    return res


@filter_results.register(BenchVarValue)
def filter_by_var_value(filter_by: BenchVarValue, res: typing.Union[GroupedResults, BenchResults]) -> typing.Union[GroupedResults, BenchResults]:
    return res.filtered_by_var_value(filter_by)


@filter_results.register(list)
def filter_by_subs(filter_by: typing.List[str], res: typing.Union[GroupedResults, BenchResults]) -> typing.Union[GroupedResults, BenchResults]:
    return res.filtered_by_subs(filter_by)


def filter_expr(filter_by):
    def filter_fn(res):
        return filter_results(filter_by, res)
    return filter_fn


def build_filter_exprs(
        subs: typing.Optional[typing.List[str]],
        var_values: typing.Optional[typing.List[str]]):

    exprs = []
    if subs is not None and len(subs) != 0:
        exprs.append(filter_expr(subs))

    if var_values is not None and len(var_values) != 0:
        for value in var_values:
            split_val = value.replace(" ", "").split("=")
            if len(split_val) != 2:
                raise inputs.InvalidInputError(
                    "not of expected form 'var_name=var_value'",
                    inputs.FILTER_BY_NAME, input_val=value)
            var = BenchVarValue(
                var_name=split_val[0], var_value=var_value(split_val[1]))
            exprs.append(filter_expr(var))
    return exprs


bench_info_expr = re.compile(r'^(Benchmark.+?)(?:\-[0-9])?\s+$')


class BenchInfo(typing.NamedTuple):
    name: str
    inputs: BenchInputs


def var_value(parsed_val: str) -> ResValue:
    possible_types = [int, float]
    for _type in possible_types:
        try:
            res_value = _type(parsed_val)
            return res_value
        except ValueError:
            continue
    normalized = parsed_val.lower().replace(" ", "")
    if normalized == "true":
        return True
    elif normalized == "false":
        return False
    else:
        return parsed_val


class ParseBenchmarkError(Exception):
    def __init__(self, line: str, reason: str):
        Exception.__init__(
            self, "%s. Output line = %s" % (reason, line))
        self.line = line
        self.reason = reason


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
            raise ParseBenchmarkError(
                line, "line didn't match regular expression %s" % (bench_info_expr))

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
            raise ParseBenchmarkError(
                line, "no time found in benchmark output")

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
                raise ParseBenchmarkError(
                    line,
                    "bench outputs provided before bench info")

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
