__all__ = ["down"]

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


def down():
    """
    Disable CSI collection
    """

    dir_picsi: Path = Path("/home/pi/.picsi")

    uname_r: str = get_uname("-r")
    path_binaries: Path = dir_picsi / f"bins/{uname_r}/"

    path_brcmfmacko: Path = get_brcmfmacko()

    with open("/etc/dhcpcd.conf", "r") as ifile:
        dhcpcd_conf = ifile.read().replace(
            "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n", ""
        )

    with open("/etc/dhcpcd.conf", "w") as ofile:
        ofile.write(dhcpcd_conf)

    del dhcpcd_conf

    # fmt: off
    commands: str = [
        # Restore original firmware and driver
        ["/usr/bin/cp", f"{path_binaries}/original/brcmfmac.ko", f"{path_brcmfmacko}"],
        ["/usr/bin/cp", f"{path_binaries}/original/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
        ["/usr/sbin/depmod", "-a"],

        # Enable wpa_supplicant
        ["/usr/sbin/wpa_supplicant"],
        ["/usr/bin/systemctl", "enable", "--now", "wpa_supplicant"],

        # Restart wlan0
        ["/usr/sbin/ip", "link", "set", "dev", "wlan0", "down"],
        ["/usr/sbin/ip", "link", "set", "dev", "wlan0", "up"],
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
