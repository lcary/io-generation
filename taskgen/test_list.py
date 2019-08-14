from taskgen.constraints import verify_types
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, test_io


def test_sum_top_index_sorted():
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    program, io_pairs = generate_interesting(source, num_examples=10)
    verify_types(io_pairs, sig=([int, [int]], int))
    test_io(program, ((2, [3, 5, 4, 7, 5]), 7))
    return program, io_pairs


def _generate_interesting(*args, **kwargs):
    """ Run IO generation with default bounds and language. """
    kwargs["min_bound"] = kwargs.get("min_bound", 0)
    kwargs["max_bound"] = kwargs.get("max_bound", 10)
    kwargs["language"] = kwargs.get("language", get_list_dsl(kwargs["max_bound"]))
    return generate_interesting(*args, **kwargs)


def test_head():
    source = "a <- [int] | b <- head a"
    program, io_pairs = _generate_interesting(source, num_examples=10)
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 3))
    return program, io_pairs


def test_tail():
    source = "a <- [int] | b <- tail a"
    program, io_pairs = _generate_interesting(source, num_examples=10)
    verify_types(io_pairs, sig=([int], [int]))
    test_io(program, (([3, 5, 4, 7, 5],), [5, 4, 7, 5]))
    return program, io_pairs


def test_count_head_in_tail():
    """
    count (head xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
    program, io_pairs = _generate_interesting(source, num_examples=10, min_variance=3.5)
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 0))
    test_io(program, (([5, 4, 7, 5],), 1))
    test_io(program, (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3))
    return program, io_pairs


def test_count_len_in_tail():
    """
    count (len xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 2))
    test_io(program, (([5, 4, 7, 5],), 1))
    test_io(program, (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0))
    return program, io_pairs


def test_count_last_in_tail():
    """
    count (last xs) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 2))
    return program, io_pairs


def test_count_len_tail_in_tail():
    """
    count (len (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 1))
    return program, io_pairs


def test_count_head_tail_in_tail():
    """
    count (head (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 2))
    return program, io_pairs


def test_count_last_tail_in_tail():
    """
    count (last (tail xs)) (tail xs)
    """
    source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 2))
    return program, io_pairs


def test_count_head_tail_tail_tail_in_list():
    """
    count (head (tail (tail (tail xs)))) xs
    """
    source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
    program, io_pairs = _generate_interesting(
        source, num_examples=10, maxv=10, min_io_len=3, max_io_len=10, min_variance=3.5
    )
    verify_types(io_pairs, sig=([int], int))
    test_io(program, (([3, 5, 4, 7, 5],), 1))
    return program, io_pairs


def test_count_n():
    source = "a <- int | b <- [int] | c <- count a b"
    program, io_pairs = _generate_interesting(source, num_examples=10)
    verify_types(io_pairs, sig=([int, [int]], int))
    test_io(program, ((3, [3, 5, 4, 7, 5]), 1))
    return program, io_pairs


def run_tests():
    test_sum_top_index_sorted()
    test_head()
    test_tail()
    test_count_head_in_tail()
    test_count_len_in_tail()
    test_count_last_in_tail()
    test_count_len_tail_in_tail()
    test_count_head_tail_in_tail()
    test_count_last_tail_in_tail()
    test_count_head_tail_tail_tail_in_list()
    test_count_n()


if __name__ == "__main__":
    run_tests()
