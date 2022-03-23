import subprocess
from pathlib import Path  # imported for typing


def get_output(
    command: list, cwd: Path = None, env: dict = None, check_return: bool = True
) -> str:
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
