{
  sources ? import ./npins,
  system ? builtins.currentSystem,
  pkgs ? import sources.nixpkgs {
    inherit system;
    config = { };
    overlays = [ ];
  },
}:
rec {
  pixiefairy = pkgs.python3Packages.callPackage ./package.nix { };
  shell = pkgs.mkShellNoCC {
    inputsFrom = [ pixiefairy ];
    packages = with pkgs; [
      (pkgs.poetry.override { python3 = pkgs.python3; })
      pkgs.python3Packages.setuptools
      npins
    ];
  };
}
