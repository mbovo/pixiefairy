import logging
import threading
from pydantic import BaseModel, FilePath
from typing import List, Dict, Optional
from pydantic_yaml import parse_yaml_raw_as, to_yaml_str
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
    mapping: Optional[Dict[str, MacEntry]] = None


class BootResponse(BaseModel):
    kernel: str
    initrd: List[str]
    message: Optional[str] = None
    cmdline: Optional[str] = None


# Global config, wraps Settings model

class Config:
    settings: Settings
    cache: Dict
    __lock: threading.Lock

    def __init__(self) -> None:
        # Initialize with default empty settings
        self.settings = Settings(
            defaults=Defaults(
                boot=BootSection(kernel="", initrd=[""]),
                net=NetworkSection(dhcp=True),
                deny_unknown_clients=False,
                role="worker"
            ),
            mapping={}
        )
        self.cache = {}
        self.__lock = threading.Lock()

    def fromFile(self, filename: str) -> bool:
        try:
            self.__lock.acquire()
            with open(filename, 'r') as f:
                raw = f.read()
            self.settings = parse_yaml_raw_as(Settings, raw)
        except Exception as e:
            logging.error(f"Exception reading config file: {e}")
            return False
        finally:
            self.__lock.release()
        return True

    def toFile(self, filename: str) -> bool:
        if not filename:
            return False
        try:
            with open(filename, "w") as c:
                self.__lock.acquire()
                settings = self.settings.copy()
                settings.config_file = None
                if settings.external_url == common.get_hostname():
                    settings.external_url = None
                yaml_str = to_yaml_str(settings, exclude_none=True, exclude_unset=True)
                c.write(yaml_str)
        except Exception as e:
            logging.error(f"Error writing config file: {e}")
            return False
        finally:
            self.__lock.release()
        return True

    def __iter__(self):
        yield from self.settings.dict().items()

    def __str__(self) -> str:
        return str(self.settings)

    def __repr__(self) -> str:
        return repr(self.settings)

# Singleton instance
cfg = Config()
