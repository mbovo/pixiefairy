{
  buildPythonApplication,
  lib,
  poetry-core,
  setuptools, # A runtime dependency (resolves package version)

  pyyaml,
  click,
  colorama,
  fastapi,
  gevent,
  loguru,
  pydantic-yaml,
  shellingham,
  typer,
  urllib3,
  uvicorn,
}:
buildPythonApplication {
  pname = "pixiefairy";
  version = "0.2.0";
  pyproject = true;
  src = lib.cleanSource ./.;
  build-system = [ poetry-core ];
  dependencies = [
    pyyaml
    click
    colorama
    fastapi
    gevent
    loguru
    pydantic-yaml
    shellingham
    typer
    urllib3
    uvicorn

    setuptools # pkg_resources
  ];
}
