#!/usr/bin/env python3

import typer
from click import Group

from picsi.commands.install import install
from picsi.commands.uninstall import uninstall
from picsi.commands.up import up
from picsi.commands.down import down
from picsi.commands.build import build

# Typer prints commands in the help menu
# in a random order. This fixes that
# https://skeptric.com/typer-command-order/
class NaturalOrderGroup(Group):
    def list_commands(self, ctx):
        return self.commands.keys()


app = typer.Typer(cls=NaturalOrderGroup)

app.command()(install)
app.command()(uninstall)

app.command()(up)
app.command()(down)

app.command()(build)

if __name__ == "__main__":
    app()
