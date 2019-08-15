task-generation
===============

A tool to return interesting, randomized input-output (IO) examples for learning list routines.

Strategy
--------

Constructs IO examples using a constraint propagation technique from the [DeepCoder](https://arxiv.org/abs/1611.01989) paper, as well as maximizing output variance via de-duplication. The goal is to increase the entropy of the inputs and outputs in each set of IO pairs for a task. For example, if a task is to learn a counting function from a bunch of input-output examples, it's impossible to learn it if all of the output values are equal to zero.

Usage
-----

This program requires Python 3 and that you run `pip install -r requirements`.

Generated IO examples will by default be output to the console. Demo:
```
❯ time ./taskg --maxv 10 --max-bound 10
Demo mode:
...
program:  a <- [int] | b <- tail a | c <- last b | d <- count c b
i: [[6, 5, 4, 9, 8, 2, 4, 0]]          o: 1
i: [[3, 5, 5, 3, 8, 5]]                o: 3
i: [[8, 9, 9]]                         o: 2
i: [[4]]                               o: 0
i: [[6, 8, 7, 8, 8, 2, 8]]             o: 4
i: [[7, 4, 2, 2, 3, 0, 2, 2, 2]]       o: 5
i: [[8]]                               o: 0
i: [[3, 1, 0, 3, 7, 8]]                o: 1
i: [[3, 7, 7, 4, 7, 7, 6, 7]]          o: 5
i: [[1]]                               o: 0
...

./taskg --maxv 10 --max-bound 10  4.61s user 0.13s system 107% cpu 4.424 total
```

To generate IO examples a program from stdin, use the `--stdin` flag:
```
❯ echo "a <- [int] | b <- tail a" | ./taskg --stdin --maxv 5 --max-bound 5
...
i: [[0, 3, 3, 4, 2, 2, 0]]             o: [3, 3, 4, 2, 2, 0]
i: [[3, 3, 2]]                         o: [3, 2]
i: [[4, 3, 3, 4, 2]]                   o: [3, 3, 4, 2]
i: [[2, 0]]                            o: [0]
i: [[3, 2, 4, 1, 0, 1, 0, 2, 2]]       o: [2, 4, 1, 0, 1, 0, 2, 2]
i: [[1, 2, 3]]                         o: [2, 3]
i: [[1, 1, 3, 2]]                      o: [1, 3, 2]
i: [[3, 1, 1, 1, 0, 3]]                o: [1, 1, 1, 0, 3]
i: [[1, 2, 2, 2, 0, 4, 3, 4, 2]]       o: [2, 2, 2, 0, 4, 3, 4, 2]
i: [[4, 0, 4]]                         o: [0, 4]
```

To output to json, use the `--json` flag. Example:
```
❯ ./taskg --json
...
/Users/lcary/w/mit/task-generation/io.json
```

Note that higher bound values (min/max for input/output values) increase the runtime:
```
❯ time ./taskg --maxv 99 --max-bound 99
...
program:  a <- int | b <- [int] | c <- count a b
i: [5, [9, 7, 4, 4]]                         o: 0
i: [8, [3, 8]]                               o: 1
i: [5, [4, 5, 9, 8, 7, 0, 8, 5]]             o: 2
i: [7, [6, 7, 3, 3, 7, 0, 7, 2]]             o: 3
i: [1, [33, 1, 1, 7, 3, 6, 1, 9, 1]]         o: 4
i: [9, [78, 9, 52, 6, 9, 76, 9, 9, 9]]       o: 5
i: [9, [1, 9]]                               o: 1
i: [0, [8, 0, 0, 17, 0, 0, 5, 3, 0]]         o: 5
i: [4, [3]]                                  o: 0
i: [36, [4]]                                 o: 0
...
./taskg --maxv 99 --max-bound 99  38.44s user 0.19s system 100% cpu 38.374 total
```

Higher example numbers (`-n`) also increase runtime significantly:
```
❯ time ./taskg -n 100 > ioexamples.txt
./taskg -n 100 > ioexamples.txt  68.85s user 0.19s system 100% cpu 1:08.80 total
```

Run `./taskg -h` for a complete list of parameterized settings.

References
----------

 1. https://arxiv.org/pdf/1611.01989.pdf
 2. https://www.biorxiv.org/content/10.1101/321505v1
