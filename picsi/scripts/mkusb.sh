#!/usr/bin/bash

# Elevate to root if not root already
[[ $UID != 0 ]] && exec sudo -E bash "$(readlink -f "$0")" "$@"

shopt -s extglob

if [ ! -f "$1/$1.zip" ]; then
    echo "mkusb err: File not found $1"
    exit 1
fi

unzip -p "$1/$1.zip" | pv | sudo dd bs=1M of=/dev/sda

mkdir -p /tmp/mkusb/{boot,root}

sudo mount /dev/sda1 /tmp/mkusb/boot
sudo mount /dev/sda2 /tmp/mkusb/root

touch /tmp/mkusb/boot/ssh
cp "$1"/picsi-ci.toml /tmp/mkusb/boot/picsi-ci.toml

echo 'Acquire::http { Proxy "http://10.20.30.40:3142"; }' | sudo tee -a /tmp/mkusb/root/etc/apt/apt.conf.d/proxy

mkdir /tmp/mkusb/root/home/pi/.ssh
chmod 700 /tmp/mkusb/root/home/pi/.ssh
cp /home/pi/.ssh/authorized_keys /tmp/mkusb/root/home/pi/.ssh/

chown pi  /tmp/mkusb/root/home/pi/.ssh -R

# Disable boot on current drive
mkdir -p /boot/container
mv /boot/!(container) /boot/container/

# sudo picsi build --nexmon-url="http://10.20.30.41/seemoo-lab/nexmon.git" --url="http://10.20.30.41/seemoo-lab/nexmon_csi.git"