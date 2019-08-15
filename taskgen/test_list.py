import argparse

from taskgen.constraints import verify_types
from taskgen.dsl.linq import get_linq_dsl
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, test_io, pretty_print_results

DEFAULT_MAXV = 99


def generate_examples(*args, **kwargs):
    """
    Run IO generation with defaults and pretty print the results.
    """
    cli_args = kwargs.pop('cli_args')
    kwargs.update(
        {
            "num_examples": kwargs.get("num_examples", cli_args.num_examples),
            "timeout": kwargs.get("timeout", cli_args.timeout),
            "min_bound": kwargs.get("min_bound", cli_args.min_bound),
            "max_bound": kwargs.get("max_bound", cli_args.max_bound),
            "min_variance": kwargs.get("min_variance", cli_args.min_variance),
            "maxv": kwargs.get("maxv", cli_args.maxv),
            "max_io_len": kwargs.get("max_io_len", cli_args.max_io_len),
        }
    )
    kwargs["language"] = kwargs.get("language", get_list_dsl(kwargs["max_bound"]))
    d = generate_interesting(*args, **kwargs)
    pretty_print_results(d)
    return d


def test_linq_sum_top_index_sorted(args):
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    language, _ = get_linq_dsl(512)
    d = generate_interesting(source, max_bound=512, min_bound=None, language=language)
    verify_types(d["io_pairs"], sig=([int, [int]], int))
    test_io(d["program"], ((2, [3, 5, 4, 7, 5]), 7))


def test_list_head(args):
    source = "a <- [int] | b <- head a"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 3))


def test_list_tail(args):
    source = "a <- [int] | b <- tail a"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], [int]))
    test_io(d["program"], (([3, 5, 4, 7, 5],), [5, 4, 7, 5]))


def test_list_count_head_in_tail(args):
    """
    count (head xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 0))
    test_io(d["program"], (([5, 4, 7, 5],), 1))
    test_io(d["program"], (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3))


def test_list_count_len_in_tail(args):
    """
    count (len xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 2))
    test_io(d["program"], (([5, 4, 7, 5],), 1))
    test_io(d["program"], (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0))


def test_list_count_last_in_tail(args):
    """
    count (last xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 2))


def test_list_count_len_tail_in_tail(args):
    """
    count (len (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 1))


def test_list_count_head_tail_in_tail(args):
    """
    count (head (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 2))


def test_list_count_last_tail_in_tail(args):
    """
    count (last (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
    d = generate_examples(source, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 2))


def test_list_count_head_tail_tail_tail(args):
    """
    count (head (tail (tail (tail xs)))) xs
    """
    source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
    d = generate_examples(source, min_io_len=3, cli_args=args)
    verify_types(d["io_pairs"], sig=([int], int))
    test_io(d["program"], (([3, 5, 4, 7, 5],), 1))


def test_list_count_n(args):
    source = "a <- int | b <- [int] | c <- count a b"
    d = generate_examples(source, min_variance=3.5, cli_args=args)
    verify_types(d["io_pairs"], sig=([int, [int]], int))
    test_io(d["program"], ((3, [3, 5, 4, 7, 5]), 1))


def run_tests():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-examples", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--min-bound", type=int, default=0)
    parser.add_argument("--max-bound", type=int, default=99)
    parser.add_argument("--min-variance", type=float, default=3.5)
    parser.add_argument("--maxv", type=int, default=DEFAULT_MAXV)  # max value in list
    parser.add_argument("--max-io-len", type=int, default=10)
    args = parser.parse_args()

    test_linq_sum_top_index_sorted(args)
    test_list_head(args)
    test_list_tail(args)
    test_list_count_head_in_tail(args)
    test_list_count_len_in_tail(args)
    test_list_count_last_in_tail(args)
    test_list_count_len_tail_in_tail(args)
    test_list_count_head_tail_in_tail(args)
    test_list_count_last_tail_in_tail(args)
    test_list_count_head_tail_tail_tail(args)
    test_list_count_n(args)


if __name__ == "__main__":
    run_tests()
