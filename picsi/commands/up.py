__all__ = ["up"]

from pathlib import Path
import subprocess
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


def get_brcmfmacko():
    p = subprocess.run(
        ["/usr/sbin/modinfo", "brcmfmac", "-n"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
    )

    p.check_returncode()

    return p.stdout.strip()


def up():
    """
    Enable CSI collection
    """

    with Halo(spinner="dots") as spinner:

        dir_picsi: Path = Path("/home/pi/.picsi")

        # Read system info
        spinner.text = "Reading system info"
        uname_r: str = get_uname("-r")

        path_binaries: Path = dir_picsi / f"bins/{uname_r}/"
        path_brcmfmacko: Path = get_brcmfmacko()

        # Disable wpa_supplicant
        spinner.text = "Disabling wpa_supplicant"
        with open("/etc/dhcpcd.conf", "a") as ofile:
            ofile.write(
                "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n"
            )

        # fmt: off
        commands: str = [
            "Disabling wpa_supplicant"
            ["/usr/bin/killall", "wpa_supplicant"],
            ["/usr/bin/systemctl", "disable", "--now", "wpa_supplicant"],

            "Applying firmware patches"
            ["/usr/bin/cp", f"{path_binaries}/patched/brcmfmac.ko", f"{path_brcmfmacko}"],
            ["/usr/bin/cp", f"{path_binaries}/patched/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
            ["/usr/sbin/depmod", "-a"],
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
