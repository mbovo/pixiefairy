# Pixie Fairy - a Pixiecore API companion

[![](https://img.shields.io/pypi/v/pixiecore.svg)](https://pypi.org/pypi/pixiefairy)
[![Tag and build](https://github.com/mbovo/pixiefairy/actions/workflows/build-image.yml/badge.svg)](https://github.com/mbovo/pixiefairy/actions/workflows/build-image.yml)

`Pixiefairy` is a companion for [pixiecore](https://github.com/danderson/netboot/tree/master/pixiecore) a tool to manage network booting of machines.
`Pixiecore` in [API mode](https://github.com/danderson/netboot/tree/master/pixiecore#pixiecore-in-api-mode) send a request to an external service for each pxe booting event; *pixiefairy* is that service, answering to api calls and serving the configured info, like the kernel, the initrd and the command line to boot.

`Pixiefairy` is higly configurable, you can decide which mac-address and which set of parameters to serve to each client.

## Installation

Pixiefairy requires `python >= 3.9`
It's as easy as

```bash
pip3 install pixiefairy
```

Then you will have available the `pixiefairy` binary

## Usage

Pixiefairy can be started using the `start` command. It requires a config.yaml file with a bunch of defaults in order to know how to serve the requests.

```bash
pixiefairy start -c config.yaml
```

## Configuration

An example configuration can be found into [examples/config.yaml](./examples/config.yaml) like

```yaml
defaults:
  boot:
                # the kernel to boot into
    kernel: "file:///root/vmlinuz-amd64"
    initrd:     # the list of initrd files to load at boot
      - "file:///root/initramfs-amd64.xz"
    message: "" # optional, a boot message
    cmdline: "" # optional, the command line to boot
  net:
    dhcp: true                 # use dhcp or send n ip=.... kernel parameters to configure the network
    gateway: "192.168.1.0"     # the default gateway to send to the requestor
    netmask: "255.255.255.0"   # the netmask to send to requestor
    dns: "8.8.8.8"         # default dns server
    ntp: "192.168.1.0"         # default ntp server
  deny_unknown_clients: false  # either boot unknown clients or boot only the mac address listed in mapping below
mapping:  # optional
  aa:bb:cc:dd:ee:ff:  # the matching mac address
    net: null             # net block, optional, identical to the net block in defaults, override
    boot: null            # boot block, optional, identical to the boot block in defaults, override
```

## Dev Requirements

In order to participate in development you need the following requirements:

- [just](https://just.systems)
- [Poetry](https://python-poetry.org)
- Python 3.14

And bootstrap the local dev environment with:

```bash
just setup
```

This will setup locally a python virtualenv with all the dependencies, ready to start coding
