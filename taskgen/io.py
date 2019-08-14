import time

import numpy as np

from taskgen.compiler import compile_program
from taskgen.constraints import is_int
from taskgen.dsl.linq import get_linq_dsl


def get_inputs(io_pairs):
    return [p[0] for p in io_pairs]


def get_outputs(io_pairs):
    return [p[1] for p in io_pairs]


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


def is_interesting(io_pairs, min_variance):
    outputs = get_outputs(io_pairs)
    output_var = get_output_variance(outputs)
    if output_var is None:
        return False
    return output_var >= min_variance


def generate_io_pairs(
    program, num_examples, max_bound, min_len=1, max_len=10
):  # TODO: allow empty lists
    """
    Given a program, randomly generates N input-output examples according to constraints.
    If an argument type or value in an argument is an integer, pick a random int within bounds.
    If an argument type is a list, randomize the list length according to min/max parameters.
    """
    input_types = program.ins
    input_nargs = len(input_types)
    io_pairs = []
    for _ in range(num_examples):
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
        io_pairs.append((input_value, output_value))
        assert (
            (program.out == int and output_value <= max_bound)
            or (program.out == [int] and len(output_value) == 0)
            or (program.out == [int] and max(output_value) <= max_bound)
        )
    return io_pairs


def generate_interesting(
    source,
    num_examples=5,
    max_bound=512,
    maxv=10,
    min_io_len=1,
    max_io_len=10,
    min_variance=1.0,
    timeout=5.0,
    language=None,
    min_bound=None,
    debug=False,
):
    if language is None:
        language, _ = get_linq_dsl(max_bound, min_bound=min_bound)

    t = time.time()
    source = source.replace(" | ", "\n")
    program = compile_program(
        language, source, max_bound=max_bound, L=maxv, min_bound=min_bound
    )
    interesting = False
    elapsed = time.time() - t
    io_pairs = []
    while not interesting and elapsed < timeout:
        latest_io_pairs = generate_io_pairs(
            program,
            num_examples=num_examples,
            max_bound=max_bound,
            min_len=min_io_len,
            max_len=max_io_len,
        )
        io_pairs.extend(latest_io_pairs)
        io_pairs = reduce_io_pairs(io_pairs, num_examples)
        elapsed = time.time() - t
        if is_interesting(io_pairs, min_variance):
            interesting = True
    if debug:
        print(("time:", elapsed))
    print(program)
    if not interesting:
        print("WARN: Timeout hit while finding most io_pairs.")
    print("io_pairs:")
    for s in io_pairs:
        print("    {}".format(s))
    if debug:
        print("output variance: ", get_output_variance(get_outputs(io_pairs)))
    return program, io_pairs


def reduce_io_pairs(io_pairs, num_examples):
    remove_indices = find_duplicates(io_pairs)
    max_remove = len(io_pairs) - num_examples
    remove_indices = remove_indices[:max_remove]
    io_pairs = [s for i, s in enumerate(io_pairs) if i not in remove_indices]
    # truncate list to handle case of no duplicates
    io_pairs = io_pairs[:num_examples]
    return io_pairs


def find_duplicates(io_pairs):
    seen = set()
    remove_indices = []
    for (index, pair) in enumerate(io_pairs):
        o = str(pair[1])
        if o in seen:
            remove_indices.append(index)
            continue
        else:
            seen.add(o)
    return remove_indices


def test_io_pair(io_pair, program):
    try:
        assert program.fun(io_pair[0]) == io_pair[1]
    except AssertionError as e:
        print("ERROR: evaluation result discrepancy")
        print("input:  ", io_pair[0])
        print("expect: ", io_pair[1])
        print("actual: ", program.fun(io_pair[0]))
        raise e
