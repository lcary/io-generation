from iogen.dsl.types import Function


def get_list_dsl(max_bound, min_bound=None):
    Null = max_bound
    return [
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
    ]
