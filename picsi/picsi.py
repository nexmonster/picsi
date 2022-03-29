#!/usr/bin/env python3

import os

# Elevate picsi to root if not running as root
if os.getuid() != 0:
    import sys
    import subprocess
    from picsi.vendored.get_output import get_output

    executable = get_output(["which", "picsi"])
    arguments = sys.argv[1:]

    p = subprocess.run(["sudo", "-E", executable] + sys.argv[1:])

    sys.exit(p.returncode)
else:
    from picsi.vendored.get_output import get_output

    get_output(["chown", "-R", "pi:pi", "/home/pi/.picsi"])


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
