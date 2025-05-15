import threading
import concurrent.futures
import logging

from .webapp import app
from .config import cfg

from uvicorn import Server, Config, config as uvicorn_config
from fastapi.staticfiles import StaticFiles

thread_pool: concurrent.futures.ThreadPoolExecutor
wsgi: Server
stop_event: threading.Event


def run():
    global thread_pool, stop_event
    logging.info("Starting threads")

    stop_event = threading.Event()
    thread_pool = concurrent.futures.ThreadPoolExecutor()

    webapp_run()


def stop():
    global thread_pool, stop_event, wsgi
    logging.info("signalling threads to stop")
    stop_event.set()
    thread_pool.shutdown(wait=False, cancel_futures=True)
    wsgi.force_exit = True


def webapp_run():
    """Run WEB Server"""
    global wsgi
    try:
        uvicorn_log_config = uvicorn_config.LOGGING_CONFIG
        del uvicorn_log_config["loggers"]

        wsgi = Server(Config(app, host=cfg.settings.listen_address, port=int(cfg.settings.listen_port), log_config=uvicorn_log_config))
        wsgi.run()
    except Exception as e:
        logging.error(f"Cannot start web server: {e}")
