import argparse
import json
import os
import sys

from tqdm import trange

from iogen.compiler import Program
from iogen.dsl import get_language_func
from iogen.io import generate_interesting, pretty_print_results

DEFAULT_MAXV = 99
DEFAULT_OUTPUT_JSON = "io.json"
LANG_CHOICES = ("simplelist", "linq", "extended")


def _serialize_programs(d):
    """ Serialize Program objects to strings, so data is JSON serializable. """
    newd = []
    for i in d:
        newi = {}
        for k, v in i.items():
            if k == "program" and isinstance(v, Program):
                v = v.src.replace("\n", " | ")
            newi[k] = v
        newd.append(newi)
    return newd


def write_json(d, to_json):
    d = _serialize_programs(d)
    with open(to_json, "w") as f:
        json.dump(d, f)


def generate_examples(*args, **kwargs):
    """
    Run IO generation with defaults set by CLI arguments.
    """
    cli_args = kwargs.pop("cli_args")
    kwargs.update(
        {
            "num_examples": kwargs.get("num_examples", cli_args.num_examples),
            "timeout": kwargs.get("timeout", cli_args.timeout),
            "min_bound": kwargs.get("min_bound", cli_args.min_bound),
            "max_bound": kwargs.get("max_bound", cli_args.max_bound),
            "min_variance": kwargs.get("min_variance", cli_args.min_variance),
            "maxv": kwargs.get("maxv", cli_args.maxv),
            "max_io_len": kwargs.get("max_io_len", cli_args.max_io_len),
        }
    )
    language = kwargs.get("language", cli_args.language(kwargs))
    return generate_interesting(language, *args, **kwargs)


def get_stock_tasks():
    return [
        {"source": "a <- [int] | b <- head a"},
        {"source": "a <- [int] | b <- tail a"},
        {"source": "a <- [int] | b <- tail a | c <- head a | d <- count c b"},
        {"source": "a <- [int] | b <- tail a | c <- len a | d <- count c b"},
        {"source": "a <- [int] | b <- tail a | c <- last a | d <- count c b"},
        {"source": "a <- [int] | b <- tail a | c <- len b | d <- count c b"},
        {"source": "a <- [int] | b <- tail a | c <- head b | d <- count c b"},
        {"source": "a <- [int] | b <- tail a | c <- last b | d <- count c b"},
        {"source": "a <- int | b <- [int] | c <- count a b"},
        {
            "source": "a <- [int] | b <- tail a | c <- tail b | d <- tail c | e <- head d | f <- count e a",
            "kwargs": {"min_io_len": 3},
        },
    ]


def progress(tasks):
    # A low mininterval setting is used to avoid skipping updates
    return trange(
        len(tasks),
        miniters=1,
        mininterval=0.000001,
        unit="tasks",
        desc="Total Progress",
    )


def get_tasks(args):
    if args.stdin:
        tasks = read_stdin()
    elif args.from_json:
        tasks = read_json(args)
    elif args.from_txt:
        tasks = read_txt(args)
    else:
        print("Demo mode:")
        tasks = get_stock_tasks()
    return tasks


def read_json(args):
    tasks = []
    for fname in args.from_json:
        with open(fname, "r") as f:
            d = json.load(f)
        for t in d:
            assert "source" in t
            if t.get("skip", False):
                continue
            tasks.append(t)
    return tasks


def read_txt(args):
    tasks = []
    for fname in args.from_txt:
        with open(fname, "r") as f:
            lines = f.readlines()
        for source in lines:
            tasks.append({"source": source.strip("\n")})
    return tasks


def read_stdin():
    tasks = []
    for line in sys.stdin:
        tasks.append({"source": line.strip()})
    return tasks


def get_result(args, index, tasks):
    t = tasks[index]
    source = t["source"]
    kwargs = t.get("kwargs", {})
    return generate_examples(source, cli_args=args, **kwargs)


def print_output(args, results):
    print()  # required to move to next line due to progress bar
    if args.json:
        write_json(results, args.to_json)
    else:
        for d in results:
            pretty_print_results(d)
    if args.json:
        print(args.to_json)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-examples", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--min-bound", type=int, default=0)
    parser.add_argument("--max-bound", type=int, default=99)
    parser.add_argument("--min-variance", type=float, default=3.5)
    parser.add_argument("--maxv", help="max val for item in list", type=int, default=DEFAULT_MAXV)
    parser.add_argument("--max-io-len", type=int, default=10)
    parser.add_argument("--json", action="store_true", default=False)
    parser.add_argument("--to-json", default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--language", choices=LANG_CHOICES, default="simplelist")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--stdin", action="store_true")
    group.add_argument("--from-json", nargs="*")
    group.add_argument("--from-txt", nargs="*")
    args = parser.parse_args(args)
    args.to_json = os.path.abspath(args.to_json)
    args.language = get_language_func(args.language)
    return args


def main(args):
    tasks = get_tasks(args)
    results = [get_result(args, i, tasks) for i in progress(tasks)]
    print_output(args, results)
    return results


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
