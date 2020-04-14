from distutils.core import setup
import setuptools

console_scripts = """
[console_scripts]
warppipe_one=warppipe.cli:cli_one
warppipe_two=warppipe.cli:cli_two
"""

setup(
  name = 'warppipe',
  packages = ['warppipe'],
  version = '0.0.1',
  description = '',
  long_description = '',
  author = '',
  license = '',
  url = 'https://github.com/alvations/warppipe',
  keywords = [],
  classifiers = [],
  install_requires = ['click', 'joblib', 'tqdm'],
  entry_points=console_scripts,
)
