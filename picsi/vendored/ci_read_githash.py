from picsi.vendored.get_output import get_output
from pathlib import Path


def ci_read_githash(path_repo: Path):
    return get_output(["/usr/bin/git", "rev-parse", "--verify", "HEAD"], cwd=path_repo)
