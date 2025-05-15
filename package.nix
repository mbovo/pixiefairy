{
  buildPythonApplication,
  nix-gitignore,
  lib,
  poetry-core,

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
  version = "0.2.4";
  pyproject = true;
  src = nix-gitignore.gitignoreSource [ ] ./.;
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
  ];
}
