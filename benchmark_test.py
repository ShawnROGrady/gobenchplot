import benchmark
import unittest
import collections


class TestBenchmark(unittest.TestCase):
    sample_bench_results = [
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
    ]

    def test_get_var_names(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in self.sample_bench_results:
            my_bench.add_result(bench_res)

        expected_var_names = ["first_var", "second_var", "third_var"]
        self.assertEqual(expected_var_names, my_bench.get_var_names())

    def test_get_subs(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in self.sample_bench_results:
            my_bench.add_result(bench_res)

        expected_subs = ["first_bench"]
        self.assertEqual(expected_subs, my_bench.get_subs())

    def test_grouped_results(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in self.sample_bench_results:
            my_bench.add_result(bench_res)

        res = my_bench.grouped_results('first_var', subs=['first_bench'])

        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = self.sample_bench_results
        expected_grouped_res: benchmark.GroupedResults = {
            group_vals: [group_res[0], group_res[1]],
        }

        self.assertEqual(expected_grouped_res, res)


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
