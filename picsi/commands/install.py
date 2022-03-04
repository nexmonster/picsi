__all__ = ["install"]

from pathlib import Path
import subprocess
import requests
from halo import Halo


def get_uname(flag: str = "-r"):
    p = subprocess.run(
        ["/usr/bin/uname", flag],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
    )

    p.check_returncode()

    return p.stdout.strip()


def get_binaries(
    uname_r: str,
    destination: Path,
    variant: str = "base",
    branch: str = "main",
    repository: str = "nexmonster/nexmon_csi_bin",
) -> None:
    url = f"https://github.com/{repository}/raw/{branch}/{variant}/{uname_r}.tar.xz"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(
            f"""
                Error: Couldn't download binaries. http {response.status_code}

                Pre-compiled binaries probably don't exist for your kernel's version: {uname_r}
                Please create a new Issue on Github and tell us which kernel you are using.

                Meanwhile, you can build Nexmon_csi from source by running 'picsi build',
                and then run 'picsi install' again.
        """
        )

    destination.parent.mkdir(exist_ok=True)

    with open(destination, "wb") as ofile:
        ofile.write(response.content)


def extract_archive(location: Path) -> None:
    p = subprocess.run(
        ["/usr/bin/tar", "-xvJf", location, "-C", location.parent],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
    )

    p.check_returncode()


def install():
    """
    Install Nexmon_CSI from binaries
    """

    with Halo(spinner="dots") as spinner:

        dir_picsi = Path("/home/pi/.picsi")
        dir_picsi.mkdir(exist_ok=True)

        # Read system info
        spinner.text = "Reading system info"
        uname_r = get_uname("-r")

        path_binarchive: Path = dir_picsi / f"bins/{uname_r}.tar.xz"
        path_binaries: Path = dir_picsi / f"bins/{uname_r}/"

        # Download binaries
        spinner.text = "Downloading binaries"
        if not path_binarchive.is_file():
            get_binaries(uname_r, path_binarchive)

        # Extract binaries
        spinner.text = "Extracting binaries"
        extract_archive(path_binarchive)

        # fmt: off
        commands = [
            "Installing Nexutil",
            ["/usr/bin/ln", "-s", f"{path_binaries}/nexutil/nexutil", "/usr/local/bin/nexutil"],

            "Installing Makecsiparams",
            ["/usr/bin/ln", "-s", f"{path_binaries}/makecsiparams/makecsiparams", "/usr/local/bin/mcp"],
            ["/usr/bin/ln", "-s", f"{path_binaries}/makecsiparams/makecsiparams", "/usr/local/bin/makecsiparams"],

            "Setting up WiFi",
            ["/usr/sbin/rfkill", "unblock", "all"],
            ["/usr/bin/raspi-config", "nonint", "do_wifi_country", "US"],

            "Expanding SD card",
            ["/usr/bin/raspi-config", "nonint", "do_expand_rootfs"],
        ]
        # fmt: on

        for c in commands:
            if type(c) == str:
                spinner.text = c
            else:
                p = subprocess.run(
                    c,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    encoding="utf-8",
                )

                p.check_returncode()
