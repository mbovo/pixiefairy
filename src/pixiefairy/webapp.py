import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from .config import cfg, MacEntry, Defaults, Settings, BootResponse
from .logic import parse_mac

app = FastAPI()
app.title = "pixiefairy"
app.description = "Pixiecore API Companion"
logger = logging.getLogger("webapp")


@app.get("/")
def root():
    return {"health": "ok"}


@app.get("/health")
def health():
    return {"status": "OK"}


@app.get("/v1/boot/{macaddress}", response_model=BootResponse, response_model_exclude_unset=True, response_model_exclude_none=True)
def bootstrap(macaddress: str):
    try:
        return parse_mac(macaddress)
    except Exception as e:
        logging.warn(e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/config", response_model=Settings, response_model_exclude_unset=True, response_model_exclude_none=True)
def get_config(apikey: str):
    if apikey != cfg.settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return cfg.settings


@app.get("/config/defaults", response_model=Defaults, response_model_exclude_unset=True, response_model_exclude_none=True)
def get_defaults():
    return cfg.settings.defaults


@app.get("/config/mapping", response_model=Optional[Dict[str, MacEntry]], response_model_exclude_unset=True, response_model_exclude_none=True)
def get_mapping():
    return cfg.settings.mapping


@app.post("/config/mapping/{macaddress}", response_model=MacEntry, response_model_exclude_unset=True, response_model_exclude_none=True)
def set_mapping(macaddress: str, apikey: str, mapping: MacEntry):
    if apikey != cfg.settings.api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cfg.settings.mapping[macaddress] = mapping
    cfg.toFile(cfg.settings.config_file)
    return cfg.settings.mapping[macaddress]
