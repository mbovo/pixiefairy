import pytest

from pixiefairy.config import BootSection, Defaults, MacEntry, NetworkSection, Settings, cfg
from pixiefairy.logic import parse_mac


@pytest.fixture(autouse=True)
def configured_settings():
    original = cfg.settings
    cfg.settings = Settings(
        external_url="http://pixiefairy:5000",
        defaults=Defaults(
            boot=BootSection(kernel="vmlinuz", initrd=["initrd"], cmdline="console=ttyS0"),
            net=NetworkSection(dhcp=True),
            deny_unknown_clients=False,
            role="worker",
        ),
        mapping={"aa:bb:cc:dd:ee:ff": MacEntry(role="controlplane")},
    )
    yield
    cfg.settings = original


def test_parse_mac_accepts_mapping_without_network_settings():
    response = parse_mac("aa:bb:cc:dd:ee:ff")

    assert response.kernel == "vmlinuz"
    assert response.cmdline == "console=ttyS0 talos.config=http://pixiefairy:5000/v1/cluster/controlplane"


def test_parse_mac_uses_defaults_for_unknown_client():
    response = parse_mac("00:00:00:00:00:00")

    assert response.model_dump() == {
        "kernel": "vmlinuz",
        "initrd": ["initrd"],
        "message": None,
        "cmdline": "console=ttyS0 talos.config=http://pixiefairy:5000/v1/cluster/worker",
    }


def test_parse_mac_applies_boot_and_static_network_overrides():
    cfg.settings.mapping["aa:bb:cc:dd:ee:ff"] = MacEntry(
        boot=BootSection(kernel="custom-kernel", initrd=["custom-initrd"], message="Booting", cmdline="quiet"),
        net=NetworkSection(
            dhcp=False,
            ip="10.0.0.2",
            server="10.0.0.1",
            gateway="10.0.0.1",
            netmask="255.255.255.0",
            hostname="node-1",
            device="eth0",
            dns="1.1.1.1",
            ntp="10.0.0.1",
        ),
        role="controlplane",
    )

    response = parse_mac("aa:bb:cc:dd:ee:ff")

    assert response.kernel == "custom-kernel"
    assert response.initrd == ["custom-initrd"]
    assert response.message == "Booting"
    assert response.cmdline == (
        "quiet ip=10.0.0.2:10.0.0.1:10.0.0.1:255.255.255.0:node-1:eth0:off:1.1.1.1::10.0.0.1" " talos.config=http://pixiefairy:5000/v1/cluster/controlplane"
    )


def test_parse_mac_rejects_unknown_client_when_denied():
    cfg.settings.defaults.deny_unknown_clients = True

    with pytest.raises(Exception, match="mac address not found"):
        parse_mac("00:00:00:00:00:00")
