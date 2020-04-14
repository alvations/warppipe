# Warp Pipe (ワープ土管)

This is an example to chain the `click` commands, as documented on https://click.palletsprojects.com/en/7.x/commands/#multi-command-pipelines

# Install

```
python setup.py install
```

# Chapter 1

**Without** using `chain=True` parameter, we can still "chain" the command by re-invoking the binary and passing on the `stdout` output of the previous function to the `stdin` to the current function.

Example usage:

```
$ echo "abc" | warppipe_one plus -e utf8 | warppipe_one xyz -e utf8
abc + xyz
```

# Chapter 2.0

Using the `chain=True` and keeping the results of previous funtion in an iterator tuple, after every function call, it thens "echos" the items out to `stdout`.

```python
@cli_two.resultcallback()
def process_pipeline(processors):
    with click.get_text_stream("stdin") as fin:
        iterator = (x.strip() for x in fin)
        for processor in processors:
            iterator = processor(iterator)
        for item in iterator:
            click.echo(item)
```

Example usage:

```
$ echo "abc" | warppipe_two plus -e utf8 xyz -e utf8
abc + xyz
```

The CLI looks elegant but it comes at some heavy memory footprint.

 1. `iterator = (x.strip() for x in fin)` literally stores everything in memory
 2. The data is re-iterated just for the sake of printing it out to `stdout`.

 # Chapter 2.1

 With minor changes to the `click` callback, we eliminate first round of iterating through the data:

```python
 @cli_two.resultcallback()
 def process_pipeline(processors):
     with click.get_text_stream("stdin") as fin:
         iterator = fin # Initialize fin as the first iterator.
         for processor in processors:
             iterator = processor(iterator)
         for item in iterator:
             click.echo(item)
```

Same example usage:

```
$ echo "abc" | warppipe_two plus -e utf8 xyz -e utf8
abc + xyz
```

Still the CLI comes with some heavy memory footprint.

 1. `iterator = processor(iterator)` literally stores one copy of the process data in memory
 2. The data is re-iterated just for the sake of printing it out to `stdout`.

# Chapter 3.0

Memory footprint aside, if we just treat it as a trade-off for I/O operations, what if we try the chaining on actual preprocessing, e.g. normalization and tokenization.

Example usage:

```
$ wget https://norvig.com/big.txt
$ cat big.txt | warppipe_three normalize -l en -j 4 tokenize -j 4 > output
100%|███████████████████████████████████| 128457/128457 [00:09<00:00, 13910.46it/s]
100%|███████████████████████████████████| 128457/128457 [00:17<00:00, 7536.68it/s]

$ head output
The Project Gutenberg EBook of The Adventures of Sherlock Holmes
by Sir Arthur Conan Doyle
 (# 15 in our series by Sir Arthur Conan Doyle)
```

Actually, not that bad. Compared to original `sacremoses`:

```
$ cat big.txt | sacremoses normalize -j 4 | sacremoses tokenize -j 4 > output2
100%|███████████████████████████████████| 128457/128457 [00:12<00:00, 10553.31it/s]
100%|███████████████████████████████████| 128457/128457 [00:23<00:00, 5477.54it/s]
```

# Chapter 4.0

Now how can we avoid repeating the `-j 4` again and again for individual process?

We can set these arguments at a group level, e.g.

```python
@click.group(chain=True, invoke_without_command=True)
@click.option("--language", "-l", default="en", help="Use language specific rules when normalizing.")
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

@cli_four.command("normalize")
def normalize_file(iterator, language, encoding, processes, quiet):
    for item in iterator:
        yield normalize(item, language, encoding, processes, quiet)

@cli_four.command("tokenize")
def normalize_file(iterator, language, encoding, processes, quiet):
    for item in iterator:
        yield tokenize(item, language, encoding, processes, quiet)
```

Example usage:

```
$ warppipe_four --help
Usage: warppipe_four [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -l, --language TEXT      Use language specific rules when normalizing.
  -e, --encoding TEXT      Specify encoding of file.
  -j, --processes INTEGER  No. of processes.
  -q, --quiet              Disable progress bar.
  --help                   Show this message and exit.

Commands:
  normalize
  tokenize


$ cat big.txt | warppipe_four -l en -j 4 normalize tokenize > output
100%|████████████████████████████████████| 128457/128457 [00:13<00:00, 9326.19it/s]
100%|████████████████████████████████████| 128457/128457 [00:20<00:00, 6190.23it/s]
```
