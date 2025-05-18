{
  buildPythonApplication,
  nix-gitignore,
  poetry-core,
  pytestCheckHook,

  click,
  colorama,
  fastapi,
  gevent,
  loguru,
  pydantic-yaml,
  pyyaml,
  shellingham,
  typer,
  urllib3,
  uvicorn,
}:
buildPythonApplication {
  pname = "pixiefairy";
  version = "0.2.5";
  pyproject = true;
  src = nix-gitignore.gitignoreSource [ ] ./.;
  build-system = [ poetry-core ];
  dependencies = [
    click
    colorama
    fastapi
    gevent
    loguru
    pydantic-yaml
    pyyaml
    shellingham
    typer
    urllib3
    uvicorn
  ];

  nativeCheckInputs = [
    pytestCheckHook
  ];
}
