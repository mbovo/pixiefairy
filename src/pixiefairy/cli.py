import signal
import typer
import logging
import uuid
from pathlib import Path
from typing import Optional
from importlib.metadata import version, PackageNotFoundError

from . import server, common
from .config import cfg

try:
    VERSION = version("pixiefairy")
except PackageNotFoundError:
    VERSION = "unknown"

cli = typer.Typer()


def main():
    common.setup_logging()
    set_sig_handler(sig_handler)
    cli()


@cli.command(help="Print version and exit")
def version():
    typer.echo(f"pixiefairy - Pixiecore API Companion v{VERSION}")


@cli.command(help="Validate the configuration files")
def validate(    config_file: Optional[Path] = typer.Option(
        "config.yaml",
        "-c",
        "--config",
        help="configuration yaml file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        resolve_path=True,
        allow_dash=False,
    )):

    if not cfg.fromFile(config_file):
        logging.error("Validating configuration file failed")
        exit(1)
    logging.info("Configuration file is valid")

@cli.command(help="Start the daemon")
def start(
    config_file: Optional[Path] = typer.Option(
        "config.yaml",
        "-c",
        "--config",
        help="configuration yaml file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        writable=False,
        resolve_path=True,
        allow_dash=False,
    ),
    listen_address: Optional[str] = typer.Option("0.0.0.0", "--listen", "-l", help="Listen address"),
    listen_port: Optional[int] = typer.Option(5000, "-p", "--port", help="Listen port"),
    external_url: Optional[str] = typer.Option(None, "-e", "--external-url", help="URL from external standpoint (like behind a proxy)"),
):

    if not cfg.fromFile(config_file):
        exit(1)

    if not cfg.settings.listen_address:
        cfg.settings.listen_address = listen_address
    if not cfg.settings.listen_port:
        cfg.settings.listen_port = listen_port
    if not cfg.settings.config_file:
        cfg.settings.config_file = config_file
    if not cfg.settings.external_url:
        cfg.settings.external_url = external_url

    if cfg.settings.external_url is None:
        cfg.settings.external_url = f"http://{common.get_hostname()}:{cfg.settings.listen_port}"

    if cfg.settings.api_key is None:
        cfg.settings.api_key = str(uuid.uuid4())
        logging.warning(f"No API_KEY given, new one generated: {cfg.settings.api_key}")
        logging.warning("To avoid this message on start add your `api_key: yourstring` to config.yaml file")

    logging.info(f"Current config: {cfg}")

    server.run()


def sig_handler(signum, stack):
    if signum in [1, 2, 3, 15]:
        logging.warning("Caught signal %s, exiting.", str(signum))
        server.stop()
    return stack


def set_sig_handler(funcname, avoid=["SIG_DFL", "SIGSTOP", "SIGKILL", "SIG_BLOCK"]):
    for i in [x for x in dir(signal) if x.startswith("SIG") and x not in avoid]:
        try:
            signum = getattr(signal, i)
            signal.signal(signum, funcname)
        except (OSError, RuntimeError, ValueError) as m:  # OSError for Python3, RuntimeError for 2
            logging.warning("Skipping {} {}".format(i, m))
