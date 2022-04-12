import subprocess
from halo import Halo
from os import environ
from pathlib import Path
from datetime import datetime
from typing import Any, Union, List


def run_commands(
    # typing.List before py 3.9
    commands: List[Union[str, List[Any]]],
    spinner: Halo = None,
    check_return: bool = True,
    cwd: str = None,
    env: dict = None,
    log_title: str = "picsi",
) -> None:

    osenv = dict(environ)

    if env is not None:
        osenv.update(env)

    Path("/home/pi/.picsi/logs/").mkdir(exist_ok=True, parents=True)

    # fmt: off
    with \
         open("/home/pi/.picsi/logs/cmd.log", "a", buffering=1) as log_cmd, \
         open("/home/pi/.picsi/logs/time.log", "a", buffering=1) as log_time, \
         open("/home/pi/.picsi/logs/stdout.log", "a", buffering=1) as log_stdout, \
         open("/home/pi/.picsi/logs/stderr.log", "a", buffering=1) as log_stderr:
        # fmt: on

        for c in commands:
            if type(c) == str:
                log_cmd.write(f"\n{c}\n")
                log_time.write(f"\n{datetime.now(): %b %d %Y %H:%M:%S} {log_title} [{0:7.2f}] 0: {c}\n")

                head = c.split(" ")[0]
                body = " ".join(c.split(" ")[1:])

                if head in ["#"]:
                    if spinner is not None:
                        spinner.text = body
                    else:
                        print(body)
                elif head in ["cd"]:
                    cwd = body

            elif type(c) == list:
                current_check_return = True

                if c[0] == "nocheck":
                    current_check_return = False
                    c = c[1:]

                log_cmd.write(f"{c}\n")

                time_start = datetime.now()

                p = subprocess.run(
                    [str(i) for i in c],
                    stdout=log_stdout,
                    stderr=log_stderr,
                    stdin=subprocess.PIPE,
                    encoding="utf-8",
                    cwd=cwd,
                    env=osenv,
                )
                
                time_stop = datetime.now()

                log_time.write(f"{time_start: %b %d %Y %H:%M:%S} {log_title} [{(time_stop - time_start).total_seconds():7.2f}] {p.returncode}: {c}\n")

                if check_return and current_check_return:
                    p.check_returncode()
