__all__ = ["install"]

import requests
from typer import Exit
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
            f"""\n
        Error: Couldn't download binaries. http code {response.status_code}

        Pre-compiled binaries are not uploaded for your kernel's version: {uname_r} yet.
        Please create a new Issue on Github and tell us which kernel you are using.

        Meanwhile, you can build Nexmon_csi from source by running `picsi build`,
        and then run `picsi install` again.
        """
        )
        raise Exit(1)

    destination.parent.mkdir(exist_ok=True)

    with open(destination, "wb") as ofile:
        ofile.write(response.content)


def extract_archive(location: Path) -> None:
    run_commands([["tar", "-xvJf", location, "-C", location.parent]])


def install():
    """
    Install Nexmon_CSI from binaries
    """

    # Check if picsi is already installed
    state_picsi_is_installed = Path("/home/pi/.picsi/state/picsi_is_installed")
    state_picsi_is_installed.parent.mkdir(exist_ok=True, parents=True)

    if state_picsi_is_installed.is_file():
        print("Error. Firmware is already installed.")
        raise Exit(10)

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

        # fmt: off
        run_commands([
            "# Installing Nexutil",
            ["ln", "-s", path_nexmon_csi_bin / "nexutil/nexutil", "/usr/local/bin/nexutil"],

            "# Installing Makecsiparams",
            ["ln", "-s", path_nexmon_csi_bin / "makecsiparams/makecsiparams", "/usr/local/bin/mcp"],
            ["ln", "-s", path_nexmon_csi_bin / "makecsiparams/makecsiparams", "/usr/local/bin/makecsiparams"],

            "# Setting up WiFi",
            ["rfkill", "unblock", "all"],
            ["raspi-config", "nonint", "do_wifi_country", "US"],

            "# Expanding SD card",
            ["raspi-config", "nonint", "do_expand_rootfs"],
        ], spinner, log_title='cmd-install')
        # fmt: on

        state_picsi_is_installed.touch()
