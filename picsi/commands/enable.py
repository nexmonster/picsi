__all__ = ["enable"]

from pathlib import Path
from halo import Halo
from typer import Exit
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_uname import get_uname
from picsi.vendored.get_brcmfmacko import get_brcmfmacko


def enable():
    """
    Enable CSI collection
    """

    # Check if picsi has been installed
    state_picsi_is_installed = Path("/home/pi/.picsi/state/picsi_is_installed")
    state_picsi_is_installed.parent.mkdir(exist_ok=True, parents=True)

    if not state_picsi_is_installed.is_file():
        print("Error. You need to run `picsi install` before you can do this.")
        raise Exit(10)

    # Check if firmware is already enabled
    state_firmware_is_patched = Path("/home/pi/.picsi/state/firmware_is_patched")
    state_firmware_is_patched.parent.mkdir(exist_ok=True, parents=True)

    if state_firmware_is_patched.is_file():
        print("Firmware is already enabled.")
        return

    with Halo(spinner="dots") as spinner:
        spinner.text = "Disabling wpa_supplicant on wlan0"

        path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")
        path_brcmfmacko: Path = get_brcmfmacko()

        # Block WPA_supplicant on wlan0
        with open("/etc/dhcpcd.conf", "a") as ofile:
            ofile.write(
                "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n"
            )

        # fmt: off
        run_commands([
            "# Disabling wpa_supplicant on wlan0",
            ["systemctl", "restart", "wpa_supplicant"],
            ["systemctl", "restart", "dhcpcd"],

            "# Applying firmware patches",
            ["cp", path_nexmon_csi_bin / "patched/brcmfmac.ko", path_brcmfmacko],
            ["cp", path_nexmon_csi_bin / "patched/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
            ["rmmod", "brcmfmac"],
            ["modprobe", "brcmutil"],
            ["insmod", path_brcmfmacko],
            ["depmod", "-a"],
        ], spinner, log_title='cmd-enable')
        # fmt: on

        state_firmware_is_patched.touch()
