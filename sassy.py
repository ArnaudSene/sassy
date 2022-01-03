#!/usr/bin/env python3
"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import basename
from sys import argv
from textwrap import dedent

from sassy import MessageService, RepoProvider, Sassy


class Parser:
    """Parser class."""

    def __init__(self):
        """Init."""
        self.exe = basename(argv[0])
        self.parser = ArgumentParser(
            formatter_class=RawDescriptionHelpFormatter,
            description="Clean Architecture CLI tool.",
            epilog=dedent(f'''\
                examples:
                  {self.exe} <apps_name> --create
                  {self.exe} <apps_name> <feature_name> --create
                  {self.exe} <apps_name> <feature_name> --delete
            ''')
        )

        self.parser.add_argument(
            'names', nargs='+', type=str, help='Project and feature names')

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


def main():
    """Execute the main function."""
    try:
        args = Parser()()
        message = MessageService()
        repo = RepoProvider()

        if args.create:
            if len(args.names) == 1:
                apps = args.names[0]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.create_structure()

            else:
                apps = args.names[0]
                feature = args.names[1]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.create_feature(feature=feature)

        elif args.delete:
            if len(args.names) == 2:
                apps = args.names[0]
                feature = args.names[1]
                sassy = Sassy(apps=apps, message=message, repo=repo)
                sassy.delete_feature(feature=feature)
        else:
            print(f"Invalid arguments: {argv[1:]}!")

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()
