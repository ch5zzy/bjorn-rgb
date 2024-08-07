import argparse


def parse_cmdline(argv, **kwargs):
    # Check whether the simulator should be used
    parser = argparse.ArgumentParser()
    parser.prog = "bjorn"
    parser.add_argument("--sim", action="store_true", default=False)

    for arg, options in kwargs.items():
        action = options.get("action", "store_true")
        default = options.get("default", False)
        parser.add_argument(f"--{arg}", action=action, default=default)

    args = parser.parse_args(argv[1:])

    return args
