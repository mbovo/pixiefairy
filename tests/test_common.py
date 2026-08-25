import logging
from types import SimpleNamespace
from unittest.mock import Mock

from pixiefairy import common


def test_setup_logging_redirects_standard_logging(monkeypatch):
    disable_warnings = Mock()
    basic_config = Mock()
    monkeypatch.setattr(common.urllib3, "disable_warnings", disable_warnings)
    monkeypatch.setattr(common.logging, "basicConfig", basic_config)

    common.setup_logging("DEBUG")

    disable_warnings.assert_called_once_with()
    assert isinstance(basic_config.call_args.kwargs["handlers"][0], common.InterceptHandler)
    assert basic_config.call_args.kwargs["level"] == "DEBUG"


def test_intercept_handler_forwards_known_and_custom_levels(monkeypatch):
    logger = Mock()
    logger.level.return_value = SimpleNamespace(name="INFO")
    monkeypatch.setattr(common, "logger", logger)
    handler = common.InterceptHandler()

    handler.emit(logging.LogRecord("test", logging.INFO, __file__, 1, "hello", (), None))
    logger.opt.return_value.log.assert_called_once_with("INFO", "hello")

    logger.reset_mock()
    logger.level.side_effect = ValueError
    handler.emit(logging.LogRecord("test", 35, __file__, 1, "custom", (), None))
    logger.opt.return_value.log.assert_called_once_with(35, "custom")


def test_get_hostname_uses_resolved_hostname(monkeypatch):
    monkeypatch.setattr(common.socket, "gethostname", lambda: "pixiefairy")
    monkeypatch.setattr(common.socket, "gethostbyname", lambda hostname: "10.0.0.2")

    assert common.get_hostname() == "10.0.0.2"


def test_get_hostname_falls_back_to_outbound_address(monkeypatch):
    sock = Mock()
    sock.getsockname.return_value = ("10.0.0.3", 12345)
    monkeypatch.setattr(common.socket, "gethostbyname", Mock(side_effect=OSError))
    monkeypatch.setattr(common.socket, "socket", Mock(return_value=sock))

    assert common.get_hostname() == "10.0.0.3"
    sock.connect.assert_called_once_with(("8.8.8.8", 80))
    sock.close.assert_called_once_with()


def test_get_hostname_falls_back_to_loopback(monkeypatch):
    sock = Mock()
    sock.connect.side_effect = OSError
    monkeypatch.setattr(common.socket, "gethostbyname", Mock(side_effect=OSError))
    monkeypatch.setattr(common.socket, "socket", Mock(return_value=sock))

    assert common.get_hostname() == "127.0.0.1"
    sock.close.assert_called_once_with()
