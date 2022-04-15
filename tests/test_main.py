from pixiefairy.cli import cli
from typer.testing import CliRunner
import pkg_resources
from pytest import fixture


def test_assert_true():
    assert True


@fixture
def runner():
    return CliRunner()


def test_main_cli(runner):
    assert runner.invoke(cli, "").exit_code == 2


def test_main_version(runner):
    result = runner.invoke(cli, "version")
    assert result.exit_code == 0
    assert result.stdout == f"pixiefairy - Pixiecore API Companion v{pkg_resources.get_distribution('pixiefairy').version}\n"


def test_main_start(runner):
    result = runner.invoke(cli, "start")
    assert result.exit_code == 2


# # need to mock server.run()
# def test_main_start_ok(runner):
#     result = runner.invoke(cli, ["start","-c","./examples/config.yaml"])
#     assert result.exit_code == 0
