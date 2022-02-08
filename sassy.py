#!/usr/bin/env python3
"""
Main script to create and manage a python project through the clean \
architecture design.

Contact:
  Arnaud SENE, arnaud.sene@halia.ca
  Karol KOZUBAL, karol.lozubal@halia.ca
"""
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import basename
from sys import argv
from textwrap import dedent

from src import MessageService, RepoProvider, Sassy


def get_version() -> str:
    """
    Get the version number from VERSION.

    Returns (str):
        The version number
    """
    with open('VERSION', 'r') as f:
        return f.read()


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
                  Create a structure
                  
                    {self.exe} <apps_name> --create
                    
                  Create | Delete a module (all structure)
                  
                    {self.exe} <apps_name> <feature_name> --create
                    {self.exe} <apps_name> <feature_name> --delete 
                    
                  Create | Delete a module (select directory)
                  
                    {self.exe} <apps_name> <feature_name> <dir_args,dir_args> --create  # noqa
                    {self.exe} <apps_name> <feature_name> <dir_args,dir_args> --delete  # noqa
                    
                    Where <dir_args> are defined as below:
                      *a or applications
                      *d or domains
                      *p or providers
                      *i or interfaces
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

        self.parser.add_argument(
            '--version', '-v',
            action='version',
            version=get_version(),
            help="Show sassy's version")

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
            # Create a project
            if len(args.names) == 1:
                apps = args.names[0]
                src = Sassy(apps=apps, message=message, repo=repo)
                src.create_structure()

            elif len(args.names) == 2:
                # Create modules
                apps = args.names[0]
                feature = args.names[1]
                src = Sassy(apps=apps, message=message, repo=repo)
                src.create_feature(feature=feature)

            elif len(args.names) == 3:
                # Create modules with options
                apps = args.names[0]
                feature = args.names[1]
                kwargs = {'directories': args.names[2].split(',')}
                src = Sassy(apps=apps, message=message, repo=repo)
                src.create_feature(feature=feature, **kwargs)

        elif args.delete:
            if len(args.names) == 2:
                apps = args.names[0]
                feature = args.names[1]
                src = Sassy(apps=apps, message=message, repo=repo)
                src.delete_feature(feature=feature)

            elif len(args.names) == 3:
                # Delete modules with options
                apps = args.names[0]
                feature = args.names[1]
                directories = {'directories': args.names[2].split(',')}
                src = Sassy(apps=apps, message=message, repo=repo)
                src.delete_feature(feature=feature, **directories)
        else:
            sys.stdout.write(f"Invalid arguments: {argv[1:]}!")

    except Exception as exc:
        print(f'{exc}')


if __name__ == '__main__':
    main()
