# Warp Pipe (ワープ土管)

This is an example to chain the `click` commands, as documented on https://click.palletsprojects.com/en/7.x/commands/#multi-command-pipelines

# Install

```
python setup.py install
```

# Method 1

**Without** using `chain=True` parameter, we can still "chain" the command by re-invoking the binary and passing on the `stdout` output of the previous function to the `stdin` to the current function.

Example usage:

```
$ echo "abc" | warppipe_one plus -e utf8 | warppipe_one xyz -e utf8
abc + xyz
```

# Method 2.0

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

 # Method 2.1

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
