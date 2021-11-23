"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import argparse

from _sassy import a_sassy as _a, p_sassy as _p


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
            sassy = _a.Sassy(apps=args.create, message=_p.MessageService())
            print(f"create apps to : {sassy.apps_path}")
            sassy.create_structure()

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()
