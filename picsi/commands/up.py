__all__ = ["up"]

from pathlib import Path
import subprocess


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

    dir_picsi: Path = Path("/home/pi/.picsi")

    uname_r: str = get_uname("-r")
    path_binaries: Path = dir_picsi / f"bins/{uname_r}/"

    path_brcmfmacko: Path = get_brcmfmacko()

    with open("/etc/dhcpcd.conf", "a") as ofile:
        ofile.write(
            "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n"
        )

    # fmt: off
    commands: str = [
        # install firmware and driver
        ["/usr/bin/cp", f"{path_binaries}/patched/brcmfmac.ko", f"{path_brcmfmacko}"],
        ["/usr/bin/cp", f"{path_binaries}/patched/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
        ["/usr/sbin/depmod", "-a"],

        # Disable wpa_supplicant
        ["/usr/bin/killall", "wpa_supplicant"],
        ["/usr/bin/systemctl", "disable", "--now", "wpa_supplicant"],
    ]
    # fmt: on

    for c in commands:
        p = subprocess.run(
            c,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            encoding="utf-8",
        )

        p.check_returncode()

    print("Done.")
