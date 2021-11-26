"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import argparse
import os
os.environ['VERBOSE'] = 'verbose'
from _sassy import a_sassy as _a, p_sassy as _p  # noqa E402


def parser():
    """Parse arguments."""
    _parser = argparse.ArgumentParser(
        description='Manage Clean Architecture application.')

    _parser.add_argument('apps_feat', nargs='+', type=str,
                         help='Provide apps (and feature) name ')

    _parser.add_argument(
        '--create', '-a', action='store_const', const=True, help='Create')

    args = _parser.parse_args()

    if len(args.apps_feat) == 0 or not args.create:
        _parser.print_help()
        raise ValueError("Provide action'")

    return args


def main():
    """Execute the main function."""
    try:
        args = parser()

        if args.create:
            if len(args.apps_feat) == 1:
                apps = args.apps_feat[0]
                sassy = _a.Sassy(apps=apps, message=_p.MessageService())

                sassy.create_structure()
            else:
                apps = args.apps_feat[0]
                feature = args.apps_feat[1]
                sassy = _a.Sassy(apps=apps, message=_p.MessageService())

                sassy.create_feature(feature=feature)

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()
