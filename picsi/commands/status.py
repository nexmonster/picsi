__all__ = ["status"]

from pathlib import Path
from picsi.vendored.get_output import get_output


def status():
    """
    See status
    """

    state_picsi_is_installed = Path("/home/pi/.picsi/state/picsi_is_installed")
    state_firmware_is_patched = Path("/home/pi/.picsi/state/firmware_is_patched")
    state_csicollection_is_up = Path("/var/run/picsi/state/csicollection_is_up")

    if state_picsi_is_installed.exists():
        print("Firmware installed: Yes")
    else:
        print("Firmware installed: No")

    if state_firmware_is_patched.exists():
        print("Firmware enabled: Yes")
    else:
        print("Firmware enabled: No")

    if state_csicollection_is_up.exists():
        chanspec = get_output(["nexutil", "-k"])
        print("CSI collection running: Yes")
        print(f"chanspec: {chanspec}")
    else:
        print("CSI collection running: No")
