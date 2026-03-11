from unittest.mock import patch, MagicMock
from yap.cli import build_parser, main


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.clipboard is False
    assert args.llm is False
    assert args.model is None
    assert args.lang is None


def test_parser_all_flags():
    parser = build_parser()
    args = parser.parse_args(
        ["--clipboard", "--llm", "--model", "tiny.en", "--lang", "zh"]
    )
    assert args.clipboard is True
    assert args.llm is True
    assert args.model == "tiny.en"
    assert args.lang == "zh"


def test_parser_config_subcommand():
    parser = build_parser()
    args = parser.parse_args(["config"])
    assert args.command == "config"


def test_main_interactive_no_speech():
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.start_recording", return_value=MagicMock()),
        patch("yap.cli.stop_recording"),
        patch("yap.cli.transcribe", return_value=""),
        patch("yap.cli.cleanup_audio"),
        patch("builtins.input"),
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            clipboard=False,
            llm=False,
            model=None,
            lang=None,
            command=None,
            serve=False,
            port=8765,
        )
        assert main() == 1


def test_main_interactive_with_text():
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.start_recording", return_value=MagicMock()),
        patch("yap.cli.stop_recording"),
        patch("yap.cli.transcribe", return_value="hello world"),
        patch("yap.cli.cleanup_audio"),
        patch("yap.cli.type_text", return_value=True),
        patch("builtins.input"),
        patch("builtins.print"),
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            clipboard=False,
            llm=False,
            model=None,
            lang=None,
            command=None,
            serve=False,
            port=8765,
        )
        assert main() == 0


def test_main_type_text_fallback():
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.start_recording", return_value=MagicMock()),
        patch("yap.cli.stop_recording"),
        patch("yap.cli.transcribe", return_value="hello"),
        patch("yap.cli.cleanup_audio"),
        patch("yap.cli.type_text", return_value=False),
        patch("yap.cli.copy_to_clipboard"),
        patch("builtins.input"),
        patch("builtins.print") as mock_print,
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            clipboard=False,
            llm=False,
            model=None,
            lang=None,
            command=None,
            serve=False,
            port=8765,
        )
        result = main()
        assert result == 0
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("clipboard" in c.lower() for c in calls)


def test_main_llm_no_config():
    """--llm without config should print setup message and skip correction."""
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.start_recording", return_value=MagicMock()),
        patch("yap.cli.stop_recording"),
        patch("yap.cli.transcribe", return_value="hello world"),
        patch("yap.cli.cleanup_audio"),
        patch("yap.cli.type_text", return_value=True),
        patch("yap.cli.load_config", return_value={}),
        patch("builtins.input"),
        patch("builtins.print") as mock_print,
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            clipboard=False,
            llm=True,
            model=None,
            lang=None,
            command=None,
            serve=False,
            port=8765,
        )
        result = main()
        assert result == 0
        calls = [str(c) for c in mock_print.call_args_list]
        assert any("yap config" in c for c in calls)


def test_main_llm_with_config():
    """--llm with config should call llm_correct with the saved provider."""
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.start_recording", return_value=MagicMock()),
        patch("yap.cli.stop_recording"),
        patch("yap.cli.transcribe", return_value="hello wrold"),
        patch("yap.cli.cleanup_audio"),
        patch("yap.cli.type_text", return_value=True),
        patch("yap.cli.load_config", return_value={"llm_provider": "openai"}),
        patch("yap.cli.llm_correct", return_value="hello world") as mock_llm,
        patch("builtins.input"),
        patch("builtins.print"),
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            clipboard=False,
            llm=True,
            model=None,
            lang=None,
            command=None,
            serve=False,
            port=8765,
        )
        main()
        mock_llm.assert_called_once_with("hello wrold", "openai", model=None)


def test_config_subcommand():
    """yap config should run the wizard."""
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.cli.run_config_wizard") as mock_wizard,
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            command="config",
            serve=False,
            port=8765,
        )
        result = main()
        mock_wizard.assert_called_once()
        assert result == 0


def test_parser_serve_flag():
    parser = build_parser()
    args = parser.parse_args(["--serve"])
    assert args.serve is True
    assert args.port == 8765


def test_parser_serve_with_port():
    parser = build_parser()
    args = parser.parse_args(["--serve", "--port", "9000"])
    assert args.serve is True
    assert args.port == 9000


def test_main_serve_mode():
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.server.run_server") as mock_serve,
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            serve=True,
            port=8765,
            command=None,
            clipboard=False,
            llm=False,
            model=None,
            lang=None,
        )
        result = main()
        mock_serve.assert_called_once_with(host="localhost", port=8765)
        assert result == 0


def test_main_serve_warns_on_extra_flags(capsys):
    with (
        patch("yap.cli.build_parser") as mock_bp,
        patch("yap.server.run_server"),
    ):
        mock_bp.return_value.parse_args.return_value = MagicMock(
            serve=True,
            port=8765,
            command=None,
            clipboard=True,
            llm=True,
            model=None,
            lang=None,
        )
        main()
        captured = capsys.readouterr()
        assert "ignored" in captured.out.lower() or "warning" in captured.out.lower()
