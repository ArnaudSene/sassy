"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import argparse

from _sassy.a_sassy import Sassy


def parser():
    """A parser."""
    _parser = argparse.ArgumentParser(
        description='Manage Clean Architecture application.')

    _parser.add_argument(
        '--create', '-c', help='Application name')
    args = _parser.parse_args()

    if not args.create:
        _parser.print_help()
        raise ValueError("Provide action'")

    return args


def main():
    """Main function."""
    try:
        args = parser()

        if args.create:
            sassy = Sassy(apps=args.create)
            print(f"create apps to : {sassy.apps_path}")
            result = sassy.create_structure()
            print(result)

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()
