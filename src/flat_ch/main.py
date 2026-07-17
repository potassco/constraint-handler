import argparse
import sys

from flat_ch.file_generation import generate_files


def main() -> None:
    parser = argparse.ArgumentParser(prog="fch", description="Flat Constraint Handler")

    parser.add_argument("--generate", action="store_true", help="Generate static/dynamic variants from your templates.")

    args = parser.parse_args()

    if args.generate:
        generate_files()
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
