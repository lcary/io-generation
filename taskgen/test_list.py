from taskgen.constraints import verify_io_pairs
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, test_sample


def test_sum_top_index_sorted():
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    program, samples = generate_interesting(source, N=10)
    sample = ((2, [3, 5, 4, 7, 5]), 7)
    test_sample(sample, program)
    return program, samples


def test_head():
    V = 512
    source = "a <- [int] | b <- head a"
    language = get_list_dsl(V)
    program, samples = generate_interesting(source, N=10, V=V, language=language)
    sample = (([3, 5, 4, 7, 5],), 3)
    test_sample(sample, program)
    return program, samples


def test_tail():
    V = 512
    source = "a <- [int] | b <- tail a"
    language = get_list_dsl(V)
    program, samples = generate_interesting(source, N=10, V=V, language=language)
    sample = (([3, 5, 4, 7, 5],), [5, 4, 7, 5])
    test_sample(sample, program)
    return program, samples


def test_count_head_in_tail():
    """
    count (head xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- head a | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 0)
    test_sample(sample, program)
    sample = (([5, 4, 7, 5],), 1)
    test_sample(sample, program)
    sample = (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 3)
    test_sample(sample, program)
    return program, samples


def test_count_len_in_tail():
    """
    count (len xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- len a | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 2)
    test_sample(sample, program)
    sample = (([5, 4, 7, 5],), 1)
    test_sample(sample, program)
    sample = (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0)
    test_sample(sample, program)
    return program, samples


def test_count_last_in_tail():
    """
    count (last xs) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- last a | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 2)
    test_sample(sample, program)
    return program, samples


def test_count_len_tail_in_tail():
    """
    count (len (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- len b | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 1)
    test_sample(sample, program)
    return program, samples


def test_count_head_tail_in_tail():
    """
    count (head (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- head b | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 2)
    test_sample(sample, program)
    return program, samples


def test_count_last_tail_in_tail():
    """
    count (last (tail xs)) (tail xs)
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- last b | d <- count c b"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 2)
    test_sample(sample, program)
    return program, samples


def test_count_head_tail_tail_tail_in_list():
    """
    count (head (tail (tail (tail xs)))) xs
    """
    V = 512
    language = get_list_dsl(V)
    source = "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a"
    program, samples = generate_interesting(
        source, N=10, V=V, maxv=10, min_io_len=3, max_io_len=10, language=language, min_variance=3.5
    )
    sample = (([3, 5, 4, 7, 5],), 1)
    test_sample(sample, program)
    return program, samples


def run_tests():
    program, io_pairs = test_sum_top_index_sorted()
    verify_io_pairs(io_pairs, in_type=[int, [int]], out_type=int)
    program, io_pairs = test_head()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=[int])
    program, io_pairs = test_count_head_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_len_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_last_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_len_tail_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_head_tail_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_last_tail_in_tail()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)
    program, io_pairs = test_count_head_tail_tail_tail_in_list()
    verify_io_pairs(io_pairs, in_type=[int], out_type=int)


if __name__ == "__main__":
    run_tests()
