from pathlib import Path
import tomli
from typing import Dict


def ci_read_author(path_picsi_ci: Path = Path("/boot/picsi-ci.toml")) -> Dict[str, str]:
    # NOTE: /boot/picsi-ci.toml is created by me while
    # flashing the Pi. It would not exist on your setup.

    if path_picsi_ci.exists():
        with open(path_picsi_ci, "rb") as infile:
            return tomli.load(infile)["author"]
    else:
        return {
            "name": "Anonymous",
            "email": "anonymous@example.com",
            "website": "https://www.example.com/",
            "license": "Unknown",
        }
