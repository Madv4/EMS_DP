# Part 3 metrics

## Static metrics

| Pattern | Language | Production source LOC | Maximum function CC |
|---|---:|---:|---:|
| Strategy | Java | 72 | 5 |
| Strategy | Python | 51 | 3 |
| Strategy | JavaScript | 71 | 5 |
| Strategy | C++ | 82 | 5 |
| Observer | Java | 86 | 3 |
| Observer | Python | 43 | 3 |
| Observer | JavaScript | 63 | 3 |
| Observer | C++ | 67 | 3 |

Source LOC excludes blank lines, comment-only lines, and tests. Cyclomatic complexity uses the manual McCabe rule documented in `Part3/README.md`.

## Process timing summary

| Pattern | Language | Median process time (ms) | Evidence |
|---|---:|---:|---|
| Strategy | Python | 20.552 | One warmup and five measured runs |
| Strategy | JavaScript | 41.596 | One warmup and five measured runs |
| Strategy | Java | Not measured | Raw five-run timing not supplied |
| Strategy | C++ | Not measured | Raw five-run timing not supplied |
| Observer | Python | 45.165 | One warmup and five measured runs |
| Observer | JavaScript | 42.924 | One warmup and five measured runs |
| Observer | Java | Not measured | Raw five-run timing not supplied |
| Observer | C++ | Not measured | Raw five-run timing not supplied |

The measured values include process startup, runner loading, assertions, and console output. They are evidence for reproducibility on this machine and are not general language-performance rankings.
