__all__ = ["down"]

import typer

from pathlib import Path
from halo import Halo

from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output


def down():
    """
    Stop CSI collection
    """

    Path("/home/pi/.picsi/state").mkdir(exist_ok=True, parents=True)

    path_state_csi_up = Path("/home/pi/.picsi/state/csi_is_up")
    if not path_state_csi_up.is_file():
        raise typer.Exit(0)

    path_state_csi_up.unlink()

    with Halo(spinner="dots") as spinner:
        spinner.text = "Stopping CSI collection"

        csiparams = get_output(["makecsiparams", "-e", "0"])

        # fmt: off
        run_commands([
            ["nexutil", "-Iwlan0", "-s500", "-b", "-l34", f"-v{csiparams}"],
            ["ip", "link", "set", "mon0", "down"],
            ["iw", "dev", "mon0", "del"],
            ["ifconfig", "wlan0", "up"],
        ], spinner)
        # fmt: on
