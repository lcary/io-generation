# task-generation

A tool to return interesting, randomized input-output (IO) examples for learning list routines.

Strategy: attempts to construct useful IO examples by a constraint propagation technique used by the DeepCoder paper (https://arxiv.org/abs/1611.01989), as well as maximizing output variance via de-duplication.

Example usage:
```
❯ time ./taskg
program:  a <- [int] | b <- head a
i: [[8, 9]]                              o: 8
i: [[2, 6, 7, 0, 33]]                    o: 2
i: [[3, 9, 9, 8, 4, 60, 9, 23, 1]]       o: 3
i: [[1]]                                 o: 1
i: [[2, 13, 9, 66, 5, 9, 6, 1]]          o: 2
i: [[8, 7, 1]]                           o: 8
i: [[5, 4, 3]]                           o: 5
i: [[8, 5, 2]]                           o: 8
i: [[98, 4, 9, 8, 5]]                    o: 98
i: [[8, 2]]                              o: 8

program:  a <- [int] | b <- tail a
i: [[72]]                               o: []
i: [[3, 6, 32, 5, 7, 9, 6, 9, 8]]       o: [6, 32, 5, 7, 9, 6, 9, 8]
i: [[26, 76, 7, 6, 6, 43]]              o: [76, 7, 6, 6, 43]
i: [[11, 4]]                            o: [4]
i: [[49]]                               o: []
i: [[1, 2, 8, 0, 2, 4, 4, 66, 8]]       o: [2, 8, 0, 2, 4, 4, 66, 8]
i: [[0, 8, 5, 0, 76, 73]]               o: [8, 5, 0, 76, 73]
i: [[2, 9, 4, 3, 5, 7, 8]]              o: [9, 4, 3, 5, 7, 8]
i: [[7, 2, 23, 37, 9]]                  o: [2, 23, 37, 9]
i: [[6]]                                o: []

program:  a <- [int] | b <- tail a | c <- head a | d <- count c b
i: [[5]]                             o: 0
i: [[7, 5, 9, 7, 7, 3, 61]]          o: 2
i: [[7, 0, 7]]                       o: 1
i: [[5, 5, 5, 5, 0, 7, 4, 1]]        o: 3
i: [[8, 8, 18, 2, 8, 7, 8, 8]]       o: 4
i: [[7, 7, 0, 7, 7, 7, 7, 4]]        o: 5
i: [[77, 1, 2, 4, 4, 4, 0, 5]]       o: 0
i: [[9, 1, 0, 9, 6, 6, 9, 3]]        o: 2
i: [[5, 0, 6, 55, 5]]                o: 1
i: [[2, 9, 7, 2, 2]]                 o: 2

program:  a <- [int] | b <- tail a | c <- len a | d <- count c b
i: [[5, 70, 1, 2, 84, 5, 5, 7]]         o: 0
i: [[0, 2, 4, 8, 4, 1, 4, 9]]           o: 1
i: [[3, 2, 21, 91, 2, 8, 8, 9]]         o: 2
i: [[6, 8, 8, 41, 4, 8, 6, 23]]         o: 3
i: [[96, 5, 8, 8, 8, 5, 8, 9]]          o: 4
i: [[1, 9, 9, 9, 8, 9, 9, 6, 5]]        o: 5
i: [[8, 3, 5]]                          o: 1
i: [[2]]                                o: 0
i: [[7, 7, 7, 4, 3, 9, 2]]              o: 2
i: [[9, 9, 9, 2, 84, 9, 9, 9, 9]]       o: 6

program:  a <- [int] | b <- tail a | c <- last a | d <- count c b
i: [[59, 6, 4, 5, 5, 5, 1, 5]]          o: 4
i: [[82, 5, 6]]                         o: 1
i: [[2]]                                o: 0
i: [[7, 4, 4, 2, 1, 5, 3, 5]]           o: 2
i: [[3, 0, 3, 49, 2, 7, 5, 0, 0]]       o: 3
i: [[1, 8, 8, 8, 8, 4, 8]]              o: 5
i: [[9, 3, 3, 1, 37, 3, 3, 3]]          o: 5
i: [[4]]                                o: 0
i: [[6, 7, 3, 0, 1, 86, 4, 2, 2]]       o: 2
i: [[0]]                                o: 0

program:  a <- [int] | b <- tail a | c <- len b | d <- count c b
i: [[2, 3, 7, 4, 3, 8, 4, 82]]          o: 1
i: [[3, 8, 0, 6]]                       o: 0
i: [[0, 6, 0, 5, 7, 8, 8, 5, 5]]        o: 2
i: [[9, 6, 1, 8, 16, 3, 8, 8, 2]]       o: 3
i: [[7, 8, 9, 7, 5, 8, 8, 8, 6]]        o: 4
i: [[5, 7, 4, 7, 7, 2, 7, 7]]           o: 5
i: [[2, 9, 7, 7, 72, 9, 46, 1]]         o: 2
i: [[3, 2, 7, 7, 5, 6]]                 o: 1
i: [[6, 4, 8, 7]]                       o: 0
i: [[5, 4, 3, 6]]                       o: 1

program:  a <- [int] | b <- tail a | c <- head b | d <- count c b
i: [[9, 9, 7, 9, 19, 2]]                o: 2
i: [[0, 6, 0, 2]]                       o: 1
i: [[20]]                               o: 0
i: [[4, 8, 9, 3, 0, 5, 8, 8]]           o: 3
i: [[7, 0, 4, 0, 0, 92, 1, 0, 1]]       o: 4
i: [[7, 6, 6, 6, 6, 9, 4, 6, 0]]        o: 5
i: [[4, 4, 5, 79, 7, 4, 4, 7]]          o: 3
i: [[4]]                                o: 0
i: [[7, 2, 2, 0, 2, 42, 2, 2, 9]]       o: 5
i: [[3]]                                o: 0

program:  a <- [int] | b <- tail a | c <- last b | d <- count c b
i: [[2, 25, 6, 3, 5, 7, 5, 8]]            o: 1
i: [[67, 1, 9, 69, 4, 1, 4]]              o: 2
i: [[6]]                                  o: 0
i: [[62, 7, 8, 6, 8, 84, 52, 1, 8]]       o: 3
i: [[4, 6, 1, 6, 7, 6, 1, 6]]             o: 4
i: [[4, 82, 7, 7, 5, 7, 2, 7, 7]]         o: 5
i: [[3]]                                  o: 0
i: [[7, 2, 7, 6, 1, 2]]                   o: 2
i: [[3]]                                  o: 0
i: [[95, 1, 1, 2, 1, 7, 1, 1]]            o: 5

program:  a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a
i: [[61, 4, 81]]                          o: 0
i: [[7, 7, 3, 8, 4]]                      o: 1
i: [[3, 4, 9, 5, 5, 6, 8, 4]]             o: 2
i: [[7, 1, 9, 9, 6, 9, 6]]                o: 3
i: [[7, 37, 10, 7, 34, 6, 5, 7, 7]]       o: 4
i: [[9, 9, 2, 9, 9, 8, 7, 9]]             o: 5
i: [[4, 2, 5, 1, 6, 8, 2]]                o: 1
i: [[6, 0, 6]]                            o: 0
i: [[4, 2, 3, 4, 4, 4, 4]]                o: 5
i: [[7, 5, 8]]                            o: 0

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

./taskg  38.44s user 0.19s system 100% cpu 38.374 total
```