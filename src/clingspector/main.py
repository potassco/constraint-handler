import argparse
import logging
from clingspector.checker import Checker, Flags
from clingspector.utils.log_formatter import LoggingFormatter


logger = logging.getLogger("clingspector")
handler = logging.StreamHandler()
handler.setFormatter(LoggingFormatter())
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def parse_arguments():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Clingspector: Validates Clingo logic programs and reports errors.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "input_files",
        nargs="*",
        default=[],
        help="Input Clingo encoding files",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output for detailed error messages",
    )
    
    return parser.parse_args()


def main():
    args = parse_arguments()

    checker = Checker()
    checker.set_flags(Flags.VERBOSE, args.verbose)
    checker.load(args.input_files)
    checker.solve()

if __name__ == "__main__":
    main()