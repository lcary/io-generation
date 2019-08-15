from taskgen.constraints import verify_types
from taskgen.dsl.linq import get_linq_dsl
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, test_io, pretty_print_results

DEFAULT_MAXV = 99


def _generate_interesting(*args, **kwargs):
    """ Run IO generation with default bounds and language. Print results. """
    kwargs["timeout"] = kwargs.get("timeout", 10)
    kwargs["min_bound"] = kwargs.get("min_bound", 0)
    kwargs["max_bound"] = kwargs.get("max_bound", 99)
    kwargs["language"] = kwargs.get("language", get_list_dsl(kwargs["max_bound"]))
    d = generate_interesting(*args, **kwargs)
    pretty_print_results(d)
    return d


def test_linq_sum_top_index_sorted():
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    language, _ = get_linq_dsl(512)
    d = generate_interesting(source, num_examples=10, max_bound=512, min_bound=None, language=language)
    verify_types(d['io_pairs'], sig=([int, [int]], int))
    test_io(d['program'], ((2, [3, 5, 4, 7, 5]), 7))


def test_list_head():
    source = "a <- [int] | b <- head a"
    d = _generate_interesting(source, num_examples=10)
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 3))


def test_list_tail():
    source = "a <- [int] | b <- tail a"
    d = _generate_interesting(source, num_examples=10)
    verify_types(d['io_pairs'], sig=([int], [int]))
    test_io(d['program'], (([3, 5, 4, 7, 5],), [5, 4, 7, 5]))


def test_list_count_head_in_tail():
    """
    count (head xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
    d = _generate_interesting(source, num_examples=10, min_variance=3.5, maxv=DEFAULT_MAXV)
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 0))
    test_io(d['program'], (([5, 4, 7, 5],), 1))
    test_io(d['program'], (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3))


def test_list_count_len_in_tail():
    """
    count (len xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 2))
    test_io(d['program'], (([5, 4, 7, 5],), 1))
    test_io(d['program'], (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0))


def test_list_count_last_in_tail():
    """
    count (last xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 2))


def test_list_count_len_tail_in_tail():
    """
    count (len (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 1))


def test_list_count_head_tail_in_tail():
    """
    count (head (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 2))


def test_list_count_last_tail_in_tail():
    """
    count (last (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 2))


def test_list_count_head_tail_tail_tail():
    """
    count (head (tail (tail (tail xs)))) xs
    """
    source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
    d = _generate_interesting(
        source, num_examples=10, maxv=DEFAULT_MAXV, min_io_len=3, max_io_len=10, min_variance=3.5
    )
    verify_types(d['io_pairs'], sig=([int], int))
    test_io(d['program'], (([3, 5, 4, 7, 5],), 1))


def test_list_count_n():
    source = "a <- int | b <- [int] | c <- count a b"
    d = _generate_interesting(source, num_examples=10, min_variance=3.5)
    verify_types(d['io_pairs'], sig=([int, [int]], int))
    test_io(d['program'], ((3, [3, 5, 4, 7, 5]), 1))


def run_tests():
    test_linq_sum_top_index_sorted()
    test_list_head()
    test_list_tail()
    test_list_count_head_in_tail()
    test_list_count_len_in_tail()
    test_list_count_last_in_tail()
    test_list_count_len_tail_in_tail()
    test_list_count_head_tail_in_tail()
    test_list_count_last_tail_in_tail()
    test_list_count_head_tail_tail_tail()
    test_list_count_n()


if __name__ == "__main__":
    run_tests()
