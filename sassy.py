#!/usr/bin/env python3
"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import argparse
import os
import sys
import textwrap

from _sassy.a_sassy import Sassy
from _sassy.p_sassy import MessageService, RepoProvider


class Parser:
    """Parser class."""

    def __init__(self):
        """Init."""
        self.exe = os.path.basename(sys.argv[0])
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Manage Clean Architecture application.",
            epilog=textwrap.dedent(f'''\
                examples:
                  {self.exe} <apps_name> --create
                  {self.exe} <apps_name> <feature_name> --create
                  {self.exe} <apps_name> <feature_name> --delete
            ''')
        )

        self.parser.add_argument(
            'apps_feat', nargs='+', type=str, help='apps_name [feature]')

        self.parser.add_argument(
            '--create', '-c',
            action='store_const',
            const=True,
            help='Create an apps structure or a feature')

        self.parser.add_argument(
            '--delete', '-d',
            action='store_const',
            const=True,
            help='Delete a feature')

    def __call__(self):
        """Parse arguments."""
        args = self.parser.parse_args()
        return args
    #
    # def help(self):
    #     """Show help."""
    #     self.parser.print_help()


def main():
    """Execute the main function."""
    try:
        args = Parser()()
        message = MessageService()
        repo = RepoProvider()

        if args.create:
            if len(args.apps_feat) == 1:
                apps = args.apps_feat[0]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.create_structure()

            else:
                apps = args.apps_feat[0]
                feature = args.apps_feat[1]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.create_feature(feature=feature)

        elif args.delete:
            if len(args.apps_feat) == 2:
                apps = args.apps_feat[0]
                feature = args.apps_feat[1]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.delete_feature(feature=feature)
        else:
            print(f"Invalid arguments: {sys.argv[1:]}!")

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()

