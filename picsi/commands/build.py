__all__ = ["build"]


from pathlib import Path
from sys import exit as sys_exit

from halo import Halo

from picsi.vendored.mkmanifest import mkmanifest
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output
from picsi.vendored.get_uname import get_uname
from picsi.vendored.ci_resolve_proxy import ci_resolve_proxy
from picsi.vendored.check_platform import check_platform


def build(
    url: str = "https://github.com/seemoo-lab/nexmon_csi",
    branch: str = "master",
    nexmon_url: str = "https://github.com/seemoo-lab/nexmon.git",
    nexmon_branch: str = "master",
):
    """
    Build Nexmon_CSI from source
    """

    if not check_platform():
        confirmation = input("Unsupported platform. Do you want to continue? [Y/n]: ")
        if confirmation.lower() in ["n", "no"]:
            sys_exit(1)

    Path("/home/pi/.picsi/").mkdir(exist_ok=True)

    path_nexmon = Path("/home/pi/.picsi/nexmon")
    path_nexmon_csi = Path(
        "/home/pi/.picsi/nexmon/patches/bcm43455c0/7_45_189/nexmon_csi"
    )
    path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")

    nexmon_kversion = ".".join(get_uname("-r").split(".")[:2]) + ".y"

    apt_deps = [
        "automake",
        "bc",
        "bison",
        "flex",
        "gawk",
        "git",
        "libgmp3-dev",
        "libncurses5-dev",
        "libssl-dev",
        "libtool-bin",
        "make",
        "qpdf",
        "raspberrypi-kernel-headers",
        "texinfo",
    ]

    if "Python 3" in get_output(["python", "--version"]):
        # In systems whose default python is python3,
        # python-is-python2 package is needed for Nexmon
        apt_deps.append("python-is-python2")

    with Halo(spinner="dots") as spinner:

        # fmt: off
        run_commands([
            "# Setting up WiFi",
            ["rfkill", "unblock", "all"],
            ["raspi-config", "nonint", "do_wifi_country", "US"],

            "# Expanding SD card",
            ["raspi-config", "nonint", "do_expand_rootfs"],

            "# Installing Dependencies",
            ["apt", "update", "-y"],
            ["apt", "install", "-y"] + apt_deps,
        ], spinner, log_title='cmd-build')
        # fmt: on

        uname_r = get_uname("-r")
        kernel_headers = Path(f"/lib/modules/{uname_r}/build/Kconfig")

        if not kernel_headers.is_file():
            # fmt: off
            run_commands([
                "# Installing Kernel headers",
                ["wget", "https://raw.githubusercontent.com/RPi-Distro/rpi-source/master/rpi-source", "-O", "/usr/local/bin/rpi-source"],
                ["chmod", "+x", "/usr/local/bin/rpi-source"],
                ["rpi-source", "-q", "--tag-update"],
                ["rpi-source"]
            ], spinner, log_title='cmd-build')
            # fmt: on

        # fmt: off
        run_commands([
            "# Backing up original binaries",
            ["mkdir", "-p",
                path_nexmon_csi_bin / "makecsiparams/",
                path_nexmon_csi_bin / "nexutil/",
                path_nexmon_csi_bin / "original/",
                path_nexmon_csi_bin / "patched/",
            ],
            ["cp",
                "/lib/firmware/brcm/brcmfmac43455-sdio.bin",
                path_nexmon_csi_bin / "original/",
            ],
            ["cp",
                get_output(["modinfo", "brcmfmac", "-n"]),
                path_nexmon_csi_bin / "original/",
            ],

            "# Downloading Nexmon",
            ["git", "clone", ci_resolve_proxy(nexmon_url, "git"), path_nexmon],
            "cd " + str(path_nexmon),
            ["git", "checkout", nexmon_branch],

            "# Downloading Nexmon_CSI",
            ["git", "clone", ci_resolve_proxy(url, "git"), path_nexmon_csi],
            "cd " + str(path_nexmon_csi),
            ["git", "checkout", branch],

            "# Building libISL",
            "cd " + str(path_nexmon / "buildtools/isl-0.10/"),
            ["autoreconf", "-f", "-i"],
            [path_nexmon / "buildtools/isl-0.10/configure"],
            ["make"],
            ["make", "install"],
            ["ln",
                "-s", "/usr/local/lib/libisl.so",
                "/usr/lib/arm-linux-gnueabihf/libisl.so.10"
            ],

            "# Building libMPFR",
            "cd " + str(path_nexmon / "buildtools/mpfr-3.1.4/"),
            ["autoreconf", "-f", "-i"],
            [path_nexmon / "buildtools/mpfr-3.1.4/configure"],
            ["make"],
            ["make", "install"],
            ["ln",
                "-s", "/usr/local/lib/libmpfr.so",
                "/usr/lib/arm-linux-gnueabihf/libmpfr.so.4"
            ],
        ], spinner, log_title='cmd-build')
        # fmt: on

        env = {
            "ARCH": "arm",
            "SUBARCH": "arm",
            "KERNEL": "kernel7",
            "HOSTUNAME": get_uname("-s"),
            "PLATFORMUNAME": get_uname("-m"),
            "NEXMON_ROOT": str(path_nexmon),
            "CC": str(
                path_nexmon
                / "buildtools/gcc-arm-none-eabi-5_4-2016q2-linux-armv7l/bin/arm-none-eabi-"
            ),
            "CCPLUGIN": str(path_nexmon / "buildtools/gcc-nexmon-plugin-arm/nexmon.so"),
            "ZLIBFLATE": "zlib-flate -compress",
            "Q": "@",
            "NEXMON_SETUP_ENV": "1",
        }

        # fmt: off
        run_commands([
            "# Extracting UCODE, TemplateRAM, and FlashPatches",
            "cd " + str(path_nexmon),
            ["sudo", "-E", "bash", "-c", "make"],

            "# Building Nexmon_CSI",
            "cd " + str(path_nexmon_csi),
            ["sudo", "-E", "bash", "-c", "make install-firmware"],

            "# Building Makecsiparams",
            "cd " + str(path_nexmon_csi / "utils/makecsiparams"),
            ["sudo", "-E", "bash", "-c", "make"],

            "# Building Nexutil",
            "cd " + str(path_nexmon / "utilities/nexutil/"),
            ["sudo", "-E", "bash", "-c", "make"],

            "# Packaging Binaries",
            ["cp",
                path_nexmon / "utilities/nexutil/nexutil", 
                path_nexmon_csi_bin / "nexutil/"
            ],
            ["cp",
                path_nexmon_csi / "utils/makecsiparams/makecsiparams",
                path_nexmon_csi_bin / "makecsiparams/",
            ],
            ["cp",
                path_nexmon_csi / ("brcmfmac_" + nexmon_kversion + "-nexmon/brcmfmac.ko"),
                path_nexmon_csi_bin / "patched/",
            ],
            ["cp",
                path_nexmon_csi / "brcmfmac43455-sdio.bin",
                path_nexmon_csi_bin / "patched/",
            ],
        ], spinner, env=env, log_title='cmd-build')
        # fmt: on

        # Writes the manifest.toml file
        mkmanifest(
            path_nexmon_csi_bin,
            path_nexmon,
            path_nexmon_csi,
            url,
            branch,
            nexmon_url,
            nexmon_branch,
        )

        # fmt: off
        run_commands([
            # When full path is used for tar, that path is preserved in the
            # archive created.
            "cd " + str((path_nexmon_csi_bin / "..").resolve()),
            ["tar", "-cvJf", f"{get_uname('-r')}.tar.xz", f"{get_uname('-r')}"]
        ], spinner, log_title='cmd-build')
        # fmt: on
