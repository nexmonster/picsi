__all__ = ["build"]

from halo import Halo
from pathlib import Path

from picsi.vendored.mkmanifest import mkmanifest
from picsi.vendored.run_commands import run_commands
from picsi.vendored.get_output import get_output
from picsi.vendored.get_uname import get_uname


def build(
    url: str = "https://github.com/seemoo-lab/nexmon_csi",
    branch: str = "master",
    nexmon_url: str = "https://github.com/seemoo-lab/nexmon.git",
    nexmon_branch: str = "master",
):
    """
    Build Nexmon_CSI from source
    """

    Path("/home/pi/.picsi/").mkdir(exist_ok=True)

    path_nexmon = Path("/home/pi/.picsi/nexmon")
    path_nexmon_csi = Path(
        "/home/pi/.picsi/nexmon/patches/bcm43455c0/7_45_189/nexmon_csi"
    )
    path_nexmon_csi_bin = Path(f"/home/pi/.picsi/bins/{get_uname('-r')}")

    nexmon_kversion = ".".join(get_uname("-r").split(".")[:2]) + ".y"

    with Halo(spinner="dots") as spinner:

        # fmt: off
        run_commands([
            "# Setting up WiFi",
            ["/usr/sbin/rfkill", "unblock", "all"],
            ["/usr/bin/raspi-config", "nonint", "do_wifi_country", "US"],

            "# Expanding SD card",
            ["/usr/bin/raspi-config", "nonint", "do_expand_rootfs"],

            "# Installing Dependencies",
            ["/usr/bin/apt", "update"],
            ["/usr/bin/apt", "install", "-y",
                "automake", "bc", "bison", "flex", "gawk", "git",
                "libgmp3-dev", "libncurses5-dev", "libssl-dev",
                "libtool-bin", "make", "python-is-python2", "qpdf",
                "raspberrypi-kernel-headers", "texinfo",
            ],
        ], spinner)
        # fmt: on

        uname_r = get_uname("-r")
        kernel_headers = Path(f"/lib/modules/{uname_r}/build/Kconfig")

        if not kernel_headers.is_file():
            # fmt: off
            run_commands([
                "# Installing Kernel headers",
                ["/usr/bin/wget", "https://raw.githubusercontent.com/RPi-Distro/rpi-source/master/rpi-source", "-O", "/usr/local/bin/rpi-source"],
                ["/usr/bin/chmod", "+x", "/usr/local/bin/rpi-source"],
                ["/usr/local/bin/rpi-source", "-q", "--tag-update"],
                ["/usr/local/bin/rpi-source"]
            ], spinner)
            # fmt: on

        # fmt: off
        run_commands([
            "# Backing up original binaries",
            ["/usr/bin/mkdir", "-p",
                path_nexmon_csi_bin / "makecsiparams/",
                path_nexmon_csi_bin / "nexutil/",
                path_nexmon_csi_bin / "original/",
                path_nexmon_csi_bin / "patched/",
            ],
            ["/usr/bin/cp",
                "/lib/firmware/brcm/brcmfmac43455-sdio.bin",
                path_nexmon_csi_bin / "original/",
            ],
            ["/usr/bin/cp",
                get_output(["/usr/sbin/modinfo", "brcmfmac", "-n"]),
                path_nexmon_csi_bin / "original/",
            ],

            "# Downloading Nexmon",
            ["/usr/bin/git", "clone", nexmon_url, path_nexmon],
            "cd " + str(path_nexmon),
            ["/usr/bin/git", "checkout", nexmon_branch],

            "# Downloading Nexmon_CSI",
            ["/usr/bin/git", "clone", url, path_nexmon_csi],
            "cd " + str(path_nexmon_csi),
            ["/usr/bin/git", "checkout", branch],

            "# Building libISL",
            "cd " + str(path_nexmon / "buildtools/isl-0.10/"),
            ["/usr/bin/autoreconf", "-f", "-i"],
            [path_nexmon / "buildtools/isl-0.10/configure"],
            ["/usr/bin/make"],
            ["/usr/bin/make", "install"],
            ["/usr/bin/ln",
                "-s", "/usr/local/lib/libisl.so",
                "/usr/lib/arm-linux-gnueabihf/libisl.so.10"
            ],

            "# Building libMPFR",
            "cd " + str(path_nexmon / "buildtools/mpfr-3.1.4/"),
            ["/usr/bin/autoreconf", "-f", "-i"],
            [path_nexmon / "buildtools/mpfr-3.1.4/configure"],
            ["/usr/bin/make"],
            ["/usr/bin/make", "install"],
            ["/usr/bin/ln",
                "-s", "/usr/local/lib/libmpfr.so",
                "/usr/lib/arm-linux-gnueabihf/libmpfr.so.4"
            ],
        ], spinner)
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
            ["sudo", "-E", "bash", "-c", "/usr/bin/make"],

            "# Building Nexmon_CSI",
            "cd " + str(path_nexmon_csi),
            ["sudo", "-E", "bash", "-c", "/usr/bin/make install-firmware"],

            "# Building Makecsiparams",
            "cd " + str(path_nexmon_csi / "utils/makecsiparams"),
            ["sudo", "-E", "bash", "-c", "/usr/bin/make"],

            "# Building Nexutil",
            "cd " + str(path_nexmon / "utilities/nexutil/"),
            ["sudo", "-E", "bash", "-c", "/usr/bin/make"],

            "# Packaging Binaries",
            ["/usr/bin/cp",
                path_nexmon / "utilities/nexutil/nexutil", 
                path_nexmon_csi_bin / "nexutil/"
            ],
            ["/usr/bin/cp",
                path_nexmon_csi / "utils/makecsiparams/makecsiparams",
                path_nexmon_csi_bin / "makecsiparams/",
            ],
            ["/usr/bin/cp",
                path_nexmon_csi / ("brcmfmac_" + nexmon_kversion + "-nexmon/brcmfmac.ko"),
                path_nexmon_csi_bin / "patched/",
            ],
            ["/usr/bin/cp",
                path_nexmon_csi / "brcmfmac43455-sdio.bin",
                path_nexmon_csi_bin / "patched/",
            ],
        ], spinner, env=env)
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
            ["/usr/bin/tar", "-cvJf", f"{get_uname('-r')}.tar.xz", f"{get_uname('-r')}"]
        ], spinner)
        # fmt: on
