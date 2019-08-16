import unittest

from iogen.constraints import verify_types
from iogen.dsl.linq import get_linq_dsl
from iogen.dsl.simple import get_list_dsl
from iogen.io import test_io, generate_interesting


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


class TestLinqDSL(unittest.TestCase):
    def test_linq_sum_top_index_sorted(self):
        max_bound = 512
        min_bound = None
        language, _ = get_linq_dsl(max_bound=max_bound, min_bound=min_bound)
        source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
        d = generate_interesting(
            language,
            source,
            num_examples=10,
            timeout=10,
            min_bound=min_bound,
            max_bound=max_bound,
            min_variance=3.5,
            maxv=10,
            max_io_len=10,
        )
        program = d["program"]
        verify_types(d["io_pairs"], sig=([int, [int]], int))
        test_io(program, ((2, [3, 5, 4, 7, 5]), 7))
        self.assertEqual(program.bounds, [(0, 10), (-50, 51)])


if __name__ == "__main__":
    unittest.main()
