__all__ = ["down"]


from pathlib import Path
from halo import Halo
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output


def down():
    """
    Stop CSI collection
    """

    state_csicollection_is_up = Path("/var/run/picsi/state/csicollection_is_up")
    state_csicollection_is_up.parent.mkdir(exist_ok=True, parents=True)

    if not state_csicollection_is_up.is_file():
        print("CSI collection is not running.")
        return

    with Halo(spinner="dots") as spinner:
        spinner.text = "Stopping CSI collection"

        csiparams = get_output(["makecsiparams", "-e", "0"])

        # fmt: off
        run_commands([
            "# Stopping CSI collection",
            ["nexutil", "-Iwlan0", "-s500", "-b", "-l34", f"-v{csiparams}"],

            "# Removing mon0",
            ["ip", "link", "set", "mon0", "down"],
            ["iw", "dev", "mon0", "del"],

            "# Restarting wlan0",
            ["ip", "link", "set", "dev", "wlan0", "down"],
            ["ip", "link", "set", "dev", "wlan0", "up"],
        ], spinner, log_title='cmd-down')
        # fmt: on

        state_csicollection_is_up.unlink()
