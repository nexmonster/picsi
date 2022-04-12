from picsi.vendored.get_uname import get_uname
from picsi.config import config


def check_kernel_version():
    current_kernel_version = ".".join(get_uname("-r").split(".")[:2])

    if current_kernel_version in config.supported_kernels:
        return True

    print(
        "Warning: Nexmon_csi is only available for kernel versions: "
        + ", ".join(config.supported_kernels)
        + ".\n"
        + "You are running Kernel version "
        + current_kernel_version
        + "."
    )

    return False


def check_cpu_arch():
    current_cpu_architecture = get_uname("-m")

    if current_cpu_architecture in config.supported_archs:
        return True

    print(
        "Warning: Nexmon_csi is only available for architectures: "
        + ", ".join(config.supported_archs)
        + ".\n"
        + "Your current architecture is "
        + current_cpu_architecture
        + "."
    )

    return False


def check_platform():
    return check_cpu_arch() and check_kernel_version()
