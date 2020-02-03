import copy
import benchmark
import functools
import unittest
import collections

sample_bench_results = (
    benchmark.BenchRes(
        inputs=benchmark.BenchInputs(
            subs=["first_bench"],
            variables=[
                benchmark.BenchVarValue(var_name='first_var',
                                        var_value='some_name'),
                benchmark.BenchVarValue(
                    var_name='second_var', var_value=1),
                benchmark.BenchVarValue(
                    var_name='third_var', var_value=1.00),
            ]),
        outputs=benchmark.BenchOutputs(
            runs=161651562, time=7.46, mem_used=0.0, mem_allocs=0),
    ),
    benchmark.BenchRes(
        inputs=benchmark.BenchInputs(
            subs=["first_bench"],
            variables=[
                benchmark.BenchVarValue(var_name='first_var',
                                        var_value='some_name'),
                benchmark.BenchVarValue(
                    var_name='second_var', var_value=2),
                benchmark.BenchVarValue(
                    var_name='third_var', var_value=1.01),
            ]),
        outputs=benchmark.BenchOutputs(
            runs=181651562, time=8.46, mem_used=0.0, mem_allocs=0),
    ),
)


class TestBenchmark(unittest.TestCase):

    def test_get_var_names(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in list(sample_bench_results):
            my_bench.add_result(bench_res)

        expected_var_names = ["first_var", "second_var", "third_var"]
        self.assertEqual(expected_var_names, my_bench.get_var_names())

    def test_get_subs(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in list(sample_bench_results):
            my_bench.add_result(bench_res)

        expected_subs = ["first_bench"]
        self.assertEqual(expected_subs, my_bench.get_subs())

    def test_grouped_results(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in list(sample_bench_results):
            my_bench.add_result(bench_res)

        res = my_bench.grouped_results('first_var')

        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = list(sample_bench_results)
        expected_grouped_res = {
            group_vals: [group_res[0], group_res[1]],
        }

        self.assertEqual(expected_grouped_res, res)


class TestGroupedResults(unittest.TestCase):
    def test_split_to(self):
        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = list(sample_bench_results)
        grouped_res: benchmark.GroupedResults = benchmark.GroupedResults(initdata={
            group_vals: [group_res[0], group_res[1]],
        })

        res = grouped_res.split_to('second_var', 'time')

        expected_split_res = {
            "first_var = some_name": [
                benchmark.SplitRes(
                    x=1, y=7.46),
                benchmark.SplitRes(
                    x=2, y=8.46),
            ]
        }

        self.assertEqual(expected_split_res, res)

    def test_filtered_by_subs(self):
        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res = list(sample_bench_results)
        group_res.append(benchmark.BenchRes(
            inputs=benchmark.BenchInputs(
                subs=["second_bench"],
                variables=[
                    benchmark.BenchVarValue(var_name='first_var',
                                            var_value='some_name'),
                    benchmark.BenchVarValue(
                        var_name='second_var', var_value=3),
                    benchmark.BenchVarValue(
                        var_name='third_var', var_value=1.02),
                ]),
            outputs=benchmark.BenchOutputs(
                runs=191651562, time=8.46, mem_used=0.0, mem_allocs=0),
        ))
        TestCase = collections.namedtuple(
            'TestCase', 'initdata subs expected_filtered')

        test_cases = {
            'already_filtered': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1]])},
                subs=['first_bench'],
                expected_filtered={group_vals: [group_res[0], group_res[1]]}),
            'valid_filter': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1], group_res[2]])},
                subs=['first_bench'],
                expected_filtered={group_vals: [group_res[0], group_res[1]]}),
            'no_matches': TestCase(
                initdata={group_vals: [group_res[0], group_res[1]]},
                subs=['second_bench'],
                expected_filtered={}),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                grouped_res: benchmark.GroupedResults = benchmark.GroupedResults(
                    initdata=test_case.initdata)
                filtered = grouped_res.filtered_by_subs(test_case.subs)
                self.assertEqual(test_case.expected_filtered, filtered)

    def test_filtered_by_var_value(self):
        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = list(sample_bench_results)
        TestCase = collections.namedtuple(
            'TestCase', 'initdata value expected_filtered')

        test_cases = {
            'already_filtered': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1]])},
                value=benchmark.BenchVarValue(var_name='first_var',
                                              var_value='some_name'),
                expected_filtered={group_vals: [group_res[0], group_res[1]]}),
            'valid_filter': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1]])},
                value=benchmark.BenchVarValue(var_name='second_var',
                                              var_value=2),
                expected_filtered={group_vals:  [group_res[1]]}),
            'no_matches': TestCase(
                initdata={group_vals: [group_res[0], group_res[1]]},
                value=benchmark.BenchVarValue(var_name='second_var',
                                              var_value=20),
                expected_filtered={}),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                grouped_res: benchmark.GroupedResults = benchmark.GroupedResults(
                    initdata=test_case.initdata)
                filtered = grouped_res.filtered_by_var_value(test_case.value)
                self.assertEqual(test_case.expected_filtered, filtered)


