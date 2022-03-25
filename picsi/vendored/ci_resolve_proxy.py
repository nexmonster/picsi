from pathlib import Path
import tomli


# I have a git mirror at 10.20.30.41 for nexmon and nexmon_csi
# When creating picsi builds, the repositories are cloned from
# there to speed up cloning.
def ci_resolve_proxy(
    key: str, section: str, ci_file: Path = Path("/boot/picsi-ci.toml")
) -> str:
    if ci_file.is_file():
        with open(ci_file, "rb") as f:
            ci_config = tomli.load(f)

            if section in ci_config["proxy"]:
                if key in ci_config["proxy"][section]:
                    return ci_config["proxy"][section][key]

    return key
