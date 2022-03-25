#!/usr/bin/bash

# Elevate to root if not root already
[[ $UID != 0 ]] && exec sudo -E bash "$(readlink -f "$0")" "$@"

mount /dev/mmcblk0p1 /media
mv /media/container/* /media/
