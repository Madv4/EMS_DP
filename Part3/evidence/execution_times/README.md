# Part 3 execution-time evidence

The timing procedure follows the supplied assignment instructions:

1. Compile first where compilation applies.
2. Run one unrecorded warmup.
3. Run the same test process five times on one machine.
4. Measure elapsed wall-clock process time with `time.perf_counter_ns()`.
5. Report the median in milliseconds.

The measured command includes runtime/process startup, module loading, all assertions, and console output. Compilation is excluded.

`raw_timings.csv` contains the twenty measured Python and JavaScript runs. `summary.csv` contains their medians and blank Java/C++ values. Java and C++ remain unmeasured because their raw five-run timings were not supplied; no values were estimated.
