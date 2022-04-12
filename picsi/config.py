from pathlib import Path
from tomli import load

path_config = Path(__file__).parent / "config.toml"

with open(path_config, "rb") as config_file:
    config = load(config_file)
