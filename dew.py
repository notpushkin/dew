import asyncio
import concurrent.futures
import csv
from functools import partial
import json
from runpy import run_path
import sys
import traceback

import click
from tqdm import tqdm


echo = partial(click.echo, err=True)


FILE_READERS = {
    "lines": lambda fp: (line.rstrip("\r\n") for line in fp),
    "json": json.load,
    "jsonl": lambda fp: (json.loads(line.rstrip("\r\n")) for line in fp),
    "csv": csv.DictReader,
    "csv-bare": csv.reader,
}


async def run_in_parallel(func, tasks, *, max_workers=20):
    def _wrapped_func(val):
        try:
            return (val, func(val))
        except Exception as e:
            echo(f"When running {func.__name__}({repr(val)}):")
            # We skip 1 stack frame here, showing only user's code part:
            tb = traceback.extract_tb(sys.exc_info()[2])[1:]
            echo("".join(traceback.format_list(tb)), nl=False)
            echo(repr(e))
            return (val, None)

    res = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, _wrapped_func, task) for task in tasks
        ]

        return {
            task: res
            async for task, res in (
                await complete
                for complete in tqdm(asyncio.as_completed(futures), total=len(futures))
            )
        }


@click.command()
@click.argument("pyfile")
@click.argument("infile", type=click.File("r"), default="-")
@click.option(
    "-t", "--input-type", default="lines", type=click.Choice(FILE_READERS.keys())
)
@click.option("--max-workers", default=20)
@click.option("--indent", default=2)
def main(pyfile, infile, input_type, max_workers, indent):
    """
    Run a piece of code (PYFILE) for every entry in INFILE, in parallel.
    """
    func = "f"
    if ":" in pyfile:
        pyfile, func = pyfile.rsplit(":", 1)

    func = run_path(pyfile)[func]
    tasks = FILE_READERS[input_type](infile)

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(run_in_parallel(func, tasks, max_workers=max_workers))
    print(json.dumps(res, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
