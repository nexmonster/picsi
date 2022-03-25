import subprocess


def get_PATH() -> str:

    # We can't use get_output because get_output uses get_PATH
    p: subprocess.CompletedProcess = subprocess.run(
        ["/usr/bin/env"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        encoding="utf-8",
    )

    env = p.stdout.strip().split("\n")

    for line in env:
        splits = line.strip().split("=")

        head = splits[0]
        tail = "=".join(splits[1:])

        if head == "PATH":
            return tail

    return ":".join(
        [
            "/home/pi/.local/bin",
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
            "/usr/local/games",
            "/usr/games",
        ]
    )
