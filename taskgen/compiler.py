from collections import namedtuple

Program = namedtuple("Program", ["src", "ins", "out", "fun", "bounds"])


def get_language_dict(language):
    return {l.src: l for l in language}


def compile_program(
    language, source_code, V, L, min_input_range_length=0,
):
    """
    Parses a program into an intermediate representation capable of constraints
    checking and execution.

    Args:
        - language: a DSL used to parse the tokens in a program
        - source_code: string of source that will be parsed
        - V: range of values allowed as integer range
        - L: "tape lengths"  # TODO: improve this definition
    """
    functions, input_types, pointers, types = parse_source(language, source_code)
    input_length = len(input_types)
    program_length = len(types)

    try:
        limits = propagate_constraints(
            source_code,
            V,
            L,
            program_length,
            input_length,
            min_input_range_length,
            pointers,
            functions,
        )
    except PropagationError:
        return None

    # Construct executor
    my_input_types = list(input_types)
    my_functions = list(functions)
    my_pointers = list(pointers)
    my_program_length = program_length

    def program_executor(args):
        assert len(args) == len(my_input_types)
        registers = [None] * my_program_length
        for t in range(len(args)):
            registers[t] = args[t]
        for t in range(len(args), my_program_length):
            registers[t] = my_functions[t].fun(*[registers[p] for p in my_pointers[t]])
        return registers[-1]

    return Program(
        source_code, input_types, types[-1], program_executor, limits[:input_length]
    )


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
    V,
    L,
    program_length,
    input_length,
    min_input_range_length,
    pointers,
    functions
):
    """
    Validate program by propagating input constraints and checking
    that all registers are useful/
    """
    limits = [(-V, V)] * program_length
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
            print(("Program with no valid inputs: %s" % source_code))
            raise PropagationError
    return limits
