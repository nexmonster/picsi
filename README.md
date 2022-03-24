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

picsi install
```


`picsi` will download the appropriate firmware and binaries for
your system and install them, or compile from source if they
are not available pre-compiled.


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

## Help page
```
Usage: picsi {{ COMMAND | help }} [--option] [--option argument]
       COMMAND := {{ install | uninstall | up | down | save | forward | rebuild | help }}
       OPTION  := {{ --url | --branch | --nexmon-url | --nexmon-branch | --apt-upgrade |
                    --no-source | --no-binaries | --binary-url }}

Examples: picsi help
          picsi install
          picsi install --url \"$NEX_REPO_URL\" --no-source

COMMAND

    i | install
        Installs Nexmon_CSI.
    U | uninstall
        Uninstalls Nexmon_CSI. Note: Upppercase U.
    e | Enable
        Enables CSI collection. WiFi will be disabled.
    d | disable
        Disables CSI collection and enables WiFi.
    s | save
        Save CSI to pcap file
    f | forward | fw
        Forward CSI packets to another IP
    r | rebuild
        Rebuilds the Nexmon_CSI from source.
    h | help
        Shows this help page.

OPTION

    --url
        URL for the Nexmon_CSI repository to git clone.
        The default value is 'https://github.com/nexmonster/nexmon_csi.git'
    
    --branch
        The git branch name in the cloned repository to
        use. The default value is 'master'.
        A commit hash or git object hash would work too.

    --nexmon-url
        URL for the Nexmon base repository to git clone.
        The default value is 'https://github.com/seemoo-lab/nexmon.git',

    --nexmon-branch
        The git branch in the cloned repository to
        use. The default is value 'master'.
        A commit hash, or git object hash would work too.
    
    --apt-upgrade
        Runs apt upgrade before installing. Not recommended.
        Running apt upgrade might upgrade your kernel.

    --no-source
        Prevent Nex from compiling Nexmon_CSI from source. If this flag
        is not present, Nex will fall back to compiling Nexmon_CSI from
        source when pre-compiled binaries are not available.

    --no-binaries
        Nex tries to use pre-compiled binaries when available,
        and will fall back to compiling Nexmon_CSI from source when not.
        Supply this flag to prevent use of pre-compiled binaries.

    --binary-url
        URL for the repository with precompiled binaries.
        Default URL is 'https://github.com/nexmonster/nexcsi-bin.git'.

Notes:
    WiFi will be unavailable for use when Nexmon_CSI is being used.
    Use an Ethernet cable or a second WiFi adapter if you're using SSH.
```