import typing
import json
import re


class BenchVarValue(typing.NamedTuple):
    var_name: str
    var_value: typing.Union[int, str, float]


class BenchInputs(typing.NamedTuple):
    variables: typing.List[BenchVarValue]
    labels: typing.Optional[typing.List[str]]


time_op_expr = re.compile(r'\s+([0-9\.]+) ([a-z])s\/op')
allocs_op_expr = re.compile(r'\s+([0-9]+) allocs\/op')
used_op_expr = re.compile(r'\s+([0-9\.]+) ([A-Z]?)B\/op')


class BenchOutputs(typing.NamedTuple):
    runs: int
    time: float  # duration per op (expressed in seconds)
    mem_allocs: typing.Optional[int]  # allocs per op
    mem_used: typing.Optional[float]  # B per op


class BenchRes(typing.NamedTuple):
    inputs: BenchInputs
    outputs: BenchOutputs

    def get_var_names(self) -> typing.List[str]:
        return list(map(lambda x: x.var_name, self.inputs.variables))


class Benchmark:
    def __init__(self, name: str):
        self.name = name
        self._results: typing.List[BenchRes] = []
        self._var_names: typing.Optional[typing.List[str]] = None

    def add_result(self, result: BenchRes):
        self._results.append(result)

    def get_var_names(self) -> typing.List[str]:
        if self._var_names is not None:
            return self._var_names
        if len(self._results) == 0:
            raise Exception("no results")
        return self._results[0].get_var_names()


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
    if output_info.startswith('pkg') or output_info.startswith('goos') or output_info.startswith('goarch'):
        # ignore
        return None
    elif output_info.startswith("Benchmark"):
        # BenchInfo
        m = bench_info_expr.match(output_info)
        if not m:
            raise Exception("unexpected bench info")

        full_name = m[1]
        name: str = ''
        labels: typing.Optional[typing.List[str]] = None
        variables: typing.List[BenchVarValue] = []

        for i, value in enumerate(full_name.split('/')):
            if i == 0:
                name = value
                continue
            split_val = value.split("=")
            if len(split_val) != 2:
                if labels is None:
                    labels = [value]
                else:
                    labels.append(value)
            else:
                variables.append(
                    BenchVarValue(var_name=split_val[0], var_value=var_value(split_val[1])))
        return BenchInfo(
            name=name,
            inputs=BenchInputs(variables=variables, labels=labels))
    else:
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
