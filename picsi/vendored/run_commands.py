import subprocess
from halo import Halo
from pathlib import Path, PosixPath
from datetime import datetime
from typing import Any, Union, List

from picsi.vendored.get_PATH import get_PATH


def run_commands(
    # typing.List before py 3.9
    commands: List[Union[str, List[Any]]],
    spinner: Halo = None,
    check_return: bool = True,
    cwd: str = None,
    env: dict = None,
) -> None:

    if env is None:
        env = {"PATH": get_PATH()}

    if "PATH" not in env:
        env["PATH"] = get_PATH()

    Path("/home/pi/.picsi/logs/").mkdir(exist_ok=True, parents=True)

    # fmt: off
    with \
         open("/home/pi/.picsi/logs/cmd.log", "a") as log_cmd, \
         open("/home/pi/.picsi/logs/time.log", "a") as log_time, \
         open("/home/pi/.picsi/logs/stdout.log", "a") as log_stdout, \
         open("/home/pi/.picsi/logs/stderr.log", "a") as log_stderr:
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

                log_time.write(f"{time_start} | {time_stop} | {time_stop - time_start} | {c}\n")

                if check_return:
                    p.check_returncode()
