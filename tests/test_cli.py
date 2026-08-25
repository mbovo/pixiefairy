from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import pixiefairy.cli as cli_module
from pixiefairy.config import Config, cfg


@pytest.fixture(autouse=True)
def reset_settings():
    original = cfg.settings
    cfg.settings = Config().settings
    yield
    cfg.settings = original


def test_main_sets_up_logging_signals_and_cli(monkeypatch):
    setup_logging = Mock()
    set_sig_handler = Mock()
    cli = Mock()
    monkeypatch.setattr(cli_module.common, "setup_logging", setup_logging)
    monkeypatch.setattr(cli_module, "set_sig_handler", set_sig_handler)
    monkeypatch.setattr(cli_module, "cli", cli)

    cli_module.main()

    setup_logging.assert_called_once_with()
    set_sig_handler.assert_called_once_with(cli_module.sig_handler)
    cli.assert_called_once_with()


def test_start_populates_missing_runtime_settings(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("", encoding="utf-8")
    server_run = Mock()
    monkeypatch.setattr(cfg, "fromFile", Mock(return_value=True))
    monkeypatch.setattr(cli_module.common, "get_hostname", lambda: "10.0.0.2")
    monkeypatch.setattr(cli_module.uuid, "uuid4", lambda: "generated-key")
    monkeypatch.setattr(cli_module.server, "run", server_run)

    cli_module.start(config_file, "127.0.0.1", 8080, None, tmp_path)

    assert cfg.settings.listen_address == "127.0.0.1"
    assert cfg.settings.listen_port == 8080
    assert cfg.settings.config_file == config_file
    assert cfg.settings.external_url == "http://10.0.0.2:8080"
    assert cfg.settings.template_dir == tmp_path
    assert cfg.settings.api_key == "generated-key"
    server_run.assert_called_once_with()


def test_start_preserves_file_settings(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    cfg.settings.listen_address = "10.0.0.1"
    cfg.settings.listen_port = 9000
    cfg.settings.config_file = Path("saved.yaml")
    cfg.settings.external_url = "https://pixiefairy.example"
    cfg.settings.template_dir = tmp_path
    cfg.settings.api_key = "existing-key"
    get_hostname = Mock()
    monkeypatch.setattr(cfg, "fromFile", Mock(return_value=True))
    monkeypatch.setattr(cli_module.common, "get_hostname", get_hostname)
    monkeypatch.setattr(cli_module.server, "run", Mock())

    cli_module.start(config_file, "127.0.0.1", 8080, "https://override.example", tmp_path)

    assert cfg.settings.listen_address == "10.0.0.1"
    assert cfg.settings.listen_port == 9000
    assert cfg.settings.config_file == Path("saved.yaml")
    assert cfg.settings.external_url == "https://pixiefairy.example"
    assert cfg.settings.api_key == "existing-key"
    get_hostname.assert_not_called()


def test_start_exits_when_config_cannot_be_loaded(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "fromFile", Mock(return_value=False))

    with pytest.raises(SystemExit) as error:
        cli_module.start(tmp_path / "missing.yaml", "127.0.0.1", 8080, None, tmp_path)

    assert error.value.code == 1


def test_signal_handler_stops_only_for_shutdown_signals(monkeypatch):
    stop = Mock()
    stack = object()
    monkeypatch.setattr(cli_module.server, "stop", stop)

    assert cli_module.sig_handler(2, stack) is stack
    assert cli_module.sig_handler(99, stack) is stack
    stop.assert_called_once_with()


def test_set_signal_handler_skips_unsupported_signals(monkeypatch):
    register = Mock(side_effect=[None, OSError("unsupported")])
    fake_signal = SimpleNamespace(SIGA=1, SIGB=2, signal=register)
    warning = Mock()
    monkeypatch.setattr(cli_module, "signal", fake_signal)
    monkeypatch.setattr(cli_module.logging, "warning", warning)

    cli_module.set_sig_handler(Mock(), avoid=[])

    assert register.call_count == 2
    assert warning.call_count >= 1
