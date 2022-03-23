from picsi.vendored.get_output import get_output


def get_uname(flags: str = "-r") -> str:
    return get_output(["/usr/bin/uname", flags]).strip()
