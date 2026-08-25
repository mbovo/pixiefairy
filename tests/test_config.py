from pixiefairy.config import Config


def test_config_yaml_round_trip(tmp_path):
    config = Config()
    config_path = tmp_path / "config.yaml"

    assert config.toFile(str(config_path))

    loaded = Config()
    assert loaded.fromFile(str(config_path))
    assert loaded.settings == config.settings
