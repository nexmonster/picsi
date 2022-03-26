import subprocess
from os import environ
from pathlib import Path  # imported for typing
from typing import List, Dict, Any


def get_output(
    command: List[Any],
    cwd: Path = None,
    env: Dict[str, str] = None,
    check_return: bool = True,
) -> str:

    if cwd is not None:
        cwd = cwd.resolve()

    osenv = dict(environ)

    if env is not None:
        osenv.update(env)

    command = [str(c) for c in command]
    p: subprocess.CompletedProcess = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
        cwd=cwd,
        env=osenv,
    )

    if check_return:
        p.check_returncode()

    return p.stdout.strip()
