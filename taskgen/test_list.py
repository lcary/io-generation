import argparse
import json
import os

from tqdm import trange

from taskgen.compiler import Program
from taskgen.dsl.simple import get_list_dsl
from taskgen.io import generate_interesting, pretty_print_results

DEFAULT_MAXV = 99
DEFAULT_JSON_FILE = "ioexamples.json"


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


def write_json(d, json_filepath):
    d = _serialize_programs(d)
    with open(json_filepath, "w") as f:
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
    kwargs["language"] = kwargs.get("language", get_list_dsl(kwargs["max_bound"]))
    return generate_interesting(*args, **kwargs)


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


def run_tests():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num-examples", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--min-bound", type=int, default=0)
    parser.add_argument("--max-bound", type=int, default=99)
    parser.add_argument("--min-variance", type=float, default=3.5)
    parser.add_argument("--maxv", type=int, default=DEFAULT_MAXV)  # max value in list
    parser.add_argument("--max-io-len", type=int, default=10)
    parser.add_argument("--json", action="store_true", default=False)
    parser.add_argument("--json-filepath", default=DEFAULT_JSON_FILE)
    args = parser.parse_args()

    args.json_filepath = os.path.abspath(args.json_filepath)

    tasks = get_stock_tasks()

    results = []
    for i in progress(tasks):
        t = tasks[i]
        source = t["source"]
        kwargs = t.get("kwargs", {})
        r = generate_examples(source, cli_args=args, **kwargs)
        results.append(r)

    print()  # required to move to next line due to progress bar

    if args.json:
        write_json(results, args.json_filepath)
    else:
        for d in results:
            pretty_print_results(d)

    if args.json:
        print(args.json_filepath)


if __name__ == "__main__":
    run_tests()
