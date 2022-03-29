# picsi

Nexmon CSI utilities for Raspberry Pi

***In development &bull; Not ready for testing yet.***

## Features

- [x] ⚡ **Superfast** installs with pre-compiled binaries
- [x] ⌛ Compiles from source when binaries are not available
- [x] 🚀 Easy Start/Stop CSI collection with `picsi up` or `picsi down`
- [x] ✨ Restore original firmware and connect to WiFi with `picsi disable`
- [ ] 💾 Saves CSI to .pcap files
- [ ] 📡 Forward CSI packets to other devices for faster collection
- [ ] 📁 Manage your CSI collection configuration with Profiles

## Install 

On a Raspberry Pi 3B+ or 4B, run:  

```bash
sudo apt install python3-pip  # install pip for python3
pip3 install picsi            # install picsi 
source ~/.profile             # update $PATH

picsi install                 # install nexmon_csi
```


`picsi` will download the appropriate firmware and binaries for
your system and install them, or compile from source if they
are not available pre-compiled.

## Usage
```bash
picsi enable                  # enable nexmon_csi
picsi up                      # Collect CSI on 36/80
```

This enables Nexmon_csi, and starts CSI collection on channel 36 with
bandwidth 80 MHz. You can see the traffic with `tcpdump -i wlan0 dst port 5500`.

More examples:
```
picsi up 149/80               # Collect CSI on 149/80

picsi down                    # Stop CSI collection
picsi disable                 # Restore original WiFi

picsi status                  # See status

picsi --help                  # See the help page
```

## Docs

Picsi (pronounced pixie?) is a Python tool to install Nexmon CSI on Raspberry Pis.
It needs Python version `>= 3.7`, although using the latest version is recommended.

The best features of picsi, in my opinion, are:

#### Installing Nexmon CSI from pre-compiled binaries.

Compiling Nexmon_CSI on the Pi takes about an hour, and downloads about 1.5 GB of data.
And it needs your attention for the entire duration because you need to reboot the Pi 
multiple times, and keep a look out for errors.

Picsi downloads appropriate pre-compiled nexmon_csi firmware and binaries (nexutil, makecsiparams) 
for your kernel from https://github.com/nexmonster/nexcsi-bin.git (repository not available yet), 
and installs them. If binaries are not available, it installs from source, including automatic 
unattended reboots, and logs errors and progress.

#### Forwards CSI packets to an IP

Picsi can forward CSI packets to a different computer on your network, which is potentially
faster than the Pi, and can collect more packets than tcpdump on the Pi can.

But additionally, an app on your phone/laptop can listen to the packets,
and plot the CSI in realtime or process it.

#### Profiles!

Manage your csi collection configuration in profiles!

write
```toml
[profiles.CustomProfileName]
    channel = 36
    bandwidth = 80

    coremask = 1
    ssmask = 1

    forward = false
    forward_ip = '192.168.1.25'

    duration = 30

    macids = ['ab:cd:ef:12:34']
```

in profiles.toml, and you can start csi collection with

`picsi up CustomProfileName`.

This collects CSI on channel 36, bandwidth 80 from macids for 30 seconds,
and forwards that CSI to 192.168.1.25. After 30 seconds, CSI collection is stopped
and original wifi firmware is restored.

You can also create a set of profiles, and make picsi loop CSI collection over them.

Only basic CSI collection via profiles will be added first, and other profile features will
be added later.
