import numpy as np


def is_int(val):
    return isinstance(val, int) or isinstance(val, np.int64)


def verify_list_int(val, minv, maxv, minl, maxl):
    assert isinstance(val, list)
    for i in val:
        assert is_int(i)
        assert minv <= i <= maxv
    assert minl <= len(val) <= maxl


class IntConstraint(object):

    def __init__(self, minv=-512, maxv=512):
        self.minv = minv
        self.maxv = maxv

    def verify(self, val):
        return is_int(val) and self.minv <= val <= self.maxv


class ListConstraint(object):

    def __init__(self, min_len=0, max_len=10, item_constraint=IntConstraint()):
        self.min_len = min_len
        self.max_len = max_len
        self.item_constraint = item_constraint

    def verify_items(self, val):
        return all(self.item_constraint.verify(i) for i in val)

    def verify(self, val):
        return isinstance(val, list) and self.verify_items(val) and self.min_len <= len(val) <= self.max_len


class ArgConstraints(object):

    def __init__(self, *constraints):
        self.constraints = (constraints)

    def verify(self, val):
        if len(val) != len(self.constraints):
            return False
        return all(self.constraints[i].verify(v) for i, v in enumerate(val))


def verify_io_pairs(io_pairs, in_type, out_type):
    for i, o in io_pairs:
        try:
            verify_input_type(i, in_type)
        except AssertionError as e:
            print('ERROR: unable to verify input type constraints ({}) for value ({})'.format(in_type, i))
            raise e
        try:
            verify_output_type(o, out_type)
        except AssertionError as e:
            print('ERROR: unable to verify output type constraints ({}) for value ({})'.format(out_type, o))
            raise e


def verify_output_type(o, out_type):
    if out_type == int:
        assert IntConstraint().verify(o)
    elif out_type == [int]:
        assert ListConstraint().verify(o)
    else:
        raise ValueError('ERROR: unsupported output type ({})'.format(out_type))


def verify_input_type(i, in_type):
    if in_type == int:
        assert IntConstraint().verify(i)
    elif in_type == [int]:
        assert ArgConstraints(ListConstraint()).verify(i)
    elif in_type == [int, [int]]:
        assert ArgConstraints(IntConstraint(), ListConstraint()).verify(i)
    else:
        raise ValueError('ERROR: unsupported input type ({})'.format(in_type))