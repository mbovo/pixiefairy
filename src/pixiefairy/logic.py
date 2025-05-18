import logging

import yaml
from .config import cfg, BootResponse


def parse_mac(mac: str) -> BootResponse:

    # defaults
    ret = {k: v for k, v in cfg.settings.defaults.boot.dict().items() if k in ["kernel", "initrd", "message", "cmdline"]}
    net = {k: v for k, v in cfg.settings.defaults.net.dict().items() if k not in ["dhcp"]}
    use_dhcp = cfg.settings.defaults.net.dhcp
    net_cmdline = ""

    if cfg.settings.defaults.deny_unknown_clients and mac not in cfg.settings.mapping:
        logging.warning(f"Unknown mac address {mac}, blocking boot process")
        raise Exception(f"mac address not found {mac}")

    if mac in cfg.settings.mapping:
        mapping = cfg.settings.mapping[mac]

        # override boot defaults with parameters from mapping
        if mapping.boot is not None:
            for k, v in mapping.boot.dict().items():
                if v is not None:
                    ret[k] = v

        # override net defaults with paramenters from mapping
        if mapping.net is not None:
            for k, v in mapping.net.dict().items():
                if v is not None and k not in ["dhcp"]:
                    net[k] = v

            # override dhcp with parameters from mapping
            if mapping.net.dhcp is not None:
                use_dhcp = mapping.net.dhcp

    # enable net cmdline if required (dhcp=false)
    if not use_dhcp:
        ip = net["ip"] if "ip" in net else ""
        server = net["server"] if "server" in net else ""
        gateway = net["gateway"] if "gateway" in net else ""
        netmask = net["netmask"] if "netmask" in net else ""
        hostname = net["hostname"] if "hostname" in net else ""
        device = net["device"] if "device" in net else ""
        dns = net["dns"] if "dns" in net else ""
        ntp = net["ntp"] if "ntp" in net else ""
        net_cmdline = f" ip={ip}:{server}:{gateway}:{netmask}:{hostname}:{device}:off:{dns}::{ntp}"

    ret["cmdline"] = f"{ret['cmdline']}{net_cmdline}"

    logging.info(ret)

    return BootResponse(**ret)
