__all__ = ["up"]


from pathlib import Path
from halo import Halo
from typer import Argument, Exit
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output
from picsi.commands.down import down as cmd_down


def up(
    chanspec: str = Argument(default="36/80"),
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

    # Check if firmware is disabled
    state_firmware_is_patched = Path("/home/pi/.picsi/state/firmware_is_patched")
    state_firmware_is_patched.parent.mkdir(exist_ok=True, parents=True)

    if not state_firmware_is_patched.is_file():
        print("Error. You need to run `picsi enable` before you can do this.")
        raise Exit(10)

    # Check if CSI collection is already running
    state_csicollection_is_up = Path("/var/run/picsi/state/csicollection_is_up")
    state_csicollection_is_up.parent.mkdir(exist_ok=True, parents=True)

    if state_csicollection_is_up.is_file():
        cmd_down()

    with Halo(spinner="dots") as spinner:
        if csiparams is None:
            spinner.text = "Generating CSI Params"
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
            "# Starting CSI collection",
            ["ip", "link", "set", "dev", "wlan0", "up"],
            ["nexutil", "-Iwlan0", "-s500", "-b", "-l34", f"-v{csiparams}"],

            "# Setting up mon0",
            ["iw", "dev", "wlan0", "interface", "add", "mon0", "type", "monitor"],
            ["ip", "link", "set", "mon0", "up"],
        ], spinner, log_title='cmd-up')
        # fmt: on

        spinner.text = "Checking for errors"

        is_error = False
        err_message = None

        if "mon0" not in get_output(["ip", "link", "show", "up"]):
            is_error = True
            err_message = "Interface mon0 couldn't be setup properly."

        nexutil_k = get_output(["nexutil", "-k"])

        if "0x6863, 85/160" in nexutil_k:
            is_error = True
            err_message = f"Nexutil reported an invalid chanspec.\n{nexutil_k}"

    if is_error:
        print(f"Error. {err_message}")
        print("The firmware has probably crashed.")
        print("Try restarting this pi and run `picsi up` again.")
        raise Exit(20)

    state_csicollection_is_up.touch()

    if chanspec is not None:
        print(f"Channel/Bandwidth: {chanspec}")
    print(f"Csiparams: {csiparams}")
