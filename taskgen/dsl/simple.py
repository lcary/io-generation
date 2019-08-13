from collections import namedtuple
from taskgen.dsl.types import Function

def get_language(V):
    Null = V
    return [
        Function(
            'head',
            ([int], int),
            lambda xs: xs[0] if len(xs) > 0 else Null,
            lambda b: [(b[0], b[1])]
        ),
        Function(
            'last',
            ([int], int),
            lambda xs: xs[-1] if len(xs) > 0 else Null,
            lambda b: [(b[0], b[1])]
        ),
        Function(
            'tail',
            ([int], [int]),
            lambda n, xs: xs[1:],
            lambda b: [(0, b[2]), (b[0], b[1])]
        ),
        Function(
            'count',
            (int, [int], int),
            lambda n, xs: len(list(filter(lambda x: x == n, xs))),
            lambda b: [(-V, V)],  # TODO: correct bounds?
        )
    ]
