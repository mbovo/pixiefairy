from unittest.mock import Mock

import pytest

from pixiefairy import server
from pixiefairy.config import Config as AppConfig
from pixiefairy.config import cfg


@pytest.fixture(autouse=True)
def reset_server_state(monkeypatch):
    original_settings = cfg.settings
    cfg.settings = AppConfig().settings
    cfg.settings.listen_address = "127.0.0.1"
    cfg.settings.listen_port = 5000
    monkeypatch.setattr(server, "thread_pool", None)
    monkeypatch.setattr(server, "stop_event", None)
    monkeypatch.setattr(server, "wsgi", None)
    yield
    cfg.settings = original_settings


def test_run_initializes_state_and_starts_webapp(monkeypatch):
    pool = Mock()
    webapp_run = Mock()
    monkeypatch.setattr(server.concurrent.futures, "ThreadPoolExecutor", Mock(return_value=pool))
    monkeypatch.setattr(server, "webapp_run", webapp_run)

    server.run()

    assert server.thread_pool is pool
    assert not server.stop_event.is_set()
    webapp_run.assert_called_once_with()


def test_stop_signals_initialized_resources():
    server.stop_event = Mock()
    server.thread_pool = Mock()
    server.wsgi = Mock()

    server.stop()

    server.stop_event.set.assert_called_once_with()
    server.thread_pool.shutdown.assert_called_once_with(wait=False, cancel_futures=True)
    assert server.wsgi.force_exit is True


def test_stop_handles_uninitialized_resources():
    server.stop()


def test_webapp_run_starts_uvicorn_without_mutating_global_logging(tmp_path, monkeypatch):
    cfg.settings.template_dir = tmp_path
    logging_config = {"version": 1, "loggers": {"uvicorn": {}}}
    mount = Mock()
    static_files = object()
    uvicorn_settings = object()
    uvicorn = Mock()
    monkeypatch.setattr(server.uvicorn_config, "LOGGING_CONFIG", logging_config)
    monkeypatch.setattr(server.app, "mount", mount)
    monkeypatch.setattr(server, "StaticFiles", Mock(return_value=static_files))
    monkeypatch.setattr(server, "Config", Mock(return_value=uvicorn_settings))
    monkeypatch.setattr(server, "Server", Mock(return_value=uvicorn))

    server.webapp_run()

    mount.assert_called_once_with("/v1/cluster", static_files, name="cluster")
    server.Config.assert_called_once_with(server.app, host="127.0.0.1", port=5000, log_config={"version": 1})
    uvicorn.run.assert_called_once_with()
    assert logging_config == {"version": 1, "loggers": {"uvicorn": {}}}


def test_webapp_run_logs_startup_error(monkeypatch):
    error = Mock()
    monkeypatch.setattr(server, "StaticFiles", Mock(side_effect=OSError("missing templates")))
    monkeypatch.setattr(server.logging, "error", error)

    server.webapp_run()

    error.assert_called_once_with("Cannot start web server: missing templates")
