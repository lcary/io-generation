import unittest

from iogen.constraints import verify_types
from iogen.dsl.extended import get_extended_dsl
from iogen.io import test_io, generate_interesting


def generate_examples(*args, **kwargs):
    kwargs.update(
        {
            "num_examples": kwargs.get("num_examples", 10),
            "timeout": kwargs.get("timeout", 10),
            "min_bound": kwargs.get("min_bound", 0),
            "max_bound": kwargs.get("max_bound", 10),
            "min_variance": kwargs.get("min_variance", 0.0),
            "maxv": kwargs.get("maxv", 10),
            "max_io_len": kwargs.get("max_io_len", 10),
        }
    )
    language = get_extended_dsl(kwargs["max_bound"])
    return generate_interesting(language, *args, **kwargs)


class TestExtendedDSL(unittest.TestCase):
    def test_add_last(self):
        source = "a <- [int] | b <- int | c <- last a | d <- + b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], int))
        test_io(program, (([3, 5, 4, 7, 5], 5), 10))
        self.assertEqual(program.bounds, [(1, 5), (1, 5)])

    def test_subtract_head(self):
        source = "a <- [int] | b <- int | c <- head a | d <- - c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], int))
        test_io(program, ([[7, 8, 22, 1, 2, 33], 5], 2))
        self.assertEqual(program.bounds, [(1, 5), (1, 5)])

    # TODO: fix
    # def test_multiply_n(self):
    #     source = "a <- int | b <- * a a"
    #     d = generate_examples(source, maxv=10, max_bound=300, min_bound=1)
    #     program = d["program"]
    #     verify_types(d["io_pairs"], sig=(int, int))
    #     test_io(program, ([5,], 10))
    #     self.assertEqual(program.bounds, [(1, 5), (1, 5)])

    def test_last_sorted(self):
        source = "a <- [int] | b <- int | c <- sort a | d <- last c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], int))
        test_io(program, (([3, 5, 4, 7, 5], 5), 7))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_sum(self):
        source = "a <- [int] | b <- sum a"
        d = generate_examples(source, max_bound=99)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int]))
        test_io(program, (([3, 5, 4, 7, 5],), 24))
        self.assertEqual(program.bounds, [(1, 9)])

    def test_add_sum(self):
        source = "a <- [int] | b <- int | c <- sum a | d <- + c b"
        d = generate_examples(source, max_bound=99, min_io_len=3)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], int))
        test_io(program, (([3, 5, 4, 7, 5], 3), 27))
        self.assertEqual(program.bounds, [(1, 4), (1, 49)])

    def test_count_index(self):
        source = "a <- [int] | b <- int | c <- index b a | d <- count c a"
        d = generate_examples(source, min_io_len=3)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], int))
        test_io(program, (([3, 5, 4, 7, 5], 1), 2))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_count_uniques(self):
        source = (
            "a <- [int] | b <- tail a | c <- unique b | d <- last c | e <- count d b"
        )
        d = generate_examples(source, min_io_len=3)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 1))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_sort(self):
        source = "a <- [int] | b <- sort a"
        d = generate_examples(source, min_io_len=3)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], [int]))
        test_io(program, (([3, 5, 4, 7, 5],), [3, 4, 5, 5, 7]))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_map_add_n(self):
        source = "a <- [int] | b <- int | c <- map(+) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        test_io(program, ([[7, 8, 22, 1, 2, 33], 5], [12, 13, 27, 6, 7, 38]))
        self.assertEqual(program.bounds, [(1, 5), (1, 5)])

    def test_map_subtract_n(self):
        source = "a <- [int] | b <- int | c <- map(-) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        test_io(program, ([[7, 8, 22, 33], 5], [2, 3, 17, 28]))
        self.assertEqual(program.bounds, [(1, 5), (1, 5)])

    def test_last_gte(self):
        source = "a <- [int] | b <- int | c <- last a | d <- >= b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[6, 0, 3], 3]
        o = True
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_last_lt(self):
        source = "a <- [int] | b <- int | c <- last a | d <- < b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[3, 0, 2, 7, 1, 8, 2], 88]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_last_lte(self):
        source = "a <- [int] | b <- int | c <- last a | d <- <= b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[0, 1, 3, 7, 15, 9, 8, 0], 3]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_last_gt(self):
        source = "a <- [int] | b <- int | c <- last a | d <- > b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[1, 8, 2, 2, 61, 0, 9], 0]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_last_eq(self):
        source = "a <- [int] | b <- int | c <- last a | d <- == b c"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[4, 8, 4, 52, 5, 4], 56]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_even(self):
        source = "a <- [int] | b <- int | c <- even? b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[57, 6], 6]
        o = True
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_odd(self):
        source = "a <- [int] | b <- int | c <- odd? b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[6], 2]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_neg(self):
        source = "a <- [int] | b <- int | c <- negative? b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[5], 2]
        o = False
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_pos(self):
        source = "a <- [int] | b <- int | c <- positive? b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], bool))
        i = [[4, 2], 5]
        o = True
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_gte(self):
        source = "a <- [int] | b <- int | c <- filter(>=) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        i = [[4], 8]
        o = []
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_lt(self):
        source = "a <- [int] | b <- int | c <- filter(<) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        i = [[9, 1, 7, 4, 5, 7, 85, 4], 9]
        o = [1, 7, 4, 5, 7, 4]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_lte(self):
        source = "a <- [int] | b <- int | c <- filter(<=) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        i = [[6, 0, 51, 9], 6]
        o = [6, 0]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_gt(self):
        source = "a <- [int] | b <- int | c <- filter(>) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        i = [[2, 7, 60, 31, 0, 5, 7, 75], 9]
        o = [60, 31, 75]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_eq(self):
        source = "a <- [int] | b <- int | c <- filter(==) b a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([[int], int], [int]))
        i = [[7, 0, 6, 8, 9, 6, 70, 3, 9], 8]
        o = [8]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_filter_even(self):
        source = "a <- [int] | b <- filter(even?) a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], [int]))
        i = [[2, 6]]
        o = [2, 6]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_filter_odd(self):
        source = "a <- [int] | b <- filter(odd?) a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], [int]))
        i = [[8, 7, 20, 1, 8]]
        o = [7, 1]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_filter_pos(self):
        source = "a <- [int] | b <- filter(positive?) a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], [int]))
        i = [[9, 0, 1, 3]]
        o = [9, 1, 3]
        test_io(program, (i, o))
        self.assertEqual(program.bounds, [(0, 10)])


if __name__ == "__main__":
    unittest.main()
