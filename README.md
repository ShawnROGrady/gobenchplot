# gobenchplot
This is a tool I've been using to plot the results of go benchmarks. It assumes that each sub-benchmark is named as `var_name=var_value`.
The input is the output of a go benchmark.

**NOTE:** right now this tool assumes that the benchmark was run with the `-json` flag.

For a full set of options run `gobenchplot --help`

## Examples

Running benchmark [comparing the performance of maps and slices](https://github.com/ShawnROGrady/mapslicecomp):
```
go test . -run ! -bench BenchmarkDedupe -benchmem -json -timeout 0 -benchtime 10000x -count 3 | tee tmp.txt | gobenchplot --bench='BenchmarkDedupe' --x='num_elems' --group-by='finder'
```
![bench_dedupe](https://github.com/ShawnROGrady/mapslicecomp/blob/master/assets/benchmark_dedupe_time-v-num_elems.png)

Focusing on just the portion of interest:
```
gobenchplot --bench='BenchmarkDedupe' --x='num_elems' --group-by='finder' --filter-by='num_elems<=10' tmp.txt
```
![focused_bench_dedupe](https://github.com/ShawnROGrady/mapslicecomp/blob/master/assets/focused_benchmark_dedupe_time-v-num_elems.png)

## Next Steps
I plan on eventually re-implementing this in go. Python and `matplotlib` have been my default tools for generating plots but after some preliminary research it looks like there are plenty of tools in the go ecosystem that would be a suitable replacement for this use case.
