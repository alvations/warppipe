# -*- coding: utf-8 -*-

from functools import partial
from functools import update_wrapper
from itertools import chain
from tqdm import tqdm

import click

from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
from sacremoses.normalize import MosesPunctNormalizer
from sacremoses.util import parallelize_preprocess

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
        iterator = fin # Initialize fin as the first iterator.
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)

@cli_two.command('plus')
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def plus_two(encoding):
    def processor(iterator):
        for line in iterator:
            yield line.strip() + " + "
    return processor

@cli_two.command('xyz')
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
def xyz_two(encoding):
    def processor(iterator):
        for line in iterator:
            yield line.strip() + " xyz"
    return processor

########################################################################
# $ wget https://norvig.com/big.txt
# $ cat big.txt | warppipe_three normalize -l en -j 4 tokenize -j 4
#
# $
########################################################################

@click.group(chain=True, invoke_without_command=True)
def cli_three():
    pass

@cli_three.resultcallback()
def process_pipeline(processors):
    with click.get_text_stream("stdin") as fin:
        iterator = fin # Initialize fin as the first iterator.
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)

@cli_three.command("tokenize")
@click.option(
    "--language", "-l", default="en", help="Use language specific rules when tokenizing"
)
@click.option("--processes", "-j", default=1, help="No. of processes.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Disable progress bar.")
def tokenize_file(
    language,
    processes,
    quiet):

    moses = MosesTokenizer(lang=language)

    moses_tokenize = partial(
        moses.tokenize,
        return_str=True,
    )

    def processor(iterator):
        if processes == 1:
            for line in list(iterator):
                yield moses_tokenize(line)
        else:
            for outline in parallelize_preprocess(
                moses_tokenize, list(iterator), processes, progress_bar=(not quiet)
            ):
                yield outline
    return processor

@cli_three.command("normalize")
@click.option(
    "--language",
    "-l",
    default="en",
    help="Use language specific rules when normalizing.",
)
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
@click.option("--processes", "-j", default=1, help="No. of processes.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Disable progress bar.")
def normalize_file(
    language, processes, encoding, quiet
):
    moses = MosesPunctNormalizer(
        language,
    )
    moses_normalize = partial(moses.normalize)

    def processor(iterator):
        print(processes)
        if processes == 1:
            for line in list(iterator):
                yield moses_normalize(line)
        else:
            for outline in parallelize_preprocess(
                moses_normalize, list(iterator), processes, progress_bar=(not quiet)
            ):
                yield outline
    return processor

########################################################################
# $ wget https://norvig.com/big.txt
# $ cat big.txt | warppipe_four -l en -j 4 normalize tokenize
########################################################################

@click.group(chain=True, invoke_without_command=True)
@click.option(
    "--language",
    "-l",
    default="en",
    help="Use language specific rules when normalizing.",
)
@click.option("--encoding", "-e", default="utf8", help="Specify encoding of file.")
@click.option("--processes", "-j", default=1, help="No. of processes.")
@click.option("--quiet", "-q", is_flag=True, default=False, help="Disable progress bar.")
def cli_four(language, encoding, processes, quiet):
    pass

@cli_four.resultcallback()
def process_pipeline(processors, **kwargs):
    with click.get_text_stream("stdin") as fin:
        iterator = fin # Initialize fin as the first iterator.
        for processor in processors:
            iterator = processor(list(iterator), **kwargs)
        for item in iterator:
            click.echo(item)

def processor(f, **kwargs):
    """Helper decorator to rewrite a function so that
    it returns another function from it.
    """
    def new_func(*args, **kwargs):
        def processor(stream, **kwargs):
            return f(stream, **kwargs)
        return processor
    return update_wrapper(new_func, f)

@cli_four.command("normalize")
@processor
def normalize_file(iterator, language, encoding, processes, quiet):
    moses = MosesPunctNormalizer(
        language,
    )
    moses_normalize = partial(moses.normalize)

    if processes == 1:
        for line in iterator:
            yield moses_normalize(line)
    else:
        for outline in parallelize_preprocess(
            moses_normalize, iterator, processes, progress_bar=(not quiet)
        ):
            yield outline



@cli_four.command("tokenize")
@processor
def tokenize_file(iterator, language, encoding, processes, quiet):
    moses = MosesTokenizer(lang=language)

    moses_tokenize = partial(
        moses.tokenize,
        return_str=True,
    )

    if processes == 1:
        for line in iterator:
            yield moses_tokenize(line)
    else:
        for outline in parallelize_preprocess(
            moses_tokenize, iterator, processes, progress_bar=(not quiet)
        ):
            yield outline
