from pathlib import Path


def ci_read_distdate(path_rpi_issue: Path = Path("/etc/rpi-issue")) -> str:
    # https://raspberrypi.stackexchange.com/questions/91548/how-to-get-the-release-date-of-os-in-raspberry-pi

    with open(path_rpi_issue, "r") as rpi_issue:
        line = rpi_issue.readline()

    return line.strip().split(" ")[-1]
