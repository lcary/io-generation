from math import sqrt, ceil

from iogen.dsl.types import Function


def sqr_bounds(lower_bound, upper_bound):
    l = max(0, lower_bound)
    u = upper_bound - 1
    if l > u:
        return [(0, 0)]
    return [(-int(sqrt(u)), ceil(sqrt(u + 1)))]


def mul_bounds(lower_bound, upper_bound):
    return sqr_bounds(0, min(-(lower_bound + 1), upper_bound))


def add_sub_bounds(b):
    bounds = (int(b[0] / 2) + 1, int(b[1] / 2))
    return bounds


def get_extended_dsl(max_bound, min_bound=None):
    Null = max_bound
    lambdas = [
        Function(
            "*", (int, int, int), lambda i, j: i * j, lambda b: mul_bounds(b[0], b[1])
        ),
        Function(
            "+",
            (int, int, int),
            lambda i, j: i + j,
            lambda b: [add_sub_bounds(b), add_sub_bounds(b)],
        ),
        Function(
            "-",
            (int, int, int),
            lambda i, j: i - j,
            lambda b: [add_sub_bounds(b), add_sub_bounds(b)],
        ),
    ]
    DSL = [
        Function(
            "head",
            ([int], int),
            lambda xs: xs[0] if len(xs) > 0 else Null,
            lambda b: [(b[0], b[1])],
        ),
        Function(
            "last",
            ([int], int),
            lambda xs: xs[-1] if len(xs) > 0 else Null,
            lambda b: [(b[0], b[1])],
        ),
        Function(
            "tail",
            ([int], [int]),
            lambda xs: xs[1:] if len(xs) > 0 else Null,
            lambda b: [(b[0], b[1])],
        ),
        Function(
            "count",
            (int, [int], int),
            lambda n, xs: len(list(filter(lambda i: i == n, xs))),
            lambda b: [(0, b[2]), (b[0], b[1])],
        ),
        Function("len", ([int], int), lambda xs: len(xs), lambda b: [(b[0], b[1])]),
        Function("max", ([int], int), lambda xs: max(xs), lambda b: [(b[0], b[1])]),
        Function("min", ([int], int), lambda xs: min(xs), lambda b: [(b[0], b[1])]),
        Function(
            "reverse",
            ([int], [int]),
            lambda xs: list(reversed(xs)),
            lambda b: [(b[0], b[1])],
        ),
        Function(
            "sort",
            ([int], [int]),
            lambda xs: list(sorted(xs)),
            lambda b: [(b[0], b[1])],
        ),
        Function(
            "unique",
            ([int], [int]),
            lambda xs: list(dict.fromkeys(xs)),
            lambda b: [(b[0], b[1])],
        ),  # TODO: check if bounds are correct
        Function(
            "sum",
            ([int], int),
            lambda xs: sum(xs),
            lambda b: [(int(b[0] / b[2]) + 1, int(b[1] / b[2]))],
        ),
        Function(
            "index",
            (int, [int], int),
            lambda n, xs: xs[n] if 0 <= n < len(xs) else Null,
            lambda b: [(0, b[2]), (b[0], b[1])],
        ),
    ] + lambdas
    DSL.extend([
        Function(
            "map " + l.src,
            ([int], [int]),
            lambda xs, l=l: list(map(l.fun, xs)),
            lambda b, l=l: l.bounds((b[0], b[1])),
        )
        for l in lambdas
        if l.sig == (int, int)
    ])
    return DSL
