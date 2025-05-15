# Pixie Fairy - a Pixiecore API companion

[![](https://img.shields.io/pypi/v/pixiecore.svg)](https://pypi.org/pypi/pixiefairy)
[![Tag and build](https://github.com/mbovo/pixiefairy/actions/workflows/build-image.yml/badge.svg)](https://github.com/mbovo/pixiefairy/actions/workflows/build-image.yml)

`Pixiefairy` is a companion for [pixiecore](https://github.com/danderson/netboot/tree/master/pixiecore) a tool to manage network booting of machines.
`Pixiecore` in [API mode](https://github.com/danderson/netboot/tree/master/pixiecore#pixiecore-in-api-mode) send a request to an external service for each pxe booting event; *pixiefairy* is that service, answering to api calls and serving the configured info, like the kernel, the initrd and the command line to boot.

> `Pixiecore` [API specification](https://github.com/danderson/netboot/blob/2ed7bd30206a51bae786b02d9a5b8156fdcc8870/pixiecore/README.api.md)

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

In order to partecipate to the development you need the following requirements

- [Taskfile](https://taskfile.dev)
- Python >=3.9

And bootstrap the local dev environment with:

```bash
task setup
```

This will setup locally a python virtualenv with all the dependencies, ready to start coding

## Maintainability

The project ships with `default.nix` with Nixpkgs dependencies pinned.
When Nixpkgs evolves, the Python dependencies might get breaking updates, so choosing stable dependencies is key.

This fork started off by refactoring `config.py` to work with `pydantic-yaml` that was in Nixpkgs.

### Dependency stability matrix

| Package           | Stability tier      | Notes & alternatives                                              |
| ----------------- | ------------------- | ----------------------------------------------------------------- |
| **click**         | ★★★★★ (very stable) | Mature CLI lib; minor bumps almost never break you.               |
| **colorama**      | ★★★★★               | Simple console-color wrapper; stable.                             |
| **shellingham**   | ★★★★★               | Tiny utility; unlikely to change.                                 |
| **PyYAML**        | ★★★★☆ (stable)      | Battle-tested YAML parser; occasional security fixes.             |
| **uvicorn** | ★★★★☆ | Core ASGI server; minor bumps rarely break, but watch the asyncio stack. |
| **urllib3**       | ★★★★☆               | Core HTTP layer; well maintained by Requests team.                |
| **loguru**        | ★★★☆☆ (moderate)    | Nice API but less widely deployed; watch for minor changes.       |
| **typer**         | ★★★★☆               | Built on Click; quite stable, but tied to Click’s major versions. |
| **pydantic-yaml** | ★★☆☆☆ (risky)       | Not very popular or actively maintained; Has lead to problems in the past. |
| **fastapi** | ★★★★☆ | Rapidly evolving but major bumps (0.XX → 1.0) are rare; keep an eye on release notes. |
| **gevent** | ★★☆☆☆ (legacy) | Green-threading can conflict with other async libs; if you’re fully on AsyncIO, drop gevent. |
