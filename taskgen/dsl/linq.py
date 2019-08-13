from math import sqrt, ceil

from taskgen.dsl.types import Function


def scanl1(f, xs):
    if len(xs) > 0:
        r = xs[0]
        for i in range(len(xs)):
            if i > 0:
                r = f.fun(r, xs[i])
            yield r


def SQR_bounds(A, B):
    l = max(0, A)   # inclusive lower bound
    u = B - 1       # inclusive upper bound
    if l > u:
        return [(0, 0)]
    # now 0 <= l <= u
    # ceil(sqrt(l))
    # Assume that if anything is valid then 0 is valid
    return [(-int(sqrt(u)), ceil(sqrt(u+1)))]


def MUL_bounds(A, B):
    return SQR_bounds(0, min(-(A+1), B))


def scanl1_bounds(l, A, B, L):
    if l.src == '+' or l.src == '-':
        return [(int(A/L)+1, int(B/L))]
    elif l.src == '*':
        return [(int((max(0, A)+1) ** (1.0 / L)), int((max(0, B)) ** (1.0 / L)))]
    elif l.src == 'MIN' or l.src == 'MAX':
        return [(A, B)]
    else:
        raise Exception('Unsupported SCANL1 lambda, cannot compute valid input bounds.')


def get_linq_language(V):
    Null = V
    lambdas = [
        Function('IDT', (int, int), lambda i: i, lambda A_B: [(A_B[0], A_B[1])]),

        Function('INC', (int, int), lambda i: i + 1, lambda A_B10: [(A_B10[0], A_B10[1] - 1)]),
        Function('DEC', (int, int), lambda i: i - 1, lambda A_B11: [(A_B11[0] + 1, A_B11[1])]),
        Function('SHL', (int, int), lambda i: i * 2, lambda A_B12: [(int((A_B12[0] + 1) / 2), int(A_B12[1] / 2))]),
        Function('SHR', (int, int), lambda i: int(float(i) / 2), lambda A_B13: [(2 * A_B13[0], 2 * A_B13[1])]),
        Function('doNEG', (int, int), lambda i: -i, lambda A_B14: [(-A_B14[1] + 1, -A_B14[0] + 1)]),
        Function('MUL3', (int, int), lambda i: i * 3, lambda A_B15: [(int((A_B15[0] + 2) / 3), int(A_B15[1] / 3))]),
        Function('DIV3', (int, int), lambda i: int(float(i) / 3), lambda A_B16: [(A_B16[0], A_B16[1])]),

        Function('MUL4', (int, int), lambda i: i * 4, lambda A_B17: [(int((A_B17[0] + 3) / 4), int(A_B17[1] / 4))]),
        Function('DIV4', (int, int), lambda i: int(float(i) / 4), lambda A_B18: [(A_B18[0], A_B18[1])]),
        Function('SQR', (int, int), lambda i: i * i, lambda A_B19: SQR_bounds(A_B19[0], A_B19[1])),
        #Function('SQRT',    (int, int),          lambda i: int(sqrt(i)),                              lambda (A, B): [(max(0, A*A), B*B)]),

        Function('isPOS', (int, bool), lambda i: i > 0, lambda A_B20: [(A_B20[0], A_B20[1])]),
        Function('isNEG', (int, bool), lambda i: i < 0, lambda A_B21: [(A_B21[0], A_B21[1])]),
        Function('isODD', (int, bool), lambda i: i % 2 == 1, lambda A_B22: [(A_B22[0], A_B22[1])]),
        Function('isEVEN', (int, bool), lambda i: i % 2 == 0, lambda A_B23: [(A_B23[0], A_B23[1])]),

        Function('+', (int, int, int), lambda i, j: i + j, lambda A_B24: [(int(A_B24[0] / 2) + 1, int(A_B24[1] / 2))]),
        Function('-', (int, int, int), lambda i, j: i - j, lambda A_B25: [(int(A_B25[0] / 2) + 1, int(A_B25[1] / 2))]),
        Function('*', (int, int, int), lambda i, j: i * j, lambda A_B26: MUL_bounds(A_B26[0], A_B26[1])),
        Function('MIN', (int, int, int), lambda i, j: min(i, j), lambda A_B27: [(A_B27[0], A_B27[1])]),
        Function('MAX', (int, int, int), lambda i, j: max(i, j), lambda A_B28: [(A_B28[0], A_B28[1])]),
    ]

    LINQ = [
        Function('REVERSE', ([int], [int]), lambda xs: list(reversed(xs)), lambda A_B_L: [(A_B_L[0], A_B_L[1])]),
        Function('SORT', ([int], [int]), lambda xs: sorted(xs), lambda A_B_L1: [(A_B_L1[0], A_B_L1[1])]),
        Function('TAKE', (int, [int], [int]), lambda n, xs: xs[:n], lambda A_B_L2: [(0, A_B_L2[2]), (A_B_L2[0], A_B_L2[1])]),
        Function('DROP', (int, [int], [int]), lambda n, xs: xs[n:], lambda A_B_L3: [(0, A_B_L3[2]), (A_B_L3[0], A_B_L3[1])]),
        Function('ACCESS', (int, [int], int), lambda n, xs: xs[n] if n >= 0 and len(xs) > n else Null, lambda A_B_L4: [(0, A_B_L4[2]), (A_B_L4[0], A_B_L4[1])]),
        Function('COUNT', (int, [int], int), lambda n, xs: len(list(filter(lambda i: i == n, xs))), lambda b: [(0, b[2]), (b[0], b[1])]),
        Function('TAIL', ([int], [int]), lambda xs: xs[1:] if len(xs) > 0 else Null, lambda b: [(b[0], b[1])]),
        Function('HEAD', ([int], int), lambda xs: xs[0] if len(xs) > 0 else Null, lambda A_B_L5: [(A_B_L5[0], A_B_L5[1])]),
        Function('LAST', ([int], int), lambda xs: xs[-1] if len(xs) > 0 else Null, lambda A_B_L6: [(A_B_L6[0], A_B_L6[1])]),
        Function('MINIMUM', ([int], int), lambda xs: min(xs) if len(xs) > 0 else Null, lambda A_B_L7: [(A_B_L7[0], A_B_L7[1])]),
        Function('LEN', ([int], int), lambda xs: len(xs), lambda b: [(b[0], b[1])]),
        Function('MAXIMUM', ([int], int), lambda xs: max(xs) if len(xs) > 0 else Null, lambda A_B_L8: [(A_B_L8[0], A_B_L8[1])]),
        Function('SUM', ([int], int), lambda xs: sum(xs), lambda A_B_L9: [(int(A_B_L9[0] / A_B_L9[2]) + 1, int(A_B_L9[1] / A_B_L9[2]))]),
    ] + \
    [Function(
            'MAP ' + l.src,
            ([int], [int]),
            lambda xs, l=l: list(map(l.fun, xs)),
            lambda A_B_L, l=l: l.bounds((A_B_L[0], A_B_L[1]))
        ) for l in lambdas if l.sig==(int, int)] + \
    [Function(
            'FILTER ' + l.src,
            ([int], [int]),
            lambda xs, l=l: list(filter(l.fun, xs)),
            lambda A_B_L, l=l: [(A_B_L[0], A_B_L[1])],
        ) for l in lambdas if l.sig==(int, bool)] + \
    [Function(
            'COUNT ' + l.src,
            ([int], int),
            lambda xs, l=l: len(list(filter(l.fun, xs))),
            lambda A_B_L, l=l: [(-V, V)],
        ) for l in lambdas if l.sig==(int, bool)] + \
    [Function(
            'ZIPWITH ' + l.src,
            ([int], [int], [int]),
            lambda xs, ys, l=l: [l.fun(x, y) for (x, y) in zip(xs, ys)],
            lambda A_B_L, l=l: l.bounds((A_B_L[0], A_B_L[1])) + l.bounds((A_B_L[0], A_B_L[1])),
        ) for l in lambdas if l.sig==(int, int, int)] + \
    [Function(
            'SCANL1 ' + l.src,
            ([int], [int]),
            lambda xs, l=l: list(scanl1(l, xs)),
            lambda A_B_L, l=l: scanl1_bounds(l, A_B_L[0], A_B_L[1], A_B_L[2]),
        ) for l in lambdas if l.sig==(int, int, int)]

    return LINQ, lambdas
