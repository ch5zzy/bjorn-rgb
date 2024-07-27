import argparse


def parse_cmdline(argv):
    # Check whether the simulator should be used
    parser = argparse.ArgumentParser()
    parser.prog = "bjorn"
    parser.add_argument("-s", "--sim", action="store_true", default=False)

    args = parser.parse_args(argv[1:])

    if args.sim:
        from unicorn_hat_sim import unicornhathd as unicorn
    else:
        import unicornhathd as unicorn

    return unicorn
