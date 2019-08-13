import numpy as np
import sys

from collections import namedtuple

from taskgen.dsl.linq import get_linq_language

Program = namedtuple('Program', ['src', 'ins', 'out', 'fun', 'bounds'])


# LINQ LANGUAGE


def get_language_dict(language):
    return {l.src: l for l in language}


def compile_program(language, source_code, V, L, min_input_range_length=0, verbose=False):
    """ Taken in a program source code, the integer range V and the tape lengths L,
        and produces a Program.
        If L is None then input constraints are not computed.
        """

    # Source code parsing into intermediate representation
    lang_dict = get_language_dict(language)

    input_types = []
    types = []
    functions = []
    pointers = []
    for line in source_code.split('\n'):
        # print("'%s'" % line)
        instruction = line[5:]
        # instruction = line
        if instruction in ['int', '[int]']:
            input_types.append(eval(instruction))
            types.append(eval(instruction))
            functions.append(None)
            pointers.append(None)
        else:
            split = instruction.split(' ')
            command = split[0]
            args = split[1:]
            # Handle lambda
            if len(split[1]) > 1 or split[1] < 'a' or split[1] > 'z':
                command += ' ' + split[1]
                args = split[2:]
            f = lang_dict[command]
            assert len(f.sig) - 1 == len(args)
            ps = [ord(arg) - ord('a') for arg in args]
            types.append(f.sig[-1])
            functions.append(f)
            pointers.append(ps)
            assert [types[p] == t for p, t in zip(ps, f.sig)]
    input_length = len(input_types)
    program_length = len(types)

    # Validate program by propagating input constraints and check all registers are useful
    limits = [(-V, V)]*program_length
    if L is not None:
        for t in range(program_length-1, -1, -1):
            if t >= input_length:
                lim_l, lim_u = limits[t]
                new_lims = functions[t].bounds((lim_l, lim_u, L))
                num_args = len(functions[t].sig) - 1
                for a in range(num_args):
                    p = pointers[t][a]
                    limits[pointers[t][a]] = (max(limits[p][0], new_lims[a][0]),
                                              min(limits[p][1], new_lims[a][1]))
                    #print('t=%d: New limit for %d is %s' % (t, p, limits[pointers[t][a]]))
            elif min_input_range_length >= limits[t][1] - limits[t][0]:
                if verbose: print(('Program with no valid inputs: %s' % source_code))
                return None

    # for t in xrange(input_length, program_length):
    #     print('%s (%s)' % (functions[t].src, ' '.join([chr(ord('a') + p) for p in pointers[t]])))

    # Construct executor
    my_input_types = list(input_types)
    my_types = list(types)
    my_functions = list(functions)
    my_pointers = list(pointers)
    my_program_length = program_length

    def program_executor(args):
        # print '--->'
        # for t in xrange(input_length, my_program_length):
        #     print('%s <- %s (%s)' % (chr(ord('a') + t), my_functions[t].src, ' '.join([chr(ord('a') + p) for p in my_pointers[t]])))
        assert len(args) == len(my_input_types)
        registers = [None]*my_program_length
        for t in range(len(args)):
            registers[t] = args[t]
        for t in range(len(args), my_program_length):
            registers[t] = my_functions[t].fun(*[registers[p] for p in my_pointers[t]])
        return registers[-1]

    return Program(
        source_code,
        input_types,
        types[-1],
        program_executor,
        limits[:input_length]
    )


def generate_IO_examples(program, N, L, V):
    """ Given a programs, randomly generates N IO examples.
        using the specified length L for the input arrays. """
    input_types = program.ins
    input_nargs = len(input_types)

    # Generate N input-output pairs
    IO = []
    for _ in range(N):
        input_value = [None]*input_nargs
        for a in range(input_nargs):
            minv, maxv = program.bounds[a]
            if input_types[a] == int:
                input_value[a] = np.random.randint(minv, maxv)
            elif input_types[a] == [int]:
                input_value[a] = list(np.random.randint(minv, maxv, size=L))
            else:
                raise Exception("Unsupported input type " + input_types[a] + " for random input generation")
        output_value = program.fun(input_value)
        IO.append((input_value, output_value))
        assert (program.out == int and output_value <= V) or (program.out == [int] and len(output_value) == 0) or (program.out == [int] and max(output_value) <= V)
    return IO


def test_program(source, N=5, V=512):
    import time
    t = time.time()
    language, _ = get_linq_language(V)
    source = source.replace(' | ', '\n')
    program = compile_program(language, source, V=V, L=10)
    samples = generate_IO_examples(program, N=N, L=10, V=V)
    print(("time:", time.time()-t))
    print(program)
    print('samples:')
    for s in samples:
        print('    {}'.format(s))
    return program, samples


if __name__ == '__main__':
    source = sys.argv[1]
    test_program(source)
