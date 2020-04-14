# -*- coding: utf-8 -*-

from functools import partial
from functools import update_wrapper
from itertools import chain
from tqdm import tqdm

import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

########################################################################
# $ echo "abc" | warppipe_one plus -e utf8 | warppipe_one xyz -e utf8
# abc + xyz
########################################################################

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli_one():
    pass

@cli_one.command("plus")
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def plus(encoding):
    with click.get_text_stream("stdin", encoding=encoding) as fin:
        with click.get_text_stream("stdout", encoding=encoding) as fout:
            for line in fin.readlines():
                print(line.strip() + " + ", end='\n', file=fout)

@cli_one.command("xyz")
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def xyz(encoding):
    with click.get_text_stream("stdin", encoding=encoding) as fin:
        with click.get_text_stream("stdout", encoding=encoding) as fout:
            for line in fin.readlines():
                print(line.strip() + " xyz", end='\n', file=fout)

########################################################################
# $ echo "abc" | warppipe_two plus -e utf8 xyz -e utf8
# abc + xyz
########################################################################

@click.group(chain=True, invoke_without_command=True)
def cli_two():
    pass

@cli_two.resultcallback()
def process_pipeline(processors):
    with click.get_text_stream("stdin") as fin:
        iterator = (x.strip() for x in fin)
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)

@cli_two.command('plus')
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def plus_two(encoding):
    def processor(iterator):
        for line in iterator:
            yield line + " + "
    return processor

@cli_two.command('xyz')
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def xyz_two(encoding):
    def processor(iterator):
        for line in iterator:
            yield line + "xyz"
    return processor
