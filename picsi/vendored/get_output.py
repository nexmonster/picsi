import subprocess
from pathlib import Path  # imported for typing
from typing import List, Dict


def get_output(
    command: List[str],
    cwd: Path = None,
    env: Dict[str, str] = None,
    check_return: bool = True,
) -> str:

    if cwd is not None:
        cwd = cwd.resolve()

    p: subprocess.CompletedProcess = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
        cwd=cwd,
        env=env,
    )

    if check_return:
        p.check_returncode()

    return p.stdout.strip()