class TestFilterResults(unittest.TestCase):
    TestCase = collections.namedtuple(
        'TestCase', 'initial_res filter_exprs expected_filtered')

    group_vals = benchmark.BenchVarValues([
        benchmark.BenchVarValue(var_name='first_var',
                                var_value='some_name'),
    ])
    group_res = list(sample_bench_results)
    group_res.append(benchmark.BenchRes(
        inputs=benchmark.BenchInputs(
            subs=["second_bench"],
            variables=[
                benchmark.BenchVarValue(var_name='first_var',
                                        var_value='some_name'),
                benchmark.BenchVarValue(
                    var_name='second_var', var_value=2),
                benchmark.BenchVarValue(
                    var_name='third_var', var_value=1.02),
            ]),
        outputs=benchmark.BenchOutputs(
            runs=191651562, time=8.46, mem_used=0.0, mem_allocs=0),
    ))

    def test_filter_grouped_results(self):
        test_cases = {
            'already_filtered_by_subs': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]])}),
                filter_exprs=[benchmark.filter_expr(['first_bench'])],
                expected_filtered={self.group_vals: [self.group_res[0], self.group_res[1]]}),
            'valid_filter_by_subs': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[benchmark.filter_expr(['first_bench'])],
                expected_filtered={self.group_vals: [self.group_res[0], self.group_res[1]]}),
            'valid_filter_by_subs_and_vars': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[
                    benchmark.filter_expr(['first_bench']),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=2)),
                ],
                expected_filtered={self.group_vals: [self.group_res[1]]}),
            'valid_filter_by_subs': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[
                    benchmark.filter_expr(['second_bench']),
                ],
                expected_filtered={self.group_vals: [self.group_res[2]]}),
            'valid_filter_by_vars': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=2)),
                ],
                expected_filtered={self.group_vals: [self.group_res[1]]}),
            'no_matching_var_combo': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=3)),
                ],
                expected_filtered={}),
            'no_matching_var-sub_combo': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=[
                    benchmark.filter_expr(['second_bench']),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                ],
                expected_filtered={}),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                filtered = copy.deepcopy(test_case.initial_res)
                for expr in test_case.filter_exprs:
                    filtered = expr(filtered)
                self.assertEqual(test_case.expected_filtered, filtered)

    def test_filter_bench_results(self):
        test_cases = {
            'already_filtered_by_subs': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]]),
                filter_exprs=[benchmark.filter_expr(['first_bench'])],
                expected_filtered=[self.group_res[0], self.group_res[1]]),
            'valid_filter_by_subs': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[benchmark.filter_expr(['first_bench'])],
                expected_filtered=[self.group_res[0], self.group_res[1]]),
            'valid_filter_by_subs_and_vars': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[
                    benchmark.filter_expr(['first_bench']),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=2)),
                ],
                expected_filtered=[self.group_res[1]]),
            'valid_filter_by_subs': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[
                    benchmark.filter_expr(['second_bench']),
                ],
                expected_filtered=[self.group_res[2]]),
            'valid_filter_by_vars': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=2)),
                ],
                expected_filtered=[self.group_res[1]]),
            'no_matching_var_combo': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='second_var',
                                                                  var_value=3)),
                ],
                expected_filtered=[]),
            'no_matching_var-sub_combo': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=[
                    benchmark.filter_expr(['second_bench']),
                    benchmark.filter_expr(benchmark.BenchVarValue(var_name='third_var',
                                                                  var_value=1.01)),
                ],
                expected_filtered=[]),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                filtered = copy.deepcopy(test_case.initial_res)
                for expr in test_case.filter_exprs:
                    filtered = expr(filtered)
                self.assertEqual(test_case.expected_filtered, filtered)


