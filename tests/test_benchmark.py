import io
import copy
import gobenchplot.benchmark as benchmark
import gobenchplot.inputs as inputs
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

sample_bench_results_no_mem = (
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
            runs=161651562, time=7.46, mem_used=None, mem_allocs=None),
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
            runs=181651562, time=8.46, mem_used=None, mem_allocs=None),
    ),
)


class TestBenchVarValue(unittest.TestCase):
    def test_eq(self):
        TestCase = collections.namedtuple(
            'TestCase', 'a b expect_eq')
        test_cases = {
            'equal_var_values': TestCase(
                a=benchmark.BenchVarValue(var_name='a', var_value=1),
                b=benchmark.BenchVarValue(var_name='a', var_value=1),
                expect_eq=True),
            'nonequal_var_values': TestCase(
                a=benchmark.BenchVarValue(var_name='a', var_value=1),
                b=benchmark.BenchVarValue(var_name='b', var_value=1),
                expect_eq=False),
            'a=None': TestCase(
                a=None,
                b=benchmark.BenchVarValue(var_name='b', var_value=1),
                expect_eq=False),
            'b=int': TestCase(
                a=benchmark.BenchVarValue(var_name='a', var_value=1),
                b=1,
                expect_eq=False),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                is_eq = test_case.a == test_case.b
                self.assertEqual(test_case.expect_eq, is_eq)


class TestBenchVarValues(unittest.TestCase):
    def test_contains(self):
        TestCase = collections.namedtuple(
            'TestCase', 'values other expect_in')
        test_cases = {
            'contains': TestCase(
                values=benchmark.BenchVarValues([
                    benchmark.BenchVarValue(var_name='a', var_value=1),
                    benchmark.BenchVarValue(var_name='b', var_value=2),
                ]),
                other=benchmark.BenchVarValue(var_name='a', var_value=1),
                expect_in=True),
            'not_contains': TestCase(
                values=benchmark.BenchVarValues([
                    benchmark.BenchVarValue(var_name='a', var_value=1),
                    benchmark.BenchVarValue(var_name='b', var_value=2),
                ]),
                other=benchmark.BenchVarValue(var_name='a', var_value=2),
                expect_in=False),
            'other=int': TestCase(
                values=benchmark.BenchVarValues([
                    benchmark.BenchVarValue(var_name='a', var_value=1),
                    benchmark.BenchVarValue(var_name='b', var_value=2),
                ]),
                other=1,
                expect_in=False),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                is_in = test_case.other in test_case.values
                self.assertEqual(test_case.expect_in, is_in)


class TestBenchOutputs(unittest.TestCase):
    def test_bench_output_units(self):
        TestCase = collections.namedtuple(
            'TestCase', 'out_name expected_units')
        test_cases = [
            TestCase(
                out_name='runs',
                expected_units=''),
            TestCase(
                out_name='time',
                expected_units='ns/op'),
            TestCase(
                out_name='mem_allocs',
                expected_units='allocs/op'),
            TestCase(
                out_name='mem_used',
                expected_units='B/op'),
            TestCase(
                out_name='unknown_name',
                expected_units=''),
        ]
        for test_case in test_cases:
            with self.subTest(test_case.out_name):
                units = benchmark.bench_output_units(test_case.out_name)
                self.assertEqual(test_case.expected_units, units)
        return


class TestBenchmark(unittest.TestCase):
    def test_get_var_names(self):
        my_bench = benchmark.Benchmark("BenchmarkMyMethod")
        for bench_res in list(sample_bench_results):
            my_bench.add_result(bench_res)

        expected_var_names = ["first_var", "second_var", "third_var"]
        self.assertEqual(expected_var_names, my_bench.get_var_names())

    def test_get_subs(self):
        TestCase = collections.namedtuple(
            'TestCase', 'results expected_subs')
        test_cases = {
            'one_sub': TestCase(
                results=list(sample_bench_results),
                expected_subs=["first_bench"]),
            'two_subs': TestCase(
                results=[
                    benchmark.BenchRes(
                        inputs=benchmark.BenchInputs(
                            subs=["first_bench", "second_bench"],
                            variables=[
                                benchmark.BenchVarValue(var_name='first_var',
                                                        var_value='some_name'),
                            ]),
                        outputs=benchmark.BenchOutputs(
                            runs=161651562, time=7.46, mem_used=0.0, mem_allocs=0),
                    ),
                    benchmark.BenchRes(
                        inputs=benchmark.BenchInputs(
                            subs=["first_bench", "second_bench"],
                            variables=[
                                benchmark.BenchVarValue(var_name='first_var',
                                                        var_value='some_name'),
                            ]),
                        outputs=benchmark.BenchOutputs(
                            runs=181651562, time=8.46, mem_used=0.0, mem_allocs=0),
                    ),
                ],
                expected_subs=["first_bench", "second_bench"]),
            'no_subs': TestCase(
                results=[
                    benchmark.BenchRes(
                        inputs=benchmark.BenchInputs(
                            subs=None,
                            variables=[
                                benchmark.BenchVarValue(var_name='first_var',
                                                        var_value='some_name'),
                            ]),
                        outputs=benchmark.BenchOutputs(
                            runs=161651562, time=7.46, mem_used=0.0, mem_allocs=0),
                    ),
                    benchmark.BenchRes(
                        inputs=benchmark.BenchInputs(
                            subs=None,
                            variables=[
                                benchmark.BenchVarValue(var_name='first_var',
                                                        var_value='some_name'),
                            ]),
                        outputs=benchmark.BenchOutputs(
                            runs=181651562, time=8.46, mem_used=0.0, mem_allocs=0),
                    ),
                ],
                expected_subs=None),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                my_bench = benchmark.Benchmark("BenchmarkMyMethod")
                for bench_res in list(test_case.results):
                    my_bench.add_result(bench_res)
                self.assertEqual(test_case.expected_subs, my_bench.get_subs())

    def test_grouped_results(self):
        group_res: benchmark.GroupedResults = list(sample_bench_results)
        TestCase = collections.namedtuple(
            'TestCase', 'results group_by expected_grouped_res')
        test_cases = {
            'no_initial_results': TestCase(
                results=[],
                group_by='first_var',
                expected_grouped_res={}),
            'valid_single_var': TestCase(
                results=list(sample_bench_results),
                group_by='first_var',
                expected_grouped_res={
                    benchmark.BenchVarValues(
                        [benchmark.BenchVarValue(
                            var_name='first_var', var_value='some_name')],
                    ): [group_res[0], group_res[1]],
                }),
            '2_valid_vars': TestCase(
                results=list(sample_bench_results),
                group_by=['first_var', 'second_var'],
                expected_grouped_res={
                    benchmark.BenchVarValues(
                        [
                            benchmark.BenchVarValue(
                                var_name='first_var', var_value='some_name'),
                            benchmark.BenchVarValue(
                                var_name='second_var', var_value=1),
                        ],
                    ): [group_res[0]],
                    benchmark.BenchVarValues(
                        [
                            benchmark.BenchVarValue(
                                var_name='first_var', var_value='some_name'),
                            benchmark.BenchVarValue(
                                var_name='second_var', var_value=2),
                        ],
                    ): [group_res[1]],
                }),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                my_bench = benchmark.Benchmark("BenchmarkMyMethod")
                for bench_res in test_case.results:
                    my_bench.add_result(bench_res)
                res = my_bench.results.group_by(test_case.group_by)
                self.assertEqual(test_case.expected_grouped_res, res)

    def test_grouped_results_raises(self):
        TestCase = collections.namedtuple(
            'TestCase', 'results group_by expected_err_type')

        test_cases = {
            'group_by_invalid_str': TestCase(
                results=list(sample_bench_results),
                group_by='fourth_var',
                expected_err_type=inputs.InvalidInputError),
            'group_by_invalid_list': TestCase(
                results=list(sample_bench_results),
                group_by=['fourth_var'],
                expected_err_type=inputs.InvalidInputError),
            'group_by_int': TestCase(
                results=list(sample_bench_results),
                group_by=1,
                expected_err_type=inputs.InvalidInputError),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                my_bench = benchmark.Benchmark("BenchmarkMyMethod")
                for bench_res in test_case.results:
                    my_bench.add_result(bench_res)
                with self.assertRaises(test_case.expected_err_type):
                    grouped_res = my_bench.results.group_by(
                        test_case.group_by)


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

    def test_split_to_raises(self):
        TestCase = collections.namedtuple(
            'TestCase', 'grouped_results x_name y_name expected_err_type')
        test_cases = {
            'invalid_x_name': TestCase(
                grouped_results={
                    benchmark.BenchVarValues([
                        benchmark.BenchVarValue(var_name='first_var',
                                                var_value='some_name'),
                    ]): list(sample_bench_results),
                },
                x_name='fake_var',
                y_name='time',
                expected_err_type=inputs.InvalidInputError),
            'invalid_y_name': TestCase(
                grouped_results={
                    benchmark.BenchVarValues([
                        benchmark.BenchVarValue(var_name='first_var',
                                                var_value='some_name'),
                    ]): list(sample_bench_results),
                },
                x_name='first_var',
                y_name='fake_output',
                expected_err_type=inputs.InvalidInputError),
            'y_name_corresponds_to_none': TestCase(
                grouped_results={
                    benchmark.BenchVarValues([
                        benchmark.BenchVarValue(var_name='first_var',
                                                var_value='some_name'),
                    ]): list(sample_bench_results_no_mem),
                },
                x_name='first_var',
                y_name='mem_allocs',
                expected_err_type=inputs.InvalidInputError),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                grouped_res: benchmark.GroupedResults = benchmark.GroupedResults(
                    initdata=test_case.grouped_results)
                with self.assertRaises(test_case.expected_err_type):
                    res = grouped_res.split_to(
                        test_case.x_name, test_case.y_name)

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

    def test_update(self):
        group_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='some_name'),
        ])
        group_res: benchmark.GroupedResults = list(sample_bench_results)

        new_vals = benchmark.BenchVarValues([
            benchmark.BenchVarValue(var_name='first_var',
                                    var_value='another_name'),
        ])
        new_res = benchmark.BenchRes(
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
        )

        TestCase = collections.namedtuple(
            'TestCase', 'initdata arg expected_updated')
        test_cases = {
            'additive_update': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1]])},
                arg={new_vals: benchmark.BenchResults([
                    new_res])},
                expected_updated={
                    group_vals: benchmark.BenchResults(
                        [group_res[0], group_res[1]]),
                    new_vals: benchmark.BenchResults(
                        [new_res]),
                },
            ),
            'replacing_update': TestCase(
                initdata={group_vals: benchmark.BenchResults(
                    [group_res[0], group_res[1]])},
                arg={group_vals: benchmark.BenchResults([
                    new_res])},
                expected_updated={
                    group_vals: benchmark.BenchResults(
                        [new_res]),
                },
            ),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                grouped_res: benchmark.GroupedResults = benchmark.GroupedResults(
                    initdata=test_case.initdata)
                grouped_res.update(test_case.arg)
                self.assertEqual(test_case.expected_updated, grouped_res)


