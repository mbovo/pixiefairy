from pathlib import Path

import yaml

from pixiefairy.config import Config


def test_config_yaml_round_trip(tmp_path):
    config = Config()
    config_path = tmp_path / "config.yaml"

    assert config.toFile(str(config_path))

    loaded = Config()
    assert loaded.fromFile(str(config_path))
    assert loaded.settings == config.settings


def test_config_rejects_invalid_yaml_and_can_retry(tmp_path):
    config = Config()
    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text("defaults: [", encoding="utf-8")

    assert not config.fromFile(str(invalid_path))

    valid_path = tmp_path / "valid.yaml"
    assert config.toFile(str(valid_path))
    assert config.fromFile(str(valid_path))


def test_config_to_file_omits_runtime_fields(tmp_path, monkeypatch):
    config = Config()
    config.settings.external_url = "pixiefairy.local"
    config.settings.config_file = Path("config.yaml")
    monkeypatch.setattr("pixiefairy.config.common.get_hostname", lambda: "pixiefairy.local")
    config_path = tmp_path / "config.yaml"

    assert config.toFile(str(config_path))

    document = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    assert "external_url" not in document
    assert "config_file" not in document


def test_config_to_file_handles_missing_filename_and_open_error(tmp_path):
    config = Config()

    assert not config.toFile(None)
    assert not config.toFile(str(tmp_path / "missing" / "config.yaml"))


def test_config_mapping_and_string_representations():
    config = Config()

    assert dict(config) == config.settings.model_dump()
    assert str(config) == str(config.settings)
    assert repr(config) == repr(config.settings)