class TestVarValue(unittest.TestCase):
    def test_int(self):
        parsed_vals = ['1', '2', '0', '-1', '100']
        expected_vals = [1, 2, 0, -1, 100]

        for i, parsed_val in enumerate(parsed_vals):
            with self.subTest(parsed_val):
                val = benchmark.var_value(parsed_val)
                self.assertIsInstance(val, int)
                self.assertEqual(expected_vals[i], val)

    def test_str(self):
        parsed_vals = ['hello', '12h34m', '_', '', ' ']
        expected_vals = ['hello', '12h34m', '_', '', ' ']

        for i, parsed_val in enumerate(parsed_vals):
            with self.subTest(parsed_val):
                val = benchmark.var_value(parsed_val)
                self.assertIsInstance(val, str)
                self.assertEqual(expected_vals[i], val)

    def test_float(self):
        parsed_vals = ['1.0', '2.2', '0.000', '-1.1', '100.2', '.2']
        expected_vals = [1.0, 2.2, 0.000, -1.1, 100.2, 0.2]

        for i, parsed_val in enumerate(parsed_vals):
            with self.subTest(parsed_val):
                val = benchmark.var_value(parsed_val)
                self.assertIsInstance(val, float)
                self.assertEqual(expected_vals[i], val)

    def test_bool(self):
        parsed_vals = ['true', 'TRUE', 'True', 'false', 'FALSE', 'false']
        expected_vals = [True, True, True, False, False, False]

        for i, parsed_val in enumerate(parsed_vals):
            with self.subTest(parsed_val):
                val = benchmark.var_value(parsed_val)
                self.assertIsInstance(val, bool)
                self.assertEqual(expected_vals[i], val)


class TestParseOutLine(unittest.TestCase):
    def test_bench_info(self):
        input_line = r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsInstance(parsed, benchmark.BenchInfo,
                              "unexpected return type")
        self.assertEqual("BenchmarkMyMethod", parsed.name, "unexpected name")
        self.assertEqual(
            ["some_case"], parsed.inputs.subs, "unexpected subs")
        self.assertEqual(
            [
                benchmark.BenchVarValue(var_name='first_var',
                                        var_value='some_name'),
                benchmark.BenchVarValue(var_name='second_var', var_value=1),
                benchmark.BenchVarValue(var_name='third_var', var_value=1.00),
            ],
            parsed.inputs.variables,
            "unexpected variable values")

    def test_bench_outputs(self):
        TestCase = collections.namedtuple(
            "TestCase", "input_line expected_runs expected_time expected_mem_used expected_mem_allocs")

        test_cases = {
            "standard_out_line": TestCase(
                input_line=r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         7.46 ns/op\t       0 B/op\t       0 allocs/op\n"}',
                expected_runs=161651562,
                expected_time=7.46,
                expected_mem_used=0.0,
                expected_mem_allocs=0),
            "leading_output_spaces": TestCase(
                input_line=r'{"Time":"2020-01-31T23:18:48.655401-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"  790609\t      1513 ns/op\t       0 B/op\t 0 allocs/op\n"}',
                expected_runs=790609,
                expected_time=1513,
                expected_mem_used=0.0,
                expected_mem_allocs=0),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                parsed = benchmark.parse_out_line(test_case.input_line)
                self.assertIsInstance(parsed, benchmark.BenchOutputs,
                                      "unexpected return type")
                self.assertEqual(test_case.expected_runs,
                                 parsed.runs, "unexpected runs")
                self.assertEqual(test_case.expected_time,
                                 parsed.time, "unexpected duration")
                self.assertEqual(test_case.expected_mem_used,
                                 parsed.mem_used, "unexpected memory usage")
                self.assertEqual(test_case.expected_mem_allocs,
                                 parsed.mem_allocs, "unexpected memory allocs")

    def test_ignored_line(self):
        input_line = r'{"Time":"2020-01-30T17:14:24.924867-06:00","Action":"fail","Package":"github.com/ShawnROGrady/mapslicecomp","Elapsed":3.233}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsNone(parsed)

    def test_ignored_output_line(self):
        input_line = r'{"Time":"2020-01-30T17:14:21.904978-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"pkg: github.com/SomeUser/somepkg\n"}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsNone(parsed)


class TestBenchSuite(unittest.TestCase):
    def test_readline(self):
        input_lines = [
            r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}',
            r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         7.46 ns/op\t       0 B/op\t       0 allocs/op\n"}',
        ]

        bench_name = "BenchmarkMyMethod"

        suite = benchmark.BenchSuite()
        for line in input_lines:
            suite.readline(line)

        bench = suite.get_benchmark(bench_name)
        self.assertIsNotNone(bench)


if __name__ == '__main__':
    unittest.main()
