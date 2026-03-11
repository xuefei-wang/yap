import os
from unittest.mock import patch
from yap.config import load_config, save_config, run_config_wizard, PROVIDER_MODELS


def test_load_config_missing(tmp_path):
    path = str(tmp_path / "config.json")
    with patch("yap.config.CONFIG_PATH", path):
        assert load_config() == {}


def test_save_and_load_config(tmp_path):
    path = str(tmp_path / "config.json")
    with patch("yap.config.CONFIG_PATH", path):
        save_config({"llm_provider": "openai"})
        assert load_config() == {"llm_provider": "openai"}


def test_save_config_creates_dir(tmp_path):
    path = str(tmp_path / "subdir" / "config.json")
    with patch("yap.config.CONFIG_PATH", path):
        save_config({"llm_provider": "gemini"})
        assert os.path.exists(path)


def test_wizard_claude_code(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("yap.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["1", ""]),
        patch("yap.config.shutil.which", return_value="/usr/bin/claude"),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["llm_provider"] == "claude-code"
        assert cfg["llm_model"] == "haiku"


def test_wizard_claude_code_pick_model(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("yap.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["1", "2"]),
        patch("yap.config.shutil.which", return_value="/usr/bin/claude"),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["llm_provider"] == "claude-code"
        assert cfg["llm_model"] == "sonnet"


def test_wizard_openai_with_key(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("yap.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["3", ""]),
        patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["llm_provider"] == "openai"
        assert cfg["llm_model"] == "gpt-4o-mini"


def test_wizard_openai_without_key(tmp_path, capsys):
    path = str(tmp_path / "config.json")
    with (
        patch("yap.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["3", ""]),
        patch.dict(os.environ, {}, clear=True),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["llm_provider"] == "openai"
        assert cfg["llm_model"] == "gpt-4o-mini"
        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out


def test_wizard_invalid_then_valid(tmp_path):
    path = str(tmp_path / "config.json")
    with (
        patch("yap.config.CONFIG_PATH", path),
        patch("builtins.input", side_effect=["9", "abc", "2", ""]),
        patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk"}, clear=True),
    ):
        run_config_wizard()
        cfg = load_config()
        assert cfg["llm_provider"] == "claude"
        assert cfg["llm_model"] == "claude-haiku-4-5-20251001"


def test_get_config_dir_windows():
    with (
        patch("yap.config.platform.system", return_value="Windows"),
        patch.dict(os.environ, {"APPDATA": "/fake/appdata"}),
    ):
        from yap.config import _get_config_dir

        assert _get_config_dir() == os.path.join("/fake/appdata", "yap")


def test_get_config_dir_unix():
    with (
        patch("yap.config.platform.system", return_value="Linux"),
        patch.dict(os.environ, {"XDG_CONFIG_HOME": "/fake/config"}, clear=False),
    ):
        from yap.config import _get_config_dir

        assert _get_config_dir() == os.path.join("/fake/config", "yap")
