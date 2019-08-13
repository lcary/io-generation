import time

import numpy as np

from taskgen.constraints import verify_io_pairs
from taskgen.dc import test_program, compile_program
from taskgen.dsl.linq import get_linq_dsl
from taskgen.dsl.simple import get_list_dsl


def test_sample(sample, program, debug=False):
    if debug:
        print("input:  ", sample[0])
        print("expect: ", sample[1])
        print("actual: ", program.fun(sample[0]))
    assert program.fun(sample[0]) == sample[1]


def test_sum_top_index_sorted():
    source = "a <- int | b <- [int] | c <- SORT b | d <- TAKE a c | e <- SUM d"
    program, samples = test_program(source, N=10)
    sample = ((2, [3, 5, 4, 7, 5]), 7)
    test_sample(sample, program)
    return program, samples


def test_head():
    V = 512
    source = "a <- [int] | b <- head a"
    language = get_list_dsl(V)
    program, samples = test_program(source, N=10, V=V, language=language)
    sample = (([3, 5, 4, 7, 5],), 3)
    test_sample(sample, program)
    return program, samples


def test_tail():
    V = 512
    source = "a <- [int] | b <- tail a"
    language = get_list_dsl(V)
    program, samples = test_program(source, N=10, V=V, language=language)
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
    program, samples = generate_interesting_io_examples(source, N=10, V=V, language=language)
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
    program, samples = generate_interesting_io_examples(
        source, N=10, V=V, maxv=10, max_io_len=10, language=language
    )  # TODO: change N to 100
    sample = (([3, 5, 4, 7, 5],), 2)
    test_sample(sample, program)
    sample = (([5, 4, 7, 5],), 1)
    test_sample(sample, program)
    sample = (([7, 4, 7, 8, 21, 1, 7, 2, 7, 5],), 0)
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


def get_inputs(samples):
    return [p[0] for p in samples]


def get_outputs(samples):
    return [p[1] for p in samples]


def is_interesting(samples, min_variance):
    outputs = get_outputs(samples)
    return np.var(outputs) >= min_variance


def generate_mixed_length_io_arrays(
    program, N, V, min_len=1, max_len=10
):  # TODO: allow empty lists
    """ Given a programs, randomly generates N IO examples.
        using the specified length L for the input arrays. """
    input_types = program.ins
    input_nargs = len(input_types)

    # Generate N input-output pairs
    IO = []
    for _ in range(N):
        input_value = [None] * input_nargs
        for a in range(input_nargs):
            minv, maxv = program.bounds[a]
            if input_types[a] == int:
                input_value[a] = np.random.randint(minv, maxv)
            elif input_types[a] == [int]:
                array_size = np.random.randint(min_len, max_len)
                input_value[a] = list(np.random.randint(minv, maxv, size=array_size))
            else:
                raise Exception(
                    "Unsupported input type "
                    + input_types[a]
                    + " for random input generation"
                )
        output_value = program.fun(input_value)
        IO.append((input_value, output_value))
        assert (
            (program.out == int and output_value <= V)
            or (program.out == [int] and len(output_value) == 0)
            or (program.out == [int] and max(output_value) <= V)
        )
    return IO


def generate_interesting_io_examples(
    source, N=5, V=512, maxv=10, max_io_len=10, min_variance=1.0, timeout=10, language=None
):
    if language is None:
        language, _ = get_linq_dsl(V)

    t = time.time()
    source = source.replace(" | ", "\n")
    program = compile_program(language, source, V=V, L=maxv)
    interesting = False
    elapsed = time.time() - t
    samples = []
    while not interesting and elapsed < timeout:
        samples = generate_mixed_length_io_arrays(program, N=N, V=V, max_len=max_io_len)
        elapsed = time.time() - t
        if is_interesting(samples, min_variance):
            interesting = True
    print(("time:", elapsed))
    print(program)
    if not interesting:
        print("No interesting samples.")
    print("samples:")
    for s in samples:
        print("    {}".format(s))
    return program, samples


if __name__ == "__main__":
    run_tests()
