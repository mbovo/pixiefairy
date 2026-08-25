from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from pixiefairy import webapp
from pixiefairy.config import BootResponse, Config, MacEntry, cfg


@pytest.fixture(autouse=True)
def reset_settings():
    original = cfg.settings
    cfg.settings = Config().settings
    cfg.settings.api_key = "secret"
    yield
    cfg.settings = original


def test_health_endpoints():
    assert webapp.root() == {"health": "ok"}
    assert webapp.health() == {"status": "OK"}


def test_bootstrap_returns_boot_configuration(monkeypatch):
    response = BootResponse(kernel="vmlinuz", initrd=["initrd"], cmdline="quiet")
    monkeypatch.setattr(webapp, "parse_mac", Mock(return_value=response))

    assert webapp.bootstrap("aa:bb:cc:dd:ee:ff") is response


def test_bootstrap_converts_errors_to_bad_request(monkeypatch):
    monkeypatch.setattr(webapp, "parse_mac", Mock(side_effect=ValueError("invalid MAC")))

    with pytest.raises(HTTPException) as error:
        webapp.bootstrap("invalid")

    assert error.value.status_code == 400
    assert error.value.detail == "invalid MAC"


def test_config_requires_api_key():
    assert webapp.get_config("secret") is cfg.settings

    with pytest.raises(HTTPException) as error:
        webapp.get_config("wrong")

    assert error.value.status_code == 401


def test_defaults_and_mapping_endpoints():
    assert webapp.get_defaults() is cfg.settings.defaults
    assert webapp.get_mapping() == {}


def test_set_mapping_persists_authorized_update(monkeypatch):
    persist = Mock(return_value=True)
    mapping = MacEntry(role="worker")
    monkeypatch.setattr(cfg, "toFile", persist)

    assert webapp.set_mapping("aa:bb:cc:dd:ee:ff", "secret", mapping) is mapping
    assert cfg.settings.mapping["aa:bb:cc:dd:ee:ff"] is mapping
    persist.assert_called_once_with(cfg.settings.config_file)


def test_set_mapping_rejects_invalid_api_key(monkeypatch):
    persist = Mock()
    monkeypatch.setattr(cfg, "toFile", persist)

    with pytest.raises(HTTPException) as error:
        webapp.set_mapping("aa:bb:cc:dd:ee:ff", "wrong", MacEntry(role="worker"))

    assert error.value.status_code == 401
    persist.assert_not_called()
