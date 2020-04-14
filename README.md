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
$ cat big.txt | warppipe_three tokenize -l en -j 4 normalize -j 4 > output
128457it [00:18, 7068.28it/s]
128457it [00:26, 4777.81it/s]

$ head output
The Project Gutenberg EBook of The Adventures of Sherlock Holmes
by Sir Arthur Conan Doyle
 (# 15 in our series by Sir Arthur Conan Doyle)
```

Actually, not that bad. Compared to original `sacremoses`:

```
cat big.txt | sacremoses normalize | sacremoses tokenize > output2
100%|████████████████████████████████████| 128457/128457 [00:15<00:00, 8503.45it/s]
100%|████████████████████████████████████| 128457/128457 [00:34<00:00, 3699.54it/s]
```
