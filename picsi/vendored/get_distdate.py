from pathlib import Path


def get_distdate(path_rpi_issue: Path = Path("/etc/rpi-issue")):
    # https://raspberrypi.stackexchange.com/questions/91548/how-to-get-the-release-date-of-os-in-raspberry-pi

    with open(path_rpi_issue, "r") as rpi_issue:
        for line in rpi_issue:
            return line.strip().split(" ")[-1]
