import unittest

from taskgen.constraints import verify_types
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import test_io, generate_interesting


def generate_examples(*args, **kwargs):
    kwargs.update(
        {
            "num_examples": kwargs.get("num_examples", 10),
            "timeout": kwargs.get("timeout", 10),
            "min_bound": kwargs.get("min_bound", 0),
            "max_bound": kwargs.get("max_bound", 10),
            "min_variance": kwargs.get("min_variance", 1.0),
            "maxv": kwargs.get("maxv", 10),
            "max_io_len": kwargs.get("max_io_len", 10),
        }
    )
    language = get_list_dsl(kwargs["max_bound"])
    return generate_interesting(language, *args, **kwargs)


class TestListDSL(unittest.TestCase):
    def test_list_head(self):
        source = "a <- [int] | b <- head a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 3))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_tail(self):
        source = "a <- [int] | b <- tail a"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], [int]))
        test_io(program, (([3, 5, 4, 7, 5],), [5, 4, 7, 5]))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_head_in_tail(self):
        """
        count (head xs) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 0))
        test_io(program, (([5, 4, 7, 5],), 1))
        test_io(program, (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_len_in_tail(self):
        """
        count (len xs) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 2))
        test_io(program, (([5, 4, 7, 5],), 1))
        test_io(program, (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_last_in_tail(self):
        """
        count (last xs) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 2))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_len_tail_in_tail(self):
        """
        count (len (tail xs)) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 1))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_head_tail_in_tail(self):
        """
        count (head (tail xs)) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 2))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_last_tail_in_tail(self):
        """
        count (last (tail xs)) (tail xs)
        """
        source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
        d = generate_examples(source)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 2))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_head_tail_tail_tail(self):
        """
        count (head (tail (tail (tail xs)))) xs
        """
        source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
        d = generate_examples(source, min_io_len=3)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int], int))
        test_io(program, (([3, 5, 4, 7, 5],), 1))
        self.assertEqual(program.bounds, [(0, 10)])

    def test_list_count_n(self):
        source = "a <- int | b <- [int] | c <- count a b"
        d = generate_examples(source, min_variance=3.5)
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int, [int]], int))
        test_io(program, ((3, [3, 5, 4, 7, 5]), 1))
        self.assertEqual(program.bounds, [(0, 10), (0, 10)])

    def test_fail_bad_min_bound(self):
        source = "a <- [int] | b <- head a"
        with self.assertRaises(AttributeError):
            generate_examples(source, min_bound=100)


if __name__ == "__main__":
    unittest.main()
