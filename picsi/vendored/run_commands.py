import subprocess
from halo import Halo
from pathlib import PosixPath
from datetime import datetime
from typing import Any, Union


def run_commands(
    commands: list[Union[str, list[Any]]],
    spinner: Halo = None,
    check_return: bool = True,
    cwd: str = None,
    env: dict = None,
) -> None:

    # fmt: off
    with \
         open("/home/pi/.picsi/cmd.log", "a") as log_cmd, \
         open("/home/pi/.picsi/time.log", "a") as log_time, \
         open("/home/pi/.picsi/stdout.log", "a") as log_stdout, \
         open("/home/pi/.picsi/stderr.log", "a") as log_stderr:
        # fmt: on

        for c in commands:
            log_cmd.write(f"{c}\n")

            if type(c) == str:
                head = c.split(" ")[0]
                body = " ".join(c.split(" ")[1:])

                if head in ["#"]:
                    if spinner is not None:
                        spinner.text = body
                    else:
                        print(body)
                elif head in ["cd"]:
                    cwd = body

            elif type(c) == PosixPath:
                cwd = str(c)

            elif type(c) == list:
                time_start = datetime.now()

                p = subprocess.run(
                    [str(i) for i in c],
                    stdout=log_stdout,
                    stderr=log_stderr,
                    stdin=subprocess.PIPE,
                    encoding="utf-8",
                    cwd=cwd,
                    env=env,
                )
                
                time_stop = datetime.now()

                log_time.write(f"{time_start} | {time_stop} | {time_stop - time_start} | {c}")

                if check_return:
                    p.check_returncode()
