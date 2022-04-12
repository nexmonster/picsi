#!/usr/bin/env python3

import os
import sys

# Elevate picsi to root if not running as root
if os.getuid() != 0:
    import subprocess
    from picsi.vendored.get_output import get_output

    executable = get_output(["which", "picsi"])
    arguments = sys.argv[1:]

    p = subprocess.run(["sudo", "-E", executable] + sys.argv[1:])

    sys.exit(p.returncode)
else:
    from picsi.vendored.get_output import get_output

    get_output(["chown", "-R", "pi:pi", "/home/pi/.picsi"])

# ---------------------------------------------------------------

import typer
from click import Group

from picsi.commands.install import install
from picsi.commands.uninstall import uninstall
from picsi.commands.enable import enable
from picsi.commands.disable import disable
from picsi.commands.build import build
from picsi.commands.up import up
from picsi.commands.down import down
from picsi.commands.status import status
from picsi.vendored.get_uname import get_uname

# Check if picsi can run on this kernel
supported_kernel_versions = ["4.19", "5.4", "5.10"]
current_kernel_version = ".".join(get_uname("-r").split(".")[:2])

if current_kernel_version not in supported_kernel_versions:
    print(
        "Warning: Nexmon_csi is only available for kernel versions: "
        + ", ".join(supported_kernel_versions)
        + ".\n"
        + "You are running Kernel version "
        + current_kernel_version
        + "."
    )

supported_cpu_architectures = ["armv7l", "armv7l+"]
current_cpu_architecture = get_uname("-m")

if current_cpu_architecture not in supported_cpu_architectures:
    print(
        "Warning: Nexmon_csi is only available for architectures: "
        + ", ".join(supported_cpu_architectures)
        + ".\n"
        + "You are running Kernel version "
        + current_kernel_version
        + "."
    )


# Typer prints commands in the help menu
# in a random order. This fixes that
# https://skeptric.com/typer-command-order/
class NaturalOrderGroup(Group):
    def list_commands(self, ctx):
        return self.commands.keys()


app = typer.Typer(cls=NaturalOrderGroup)

app.command()(install)
app.command()(uninstall)
app.command()(enable)
app.command()(disable)
app.command()(up)
app.command()(down)
app.command()(status)
app.command()(build)

if __name__ == "__main__":
    app()
