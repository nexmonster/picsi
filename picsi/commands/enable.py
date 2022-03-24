__all__ = ["enable"]

from pathlib import Path
from halo import Halo

from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_uname import get_uname
from picsi.vendored.get_brcmfmacko import get_brcmfmacko


def enable():
    """
    Enable CSI collection
    """

    with Halo(spinner="dots") as spinner:

        Path("/home/pi/.picsi/state").mkdir(exist_ok=True, parents=True)

        path_picsi_up = Path("/home/pi/.picsi/state/firmware_is_up")
        path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")
        path_brcmfmacko: Path = get_brcmfmacko()

        if path_picsi_up.is_file():
            return

        path_picsi_up.touch()

        # Disable wpa_supplicant
        spinner.text = "Disabling wpa_supplicant"
        with open("/etc/dhcpcd.conf", "a") as ofile:
            ofile.write(
                "\ndenyinterfaces wlan0\ninterface wlan0\n\tnohook wpa_supplicant\n"
            )

        # TODO: wpa_supplicant is completely stopped
        # and disabled. Investigate disabling it on wlan0 only
        # so poeple can use WiFi adapters and such

        # fmt: off
        run_commands([
            "# Disabling wpa_supplicant",
            ["/usr/bin/killall", "wpa_supplicant"],
            ["/usr/bin/systemctl", "disable", "--now", "wpa_supplicant"],

            "# Applying firmware patches",
            ["/usr/bin/cp", path_nexmon_csi_bin / "patched/brcmfmac.ko", path_brcmfmacko],
            ["/usr/bin/cp", path_nexmon_csi_bin / "patched/brcmfmac43455-sdio.bin", "/lib/firmware/brcm/brcmfmac43455-sdio.bin"],
            ["/usr/sbin/depmod", "-a"],
        ], spinner)
        # fmt: on
