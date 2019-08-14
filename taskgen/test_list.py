from taskgen.constraints import verify_io_pairs
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, test_io_pair


def test_sum_top_index_sorted():
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    program, io_pairs = generate_interesting(source, N=10)
    verify_io_pairs(io_pairs, sig=([int, [int]], int))
    io_pair = ((2, [3, 5, 4, 7, 5]), 7)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_head():
    V = 512
    source = "a <- [int] | b <- head a"
    language = get_list_dsl(V)
    program, io_pairs = generate_interesting(source, N=10, V=V, language=language)
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 3)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_tail():
    V = 512
    source = "a <- [int] | b <- tail a"
    language = get_list_dsl(V)
    program, io_pairs = generate_interesting(source, N=10, V=V, language=language)
    verify_io_pairs(io_pairs, sig=([int], [int]))
    io_pair = (([3, 5, 4, 7, 5],), [5, 4, 7, 5])
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_head_in_tail():
    """
    count (head xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 0)
    test_io_pair(io_pair, program)
    io_pair = (([5, 4, 7, 5],), 1)
    test_io_pair(io_pair, program)
    io_pair = (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_len_in_tail():
    """
    count (len xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 2)
    test_io_pair(io_pair, program)
    io_pair = (([5, 4, 7, 5],), 1)
    test_io_pair(io_pair, program)
    io_pair = (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_last_in_tail():
    """
    count (last xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 2)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_len_tail_in_tail():
    """
    count (len (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 1)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_head_tail_in_tail():
    """
    count (head (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 2)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_last_tail_in_tail():
    """
    count (last (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
    program, io_pairs = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 2)
    test_io_pair(io_pair, program)
    return program, io_pairs


def test_count_head_tail_tail_tail_in_list():
    """
    count (head (tail (tail (tail xs)))) xs
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
    program, io_pairs = generate_interesting(
        source,
        N=10,
        V=V,
        maxv=10,
        min_io_len=3,
        max_io_len=10,
        language=language,
        min_variance=3.5,
    )
    verify_io_pairs(io_pairs, sig=([int], int))
    io_pair = (([3, 5, 4, 7, 5],), 1)
    test_io_pair(io_pair, program)
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


if __name__ == "__main__":
    run_tests()
