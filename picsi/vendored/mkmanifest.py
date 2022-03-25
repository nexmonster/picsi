import time
import hashlib
from pathlib import Path
import tomli_w

from picsi.vendored.get_uname import get_uname
from picsi.vendored.ci_read_author import ci_read_author
from picsi.vendored.ci_read_githash import ci_read_githash
from picsi.vendored.ci_read_distdate import ci_read_distdate
from picsi.vendored.ci_read_distlink import ci_read_distlink


def iterdir(dir_path: Path) -> dict:
    hashes = {}

    for child in dir_path.iterdir():
        if child.is_file():
            with open(child.resolve(), "rb") as infile:
                filehash = hashlib.sha256()
                filehash.update(infile.read())

                hashes[child.name] = {"hash": "", "hashtype": "sha256"}
                hashes[child.name]["hash"] = filehash.hexdigest()

        elif child.is_dir():
            hashes[child.name] = iterdir(child)

    return hashes


def mkmanifest(
    path_nexmon_csi_bin: Path,
    path_nexmon: Path,
    path_nexmon_csi: Path,
    url: str,
    branch: str,
    nexmon_url: str,
    nexmon_branch: str,
) -> None:

    manifest = {
        "author": ci_read_author(),
        "build": {
            "uname_a": get_uname("-a"),
            "uname_r": get_uname("-r"),
            "uname_v": get_uname("-v"),
            "rpios_date": ci_read_distdate(),
            "rpios_link": ci_read_distlink(),
            "timestamp": int(time.time()),
        },
        "nexmon_csi": {
            "repository": url,
            "branch": branch,
            "commit": ci_read_githash(path_nexmon_csi),
        },
        "nexmon": {
            "repository": nexmon_url,
            "branch": nexmon_branch,
            "commit": ci_read_githash(path_nexmon),
        },
        "contents": iterdir(path_nexmon_csi_bin),
    }

    with open(path_nexmon_csi_bin / "manifest.toml", "wb") as outfile:
        tomli_w.dump(manifest, outfile)


# mkmanifest(
#     Path(f"/home/pi/.picsi/bins/{get_uname('-r')}"),
#     Path("/home/pi/.picsi/nexmon"),
#     Path("/home/pi/.picsi/nexmon/patches/bcm43455c0/7_45_189/nexmon_csi"),
#     "https://github.com/seemoo-lab/nexmon_csi",
#     "master",
#     "https://github.com/seemoo-lab/nexmon.git",
#     "master",
# )
