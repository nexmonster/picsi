from pathlib import Path
from picsi.vendored.get_output import get_output


def get_brcmfmacko() -> Path:
    return Path(get_output(["/usr/sbin/modinfo", "brcmfmac", "-n"]).strip())
