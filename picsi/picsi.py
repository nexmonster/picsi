#!/usr/bin/env python3
from os import getuid
from sys import argv
from sys import exit as sys_exit
from subprocess import run
from importlib import import_module

from typer import Typer
from click import Group

from picsi.vendored.get_output import get_output


if getuid() != 0:
    # If not running as root
    executable = get_output(["which", "picsi"])

    # Start picsi as root
    p = run(["sudo", "-E", executable] + argv[1:])

    sys_exit(p.returncode)
# else:
#     get_output(["chown", "-R", "pi:pi", "/home/pi/.picsi"])


# Typer prints commands in the help menu
# in a random order. This fixes that
# https://skeptric.com/typer-command-order/
class NaturalOrderGroup(Group):
    def list_commands(self, ctx):
        return self.commands.keys()


commands = [
    "install",
    "uninstall",
    "enable",
    "disable",
    "up",
    "down",
    "status",
    "build",
]

app = Typer(cls=NaturalOrderGroup)
for command in commands:
    module = import_module(f"picsi.commands.{command}")

    app.command()(getattr(module, command))

if __name__ == "__main__":
    app()
