__all__ = ["disable"]

from pathlib import Path
from halo import Halo
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_uname import get_uname
from picsi.vendored.get_brcmfmacko import get_brcmfmacko
from picsi.commands.down import down as cmd_down


def disable():
    """
    Disable CSI collection
    """

    # Check if firmware is already disabled.
    state_firmware_is_patched = Path("/home/pi/.picsi/state/firmware_is_patched")
    state_firmware_is_patched.parent.mkdir(exist_ok=True, parents=True)

    if not state_firmware_is_patched.is_file():
        print("Firmware is already disabled.")
        return

    # Stop CSI collection if it's running.
    state_csicollection_is_up = Path("/var/run/picsi/state/csicollection_is_up")
    state_csicollection_is_up.parent.mkdir(exist_ok=True, parents=True)

    if state_csicollection_is_up.is_file():
        cmd_down()

    with Halo(spinner="dots") as spinner:
        spinner.text = "Restoring original firmware"

        path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")
        path_brcmfmacko: Path = get_brcmfmacko()

        # Unblock WPA_supplicant on wlan0
        with open("/etc/dhcpcd.conf", "r") as ifile:
            dhcpcd_conf = ifile.read()

        with open("/etc/dhcpcd.conf", "w") as ofile:
            ofile.write(
                dhcpcd_conf.replace(
                    "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n",
                    "",
                )
            )

        # fmt: off
        run_commands([
            "# Restoring original firmware",
            ["cp", path_nexmon_csi_bin / "original/brcmfmac.ko", f"{path_brcmfmacko}"],
            ["cp", path_nexmon_csi_bin / "original/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
            ["rmmod", "brcmfmac"],
            ["modprobe", "brcmutil"],
            ["insmod", path_brcmfmacko],
            ["depmod", "-a"],

            "# Enabling wpa_supplicant on wlan0",
            ["systemctl", "enable", "wpa_supplicant"],
            ["nocheck", "wpa_supplicant", "-B", "-c", "/etc/wpa_supplicant/wpa_supplicant.conf", "-i", "wlan0"],
            ["dhcpcd", "wlan0"],

            "# Restarting wlan0",
            ["ip", "link", "set", "dev", "wlan0", "down"],
            ["ip", "link", "set", "dev", "wlan0", "up"],
        ], spinner, log_title='cmd-disable')
        # fmt: on

        state_firmware_is_patched.unlink()
