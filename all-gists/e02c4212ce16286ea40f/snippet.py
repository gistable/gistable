#!/usr/bin/env python

"""
Test parallel scripts running with asyncio executors.

Requires at least Python 3.4 to run.
"""

import asyncio
import os
import subprocess
from functools import partial
from typing import Sequence, Any

from asyncio import async as ensure_future  # async is deprecated in Python 3.4


COMMANDS = [
    "ls /usr",
    "ls /usr/local",
    "ls ~",
    "ls /themiddleofnowhere",
]

MAX_RUNNERS = 2

semaphore = asyncio.Semaphore(MAX_RUNNERS)


def run_command(cmd: str) -> str:
    """
    Run prepared behave command in shell and return its output.

    :param cmd: Well-formed behave command to run.
    :return: Command output as string.
    """

    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True,
            cwd=os.getcwd(),
        )

    except subprocess.CalledProcessError as e:
        output = e.output

    return output


@asyncio.coroutine
def run_command_on_loop(loop: asyncio.AbstractEventLoop, command: str) -> bool:
    """
    Run test for one particular feature, check its result and return report.

    :param loop: Loop to use.
    :param command: Command to run.
    :return: Result of the command.
    """
    with (yield from semaphore):
        runner = partial(run_command, command)
        output = yield from loop.run_in_executor(None, runner)
        yield from asyncio.sleep(2)  # Slowing a bit for demonstration purposes
        return output


@asyncio.coroutine
def run_all_commands(command_list: Sequence[str] = COMMANDS) -> None:
    """
    Run all commands in a list

    :param command_list: List of commands to run.
    """
    loop = asyncio.get_event_loop()
    fs = [run_command_on_loop(loop, command) for command in command_list]
    for f in asyncio.as_completed(fs):
        result = yield from f
        ensure_future(process_result(result))


@asyncio.coroutine
def process_result(result: Any):
    """
    Do something useful with result of the commands
    """
    print(result)


def main() -> None:
    """ Entry point """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_all_commands())


if __name__ == "__main__":
    main()
