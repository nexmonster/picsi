from picsi.vendored.get_output import get_output


def get_architecture() -> str:
    return get_output(["/usr/bin/dpkg", "--print-architecture"])
