import time

import numpy as np

from taskgen.compiler import compile_program
from taskgen.constraints import is_int
from taskgen.dsl.linq import get_linq_dsl


def get_inputs(samples):
    return [p[0] for p in samples]


def get_outputs(samples):
    return [p[1] for p in samples]


def get_output_variance(outputs):
    if not outputs:
        # empty list
        return None
    o = outputs[0]
    if is_int(o):
        pass
    elif isinstance(o, list) and all(not i for i in outputs):
        # all empty lists
        return None
    elif isinstance(o, list) and any(is_int(i) for l in outputs for i in l):
        # is list[int]
        outputs = list(map(sum, outputs))
    else:
        raise ValueError("Unsupported output type for outputs ({})".format(outputs))
    return np.var(outputs)


def is_interesting(samples, min_variance):
    outputs = get_outputs(samples)
    output_var = get_output_variance(outputs)
    if output_var is None:
        return False
    return output_var >= min_variance


def generate_io_pairs(
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


def generate_interesting(
    source,
    N=5,
    V=512,
    maxv=10,
    min_io_len=1,
    max_io_len=10,
    min_variance=1.0,
    timeout=5.0,
    language=None,
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
        latest_samples = generate_io_pairs(
            program, N=N, V=V, min_len=min_io_len, max_len=max_io_len
        )
        samples.extend(latest_samples)
        samples = reduce_samples(samples, N)
        elapsed = time.time() - t
        if is_interesting(samples, min_variance):
            interesting = True
    print(("time:", elapsed))
    print(program)
    if not interesting:
        print("WARN: Timeout hit while finding most samples.")
    print("samples:")
    for s in samples:
        print("    {}".format(s))
    print("output variance: ", get_output_variance(get_outputs(samples)))
    return program, samples


def reduce_samples(samples, N):
    remove_indices = find_duplicates(samples)
    max_remove = len(samples) - N
    remove_indices = remove_indices[:max_remove]
    samples = [s for i, s in enumerate(samples) if i not in remove_indices]
    # truncate list to handle case of no duplicates
    samples = samples[:N]
    return samples


def find_duplicates(samples):
    seen = set()
    remove_indices = []
    for (index, pair) in enumerate(samples):
        o = str(pair[1])
        if o in seen:
            remove_indices.append(index)
            continue
        else:
            seen.add(o)
    return remove_indices


def test_sample(sample, program):
    try:
        assert program.fun(sample[0]) == sample[1]
    except AssertionError as e:
        print("ERROR: evaluation result discrepancy")
        print("input:  ", sample[0])
        print("expect: ", sample[1])
        print("actual: ", program.fun(sample[0]))
        raise e
