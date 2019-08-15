import random
import time
from collections import Counter

import numpy as np
from tqdm import tqdm

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


BIAS_MAX = 10
BIAS_AMOUNT = 0.98


def biased_randint(minv, maxv, bias_max=BIAS_MAX, bias_amount=BIAS_AMOUNT):
    """
    Biases random selection for numbers under bias_max in range(minv, maxv).

    Example benchmarks for range(0, 99) and bias_max=10 showing average likelihood
    of N being under 11.

        for bias in [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]:
            ns = []
            for i in range(50):
                xs = [biased_randint(0, 99, bias_amount=bias) for _ in range(1000)]
                ns.append(len([i for i in xs if i <= 10]) / 1000.0)
            print("bias={}: ".format(bias), sum(ns) / float(len(ns)))

        bias=0.9:  0.5008400000000001
        bias=0.91:  0.5370600000000002
        bias=0.92:  0.56798
        bias=0.93:  0.6042799999999998
        bias=0.94:  0.6418
        bias=0.95:  0.6832600000000001
        bias=0.96:  0.7304999999999999
        bias=0.97:  0.7899200000000001
        bias=0.98:  0.84718
        bias=0.99:  0.9166199999999999
    """
    if maxv <= bias_max or minv >= bias_max:
        return np.random.randint(minv, maxv)
    probs = get_biased_probabilities(minv, maxv, bias_max, bias_amount)
    res = np.random.multinomial(1, probs)
    return np.argmax(res).item()


def biased_randint_list(
    minv, maxv, array_size, bias_max=BIAS_MAX, bias_amount=BIAS_AMOUNT
):
    """
    Similar to biased_randint but for lists of ints.

        for bias in [0.90, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]:
            ns = []
            for i in range(50):
                xs = biased_randint_list(0, 99, 1000, bias_amount=bias)
                ns.append(len([i for i in xs if i <= 10]) / 1000.0)
            print("bias={}: ".format(bias), sum(ns) / float(len(ns)))

        bias=0.9:  0.5077799999999999
        bias=0.91:  0.5371400000000001
        bias=0.92:  0.5693199999999998
        bias=0.93:  0.6054799999999998
        bias=0.94:  0.6395200000000001
        bias=0.95:  0.6826999999999999
        bias=0.96:  0.7343799999999997
        bias=0.97:  0.7850799999999998
        bias=0.98:  0.8470199999999999
        bias=0.99:  0.9174999999999999
    """
    if maxv <= bias_max or minv >= bias_max:
        return [i.item() for i in np.random.randint(minv, maxv, size=array_size)]
    probs = get_biased_probabilities(minv, maxv, bias_max, bias_amount)
    res = np.random.multinomial(array_size, probs, size=1)
    vals = []
    for (i, v) in enumerate(res[0]):
        for j in range(v):
            vals.append(i)
    random.shuffle(vals)
    return vals


def get_biased_probabilities(minv, maxv, bias_max=BIAS_MAX, bias_amount=BIAS_AMOUNT):
    probs = []
    for i in range(maxv):
        if i < minv:
            probs.append(0)
        elif i >= bias_max:
            probs.append(1.0 - bias_amount)
        else:
            probs.append(bias_amount)
    s = sum(probs)
    return [i / s for i in probs]


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
                input_value[a] = biased_randint(minv, maxv)
            elif input_types[a] == [int]:
                array_size = np.random.randint(min_len, max_len)
                input_value[a] = biased_randint_list(minv, maxv, array_size)
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
):
    """
    Compile a program and generates interesting IO pairs.
    Returns output as a dictionary.
    """

    if language is None:
        language, _ = get_linq_dsl(max_bound, min_bound=min_bound)

    t = time.time()
    source = source.replace(" | ", "\n")
    program = compile_program(
        language, source, max_bound=max_bound, L=maxv, min_bound=min_bound
    )

    interesting = False
    hit_timeout = False
    io_pairs = []

    elapsed = time.time() - t
    tqdm.write("program: {}".format(source.replace("\n", " | ")))
    pbar = tqdm(total=timeout, desc="IO For Program", unit="sec")

    samples = 0
    last_progress = 0
    last_elapsed = 0

    while not interesting and not hit_timeout:
        latest_io_pairs = generate_io_pairs(
            program,
            num_examples=num_examples,
            max_bound=max_bound,
            min_len=min_io_len,
            max_len=max_io_len,
        )
        samples += len(latest_io_pairs)
        io_pairs.extend(latest_io_pairs)
        io_pairs = reduce_io_pairs(io_pairs, num_examples)
        if is_interesting(io_pairs, min_variance):
            interesting = True
        elapsed = time.time() - t
        if elapsed > timeout:
            hit_timeout = True

        n = elapsed - last_elapsed
        last_elapsed = elapsed

        pbar.set_postfix(io_samples=samples, refresh=False)
        pbar.update(n)

    pbar.update(100 - last_progress)
    pbar.close()

    return format_examples(program, io_pairs, elapsed, timeout, hit_timeout, samples)


def format_examples(program, io_pairs, elapsed, timeout, hit_timeout, samples):
    return {
        "program": program,
        "io_pairs": [{"i": i, "o": o} for (i, o) in io_pairs],
        "output_variance": get_output_variance(get_outputs(io_pairs)),
        "runtime_seconds": elapsed,
        "timeout": timeout,
        "hit_timeout": hit_timeout,
        "samples": samples,
    }


def reduce_io_pairs(io_pairs, num_examples):
    remove_indices = find_duplicates(io_pairs)
    max_remove = len(io_pairs) - num_examples
    remove_indices = remove_indices[:max_remove]
    io_pairs = [s for i, s in enumerate(io_pairs) if i not in remove_indices]
    # truncate list to handle case of no duplicates
    io_pairs = io_pairs[:num_examples]
    return io_pairs


def occurs_frequently(counter, val):
    avg = sum(counter.values()) / float(len(counter))
    return counter[val] > avg


def find_duplicates(io_pairs):
    """
    Returns a list of indices for duplicate output values, where indices at the beginning of the
    list are for outputs that appear as duplicates more frequently than outputs for indices at
    the end of the list.
    """
    seen = Counter()
    remove_indices = []
    for (index, pair) in enumerate(io_pairs):
        o = str(pair[1])
        if o in seen:
            if occurs_frequently(seen, o):
                # remove this first, since it's so common
                remove_indices.insert(0, index)
            else:
                remove_indices.append(index)
        seen[o] += 1
    return remove_indices


def test_io(program, io_pair):
    try:
        assert program.fun(io_pair[0]) == io_pair[1]
    except AssertionError as e:
        print("ERROR: evaluation result discrepancy")
        print("input:  ", io_pair[0])
        print("expect: ", io_pair[1])
        print("actual: ", program.fun(io_pair[0]))
        raise e


def pretty_print_results(d, margin=7, debug=False):
    print("program: ", d["program"].src.replace("\n", " | "))
    inputs = [v for pair in d["io_pairs"] for k, v in pair.items() if k == "i"]
    col_width = max(len(str(v)) for v in inputs) + margin
    for io_pair in d["io_pairs"]:
        i = str(io_pair["i"])
        o = str(io_pair["o"])
        print("i: " + i.ljust(col_width) + "o: " + o)
    if d["hit_timeout"]:
        print(
            "WARN: Timeout hit while finding most interesting io_pairs for above program."
        )
    if debug:
        print(
            (
                "output variance: ",
                d["output_variance"],
                "runtime (seconds): ",
                d["runtime_seconds"],
            )
        )
    print()
