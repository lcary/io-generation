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
        source = "a <- [int] | b <- tail a | c <- unique b | d <- last c | e <- count d b"
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


if __name__ == "__main__":
    unittest.main()
