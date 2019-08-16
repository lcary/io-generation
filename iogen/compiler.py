from collections import namedtuple

Program = namedtuple("Program", ["src", "ins", "out", "fun", "bounds"])


def get_language_dict(language):
    return {l.src: l for l in language}


def compile_program(
    language, source_code, max_bound, L, min_input_range_length=0, min_bound=None
):
    """
    Parses a program into an intermediate representation capable of constraints
    checking and execution.

    Args:
        - language: a DSL used to parse the tokens in a program
        - source_code: string of source that will be parsed
        - max_bound: max value allowed as integer
        - L: "tape lengths"  # TODO: improve this definition
        - min_bound: min value allowed as integer (default: -max_bound)
    """
    functions, input_types, pointers, types = parse_source(language, source_code)
    input_length = len(input_types)
    program_length = len(types)

    try:
        limits = propagate_constraints(
            source_code,
            max_bound,
            L,
            program_length,
            input_length,
            min_input_range_length,
            pointers,
            functions,
            min_bound=min_bound,
        )
    except PropagationError:
        print("WARN: PropagationError")
        return None

    program_executor = Executor(input_types, functions, pointers, program_length)

    return Program(
        source_code, input_types, types[-1], program_executor, limits[:input_length]
    )


class Executor(object):
    def __init__(self, input_types, functions, pointers, program_length, debug=False):
        self.input_types = list(input_types)
        self.functions = list(functions)
        self.pointers = list(pointers)
        self.program_length = program_length
        self.debug = debug

    def __call__(self, args):
        assert len(args) == len(self.input_types)
        registers = [None] * self.program_length
        for t in range(len(args)):
            registers[t] = args[t]
        for t in range(len(args), self.program_length):
            args = [registers[p] for p in self.pointers[t]]
            func = self.functions[t]
            if self.debug:
                print("DEBUG: func = {}".format(func))
                print("DEBUG: args = {}".format(args))
            try:
                res = func.fun(*args)
                if self.debug:
                    print("DEBUG: res  = {}".format(res))
            except TypeError as e:
                print("ERROR: failed to execute program")
                print("ERROR: func = {}".format(func))
                print("ERROR: args = {}".format(args))
                raise e
            registers[t] = res
        return registers[-1]


def parse_source(language, source_code):
    lang_dict = get_language_dict(language)
    input_types = []
    types = []
    functions = []
    pointers = []
    for line in source_code.split("\n"):
        instruction = line[5:]
        if instruction in ["int", "[int]"]:
            input_types.append(eval(instruction))
            types.append(eval(instruction))
            functions.append(None)
            pointers.append(None)
        else:
            split = instruction.split(" ")
            command = split[0]
            args = split[1:]
            # Handle lambda
            if len(split[1]) > 1 or split[1] < "a" or split[1] > "z":
                command += " " + split[1]
                args = split[2:]
            f = lang_dict[command]
            assert len(f.sig) - 1 == len(args)
            ps = [ord(arg) - ord("a") for arg in args]
            types.append(f.sig[-1])
            functions.append(f)
            pointers.append(ps)
            assert [types[p] == t for p, t in zip(ps, f.sig)]
    return functions, input_types, pointers, types


class PropagationError(Exception):
    pass


def propagate_constraints(
    source_code,
    max_bound,
    L,
    program_length,
    input_length,
    min_input_range_length,
    pointers,
    functions,
    min_bound=None,
):
    """
    Validate program by propagating input constraints and checking
    that all registers are useful.
    """
    if min_bound is None:
        min_bound = -max_bound
    limits = [(min_bound, max_bound)] * program_length
    if L is None:
        return limits
    for t in range(program_length - 1, -1, -1):
        if t >= input_length:
            lim_l, lim_u = limits[t]
            new_lims = functions[t].bounds((lim_l, lim_u, L))
            num_args = len(functions[t].sig) - 1
            for a in range(num_args):
                p = pointers[t][a]
                limits[pointers[t][a]] = (
                    max(limits[p][0], new_lims[a][0]),
                    min(limits[p][1], new_lims[a][1]),
                )
        elif min_input_range_length >= limits[t][1] - limits[t][0]:
            print(("WARN: Program with no valid inputs: %s" % source_code))
            print('limits: ', limits)
            print('limits[t]: ', limits[t])
            raise PropagationError
    return limits
