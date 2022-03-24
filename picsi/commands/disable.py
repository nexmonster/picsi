__all__ = ["disable"]

from pathlib import Path
from halo import Halo

from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_uname import get_uname
from picsi.vendored.get_brcmfmacko import get_brcmfmacko


def disable():
    """
    Disable CSI collection
    """

    with Halo(spinner="dots") as spinner:

        Path("/home/pi/.picsi/state").mkdir(exist_ok=True, parents=True)

        path_picsi_up = Path("/home/pi/.picsi/state/firmware_is_up")
        path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")
        path_brcmfmacko: Path = get_brcmfmacko()

        if not path_picsi_up.is_file():
            return

        path_picsi_up.unlink()

        # Enable wpa_supplicant
        spinner.text = "Enabling wpa_supplicant"

        with open("/etc/dhcpcd.conf", "r") as ifile:
            dhcpcd_conf = ifile.read().replace(
                "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n", ""
            )

        with open("/etc/dhcpcd.conf", "w") as ofile:
            ofile.write(dhcpcd_conf)

        # TODO: Investigate disabling CSI collection
        # by stopping nexutil

        # fmt: off
        run_commands([
            "# Enabling wpa_supplicant",
            ["/usr/bin/systemctl", "enable", "--now", "wpa_supplicant"],
            ["wpa_supplicant", "-B", "-c", "/etc/wpa_supplicant/wpa_supplicant.conf", "-i", "wlan0"],

            "# Restoring original firmware",
            ["/usr/bin/cp", path_nexmon_csi_bin / "original/brcmfmac.ko", f"{path_brcmfmacko}"],
            ["/usr/bin/cp", path_nexmon_csi_bin / "original/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
            ["/usr/sbin/depmod", "-a"],

            "# Restarting WiFi",
            ["/usr/sbin/ip", "link", "set", "dev", "wlan0", "down"],
            ["/usr/sbin/ip", "link", "set", "dev", "wlan0", "up"],

        ], spinner)
        # fmt: on
