import benchmark
import unittest


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

    def test_split_to(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in self.sample_bench_results:
            my_bench.add_result(bench_res)

        res = my_bench.split_to('second_var', 'time',
                                'first_var', subs=['first_bench'])

        expected_split_res = {
            "first_var = some_name": [
                benchmark.SplitRes(
                    x=1, y=7.46),
                benchmark.SplitRes(
                    x=2, y=8.46),
            ]
        }

        self.assertEqual(expected_split_res, res)


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
        input_line = r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         7.46 ns/op\t       0 B/op\t       0 allocs/op\n"}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsInstance(parsed, benchmark.BenchOutputs,
                              "unexpected return type")
        self.assertEqual(161651562, parsed.runs, "unexpected runs")
        self.assertEqual(7.46, parsed.time, "unexpected duration")
        self.assertEqual(0.0, parsed.mem_used, "unexpected memory usage")
        self.assertEqual(0, parsed.mem_allocs, "unexpected memory allocs")

    def test_ignored_line(self):
        input_line = r'{"Time":"2020-01-30T17:14:24.924867-06:00","Action":"fail","Package":"github.com/ShawnROGrady/mapslicecomp","Elapsed":3.233}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsNone(parsed)

    def test_ignored_output_line(self):
        input_line = r'{"Time":"2020-01-30T17:14:21.904978-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"pkg: github.com/SomeUser/somepkg\n"}'
        parsed = benchmark.parse_out_line(input_line)
        self.assertIsNone(parsed)


if __name__ == '__main__':
    unittest.main()
