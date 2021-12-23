import pathlib
import sys
import os

sys.path.insert(0, pathlib.Path(__file__).parents[2].resolve().as_posix())
root_path = pathlib.Path(__file__).parents[2]

version_file = os.path.join(root_path, 'VERSION')
release = open(version_file, 'r').read()
print(release)