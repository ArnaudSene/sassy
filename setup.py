"""Setuptools for package registry."""
import typing as _t
from setuptools import setup, find_packages

with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

packages: _t.List[_t.Any] = find_packages()
packages.append('')

setup(
    name="sassy",
    version=open('VERSION', 'r').read(),
    author='Arnaud SENE & Karol KOZUBAL',
    author_email='arnaud@halia.ca',
    description='A Python framework for building SaaS applications using '
                'clean architecture.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/halia-ca/sassy',
    packages=packages,
    package_data={'src': ['*.yml']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'sassy = sassy:main',
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
