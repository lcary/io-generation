import unittest

from taskgen.constraints import verify_types
from taskgen.dsl.linq import get_linq_dsl
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import test_io, generate_interesting


def generate_examples(*args, **kwargs):
    kwargs.update(
        {
            "num_examples": kwargs.get("num_examples", 10),
            "timeout": kwargs.get("timeout", 10),
            "min_bound": kwargs.get("min_bound", 0),
            "max_bound": kwargs.get("max_bound", 10),
            "min_variance": kwargs.get("min_variance", 3.5),
            "maxv": kwargs.get("maxv", 10),
            "max_io_len": kwargs.get("max_io_len", 10),
        }
    )
    kwargs["language"] = kwargs.get("language", get_list_dsl(kwargs["max_bound"]))
    return generate_interesting(*args, **kwargs)


class TestLinqDSL(unittest.TestCase):
    def test_linq_sum_top_index_sorted(self):
        max_bound = 512
        min_bound = None
        source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
        language, _ = get_linq_dsl(max_bound)
        d = generate_examples(
            source,
            num_examples=10,
            timeout=10,
            min_bound=min_bound,
            max_bound=max_bound,
            min_variance=3.5,
            maxv=10,
            max_io_len=10,
            language=language,
        )
        verify_types(d["io_pairs"], sig=([int, [int]], int))
        test_io(d["program"], ((2, [3, 5, 4, 7, 5]), 7))


if __name__ == "__main__":
    unittest.main()