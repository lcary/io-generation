from taskgen.dsl.extended import get_extended_dsl
from taskgen.dsl.linq import get_linq_dsl
from taskgen.dsl.simple import get_list_dsl


def get_language_func(choice):
    if choice == "simplelist":

        def f(kwargs):
            return get_list_dsl(kwargs["max_bound"])

        return f
    elif choice == "extended":

        def f(kwargs):
            return get_extended_dsl(kwargs["max_bound"], min_bound=kwargs["min_bound"])

        return f
    elif choice == "linq":

        def f(kwargs):
            language, _ = get_linq_dsl(
                kwargs["max_bound"], min_bound=kwargs["min_bound"]
            )
            return language

        return f
    else:
        raise ValueError("Language type ({}) not recognized.".format(choice))
