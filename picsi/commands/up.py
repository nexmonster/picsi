__all__ = ["up"]

import typer

from pathlib import Path
from halo import Halo

from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output
from picsi.commands.down import down as picsi_down


def up(
    chanspec: str = typer.Argument(default="36/80"),
    macs: str = None,
    byte: str = None,
    delay: int = None,
    coremask: int = 1,
    nssmask: int = 1,
    csiparams: str = None,
):
    """
    Start CSI collection
    """

    Path("/home/pi/.picsi/state").mkdir(exist_ok=True, parents=True)

    path_state_firmware_up = Path("/home/pi/.picsi/state/firmware_is_up")
    if not path_state_firmware_up.is_file():
        print(
            """
        Error: Couldn't start CSI collection.
        
        It seems the firmware is not enabled.
        Please run `picsi enable`.
        """
        )

        raise typer.Exit(1)

    path_state_csi_up = Path("/home/pi/.picsi/state/csi_is_up")
    if path_state_csi_up.is_file():
        picsi_down()

    path_state_csi_up.touch()

    with Halo(spinner="dots") as spinner:
        spinner.text = "Starting CSI collection"
        if csiparams is None:
            mcp = [
                "makecsiparams",
                "-c",
                chanspec,
                "-C",
                coremask,
                "-N",
                nssmask,
            ]

            if macs is not None:
                mcp += ["-m", macs]

            if byte is not None:
                mcp += ["-b", byte]

            if delay is not None:
                mcp += ["-d", delay]

            csiparams = get_output(mcp)

        # fmt: off
        run_commands([
            ["ifconfig", "wlan0", "up"],
            ["nexutil", "-Iwlan0", "-s500", "-b", "-l34", f"-v{csiparams}"],
            ["iw", "dev", "wlan0", "interface", "add", "mon0", "type", "monitor"],
            ["ip", "link", "set", "mon0", "up"],
        ], spinner, log_title='cmd-up')
        # fmt: on