class TestBenchResults(unittest.TestCase):
    new_res = benchmark.BenchRes(
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
    )

    # helper
    def init_res(self):
        initdata = copy.copy(list(sample_bench_results))
        results = benchmark.BenchResults(initdata)

        return results

    def test_get_item(self):
        results = self.init_res()

        self.assertEqual(sample_bench_results[0], results[0])
        self.assertEqual(sample_bench_results[1], results[1])

    def test_set_item(self):
        results = self.init_res()

        results[0] = self.new_res
        self.assertEqual(self.new_res, results[0])
        self.assertEqual(sample_bench_results[1], results[1])

    def test_contains(self):
        results = self.init_res()

        self.assertTrue(sample_bench_results[0] in results)

    def test_append(self):
        results = self.init_res()

        results.append(self.new_res)
        self.assertEqual(self.new_res, results[2])

    def test_delete(self):
        results = self.init_res()

        del results[0]
        self.assertEqual(1, len(results))
        self.assertFalse(sample_bench_results[0] in results)

    def test_list(self):
        results = self.init_res()

        self.assertEqual(list(results), list(sample_bench_results))

    def test_eq(self):
        TestCase = collections.namedtuple(
            'TestCase', 'a b expect_eq')

        test_cases = {
            'eq_bench_results': TestCase(
                a=self.init_res(),
                b=self.init_res(),
                expect_eq=True),
            'eq_bench_results+list': TestCase(
                a=self.init_res(),
                b=list(sample_bench_results),
                expect_eq=True),
            'non_eq_bench_results': TestCase(
                a=self.init_res(),
                b=benchmark.BenchResults([self.new_res]),
                expect_eq=False),
            'non_eq_bench_results+list': TestCase(
                a=self.init_res(),
                b=[self.new_res],
                expect_eq=False),
            'b=int': TestCase(
                a=self.init_res(),
                b=1,
                expect_eq=False),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                is_eq = test_case.a == test_case.b
                self.assertEqual(test_case.expect_eq, is_eq)


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
            'filter_by_int': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]])}),
                filter_exprs=[benchmark.filter_expr(1)],
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
            'valid_filter_by_subs_and_vars_with_builder': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    ['first_bench'],
                    ['second_var==2', 'first_var==some_name']),
                expected_filtered={self.group_vals: [self.group_res[1]]}),
            'valid_filter_by_not_eq_var_value': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    [],
                    ['second_var!=2']),
                expected_filtered={self.group_vals: [self.group_res[0]]}),
            'valid_filter_by_lt_var_value': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    [],
                    ['second_var<2']),
                expected_filtered={self.group_vals: [self.group_res[0]]}),
            'valid_filter_by_gt_var_value': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    [],
                    ['third_var>1']),
                expected_filtered={self.group_vals: [self.group_res[1], self.group_res[2]]}),
            'valid_filter_by_le_var_value': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    [],
                    ['third_var<=1.01']),
                expected_filtered={self.group_vals: [self.group_res[0], self.group_res[1]]}),
            'valid_filter_by_ge_var_value': self.TestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]])}),
                filter_exprs=benchmark.build_filter_exprs(
                    [],
                    ['third_var>=1.01']),
                expected_filtered={self.group_vals: [self.group_res[1], self.group_res[2]]}),
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

    def test_build_filter_exprs_raises(self):
        RaisesTestCase = collections.namedtuple(
            'RaisesTestCase', 'initial_res subs var_values expected_err_type')

        test_cases = {
            'invalid_var_value': RaisesTestCase(
                initial_res=benchmark.GroupedResults(initdata={self.group_vals: benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]])}),
                subs=None, var_values=['first_var-some_value'],
                expected_err_type=inputs.InvalidInputError),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                filtered = copy.deepcopy(test_case.initial_res)
                with self.assertRaises(test_case.expected_err_type):
                    exprs = benchmark.build_filter_exprs(
                        test_case.subs, test_case.var_values)

    def test_filter_bench_results(self):
        test_cases = {
            'already_filtered_by_subs': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]]),
                filter_exprs=[benchmark.filter_expr(['first_bench'])],
                expected_filtered=[self.group_res[0], self.group_res[1]]),
            'filter_by_int': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1]]),
                filter_exprs=[benchmark.filter_expr(1)],
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
            'valid_filter_by_subs_and_vars_with_builder': self.TestCase(
                initial_res=benchmark.BenchResults(
                    [self.group_res[0], self.group_res[1], self.group_res[2]]),
                filter_exprs=benchmark.build_filter_exprs(
                    ['first_bench'],
                    ['second_var==2', 'first_var==some_name']),
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
        TestCase = collections.namedtuple(
            'TestCase', 'input_line expected_name expected_vars expected_subs')

        test_cases = {
            'standard_info_line': TestCase(
                input_line=r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}',
                expected_name='BenchmarkMyMethod',
                expected_vars=[
                    benchmark.BenchVarValue(var_name='first_var',
                                            var_value='some_name'),
                    benchmark.BenchVarValue(
                        var_name='second_var', var_value=1),
                    benchmark.BenchVarValue(
                        var_name='third_var', var_value=1.00),
                ],
                expected_subs=['some_case']),
            'multiple_subs': TestCase(
                input_line=r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/another_case/second_var=1/third_var=1.00-4         \t"}',
                expected_name='BenchmarkMyMethod',
                expected_vars=[
                    benchmark.BenchVarValue(var_name='first_var',
                                            var_value='some_name'),
                    benchmark.BenchVarValue(
                        var_name='second_var', var_value=1),
                    benchmark.BenchVarValue(
                        var_name='third_var', var_value=1.00),
                ],
                expected_subs=['some_case', 'another_case']),
        }
        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                parsed = benchmark.parse_out_line(test_case.input_line)
                self.assertIsInstance(parsed, benchmark.BenchInfo,
                                      "unexpected return type")
                self.assertEqual(test_case.expected_vars,
                                 parsed.inputs.variables)
                self.assertEqual(test_case.expected_subs, parsed.inputs.subs)

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

    def test_raises(self):
        TestCase = collections.namedtuple(
            'TestCase', 'input_line expected_err_type')
        test_cases = {
            'invalid_info_expression': TestCase(
                input_line=r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod_abc"}',
                expected_err_type=benchmark.ParseBenchmarkError),
            'output_missing_time': TestCase(
                input_line=r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         0 B/op\t       0 allocs/op\n"}',
                expected_err_type=benchmark.ParseBenchmarkError),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                with self.assertRaises(test_case.expected_err_type):
                    parsed = benchmark.parse_out_line(test_case.input_line)


class TestBenchSuite(unittest.TestCase):
    def test_readline(self):
        input_lines = [
            r'{"Time":"2020-01-30T17:14:21.904978-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"pkg: github.com/SomeUser/somepkg\n"}',
            r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}',
            r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         7.46 ns/op\t       0 B/op\t       0 allocs/op\n"}',
            r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=2/third_var=1.01-4         \t"}',
            r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         8.46 ns/op\t       0 B/op\t       0 allocs/op\n"}',
        ]

        bench_name = "BenchmarkMyMethod"

        f = io.StringIO()
        for line in input_lines:
            f.write(line + '\n')
        f.seek(0)
        suite = benchmark.parse_bench_output(f)
        f.close()

        bench = suite.get_benchmark(bench_name)
        self.assertIsNotNone(bench)

        self.assertEqual(1, len(suite.benchmarks))

        bench2 = suite.get_benchmark("InvalidBenchmarkName")
        self.assertIsNone(bench2)

    def test_readline_raises(self):
        TestCase = collections.namedtuple(
            'TestCase', 'input_lines expected_err_type')
        test_cases = {
            'output_missing_time': TestCase(
                input_lines=[
                    r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}',
                    r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         0 B/op\t       0 allocs/op\n"}',
                ],
                expected_err_type=benchmark.ParseBenchmarkError),
            'info_output_swapped': TestCase(
                input_lines=[
                    r'{"Time":"2020-01-30T17:14:23.859509-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"161651562\t         7.46 ns/op\t       0 B/op\t       0 allocs/op\n"}',
                    r'{"Time":"2020-01-30T12:53:44.276751-06:00","Action":"output","Package":"github.com/SomeUser/somepkg","Output":"BenchmarkMyMethod/some_case/first_var=some_name/second_var=1/third_var=1.00-4         \t"}',
                ],
                expected_err_type=benchmark.ParseBenchmarkError),
        }

        for test_name, test_case in test_cases.items():
            with self.subTest(test_name):
                with self.assertRaises(test_case.expected_err_type):
                    f = io.StringIO()
                    for line in test_case.input_lines:
                        f.write(line + '\n')
                    f.seek(0)
                    suite = benchmark.parse_bench_output(f)
                    f.close()
        return


if __name__ == '__main__':
    unittest.main()
