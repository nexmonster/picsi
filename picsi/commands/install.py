__all__ = ["install"]

import requests
import subprocess
import typer
from pathlib import Path
from halo import Halo

from picsi.vendored.get_uname import get_uname
from picsi.vendored.run_commands import run_commands


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
        print(
            f"""
            Error: Couldn't download binaries. http code {response.status_code}

            Pre-compiled binaries are not uploaded for your kernel's version: {uname_r} yet.
            Please create a new Issue on Github and tell us which kernel you are using.

            Meanwhile, you can build Nexmon_csi from source by running `picsi build`,
            and then run `picsi install` again.
        """
        )
        raise typer.Exit(1)

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

        Path("/home/pi/.picsi/").mkdir(exist_ok=True)

        path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")
        path_nexmon_csi_bin_tarxz = Path(str(path_nexmon_csi_bin) + ".tar.xz")

        # Read system info
        spinner.text = "Reading system info"
        uname_r = get_uname("-r")

        # Download binaries
        spinner.text = "Downloading binaries"
        if not path_nexmon_csi_bin_tarxz.is_file():
            get_binaries(uname_r, path_nexmon_csi_bin_tarxz)

        # Extract binaries
        spinner.text = "Extracting binaries"
        extract_archive(path_nexmon_csi_bin_tarxz)

        commands = [
            # fmt: off
            "# Installing Nexutil",
            ["/usr/bin/ln", "-s", path_nexmon_csi_bin / "nexutil/nexutil", "/usr/local/bin/nexutil"],

            "# Installing Makecsiparams",
            ["/usr/bin/ln", "-s", path_nexmon_csi_bin / "makecsiparams/makecsiparams", "/usr/local/bin/mcp"],
            ["/usr/bin/ln", "-s", path_nexmon_csi_bin / "makecsiparams/makecsiparams", "/usr/local/bin/makecsiparams"],

            "# Setting up WiFi",
            ["/usr/sbin/rfkill", "unblock", "all"],
            ["/usr/bin/raspi-config", "nonint", "do_wifi_country", "US"],

            "# Expanding SD card",
            ["/usr/bin/raspi-config", "nonint", "do_expand_rootfs"],
            # fmt: on
        ]

        run_commands(commands, spinner)
