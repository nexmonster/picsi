from pathlib import Path
import tomli


def get_distlink(path_picsi_ci: Path = Path("/boot/picsi-ci.toml")) -> str:
    # NOTE: /boot/picsi-ci.toml is created by me while
    # flashing the Pi. It would not exist on your setup.

    if path_picsi_ci.exists():
        with open(path_picsi_ci, "rb") as infile:
            return tomli.load(infile)["dist"]["link"]
    else:
        return ""
