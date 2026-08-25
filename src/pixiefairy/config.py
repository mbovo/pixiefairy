import logging
import threading
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, FilePath
from pydantic_yaml import parse_yaml_file_as, to_yaml_str

from . import common

# Models


class BootSection(BaseModel):
    kernel: str
    initrd: List[str]
    message: Optional[str] = None
    cmdline: Optional[str] = None


class NetworkSection(BaseModel):
    dhcp: bool
    server: Optional[str] = None
    gateway: Optional[str] = None
    netmask: Optional[str] = None
    dns: Optional[str] = None
    ntp: Optional[str] = None
    ip: Optional[str] = None
    hostname: Optional[str] = None
    device: Optional[str] = None


class Defaults(BaseModel):
    boot: BootSection
    net: NetworkSection
    deny_unknown_clients: bool
    role: str


class MacEntry(BaseModel):
    boot: Optional[BootSection] = None
    net: Optional[NetworkSection] = None
    role: Optional[str] = None


class Settings(BaseModel):
    api_key: Optional[str] = None
    listen_address: Optional[str] = None
    listen_port: Optional[int] = None
    external_url: Optional[str] = None
    config_file: Optional[FilePath] = None
    template_dir: Optional[FilePath] = None
    defaults: Defaults
    mapping: Dict[str, MacEntry] = Field(default_factory=dict)


class BootResponse(BaseModel):
    kernel: str
    initrd: List[str]
    message: Optional[str] = None
    cmdline: Optional[str] = None


# Global config, wraps Settings model


class Config(object):
    settings: Settings
    cache: dict
    __lock: threading.Lock

    def __init__(self) -> None:
        self.settings: Settings = Settings(
            defaults=Defaults(boot=BootSection(kernel="", initrd=[""]), net=NetworkSection(dhcp=True), deny_unknown_clients=False, role="worker"), mapping={}
        )
        self.cache = {}
        self.__lock = threading.Lock()

    def fromFile(self, filename: str) -> bool:
        try:
            with self.__lock:
                self.settings = parse_yaml_file_as(Settings, filename)
        except Exception as e:
            logging.error(f"exception {e}")
            return False
        return True

    def toFile(self, filename: str) -> bool:
        if filename is None:
            return False
        try:
            with self.__lock, open(filename, "w") as c:
                settings: Settings = self.settings.model_copy()
                settings.config_file = None
                if settings.external_url == common.get_hostname():
                    settings.external_url = None
                c.write(to_yaml_str(settings, exclude_none=True, exclude_unset=True))
        except Exception as e:
            logging.error(f"error {e}")
            return False
        return True

    def __iter__(self):
        yield from self.settings.model_dump().items()

    def __str__(self) -> str:
        return self.settings.__str__()

    def __repr__(self) -> str:
        return self.settings.__repr__()


cfg = Config()
