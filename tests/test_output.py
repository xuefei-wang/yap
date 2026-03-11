from unittest.mock import patch
from yap.output import type_text, copy_to_clipboard, _escape_applescript


def test_type_text_linux_xdotool():
    with (
        patch("yap.output.platform.system", return_value="Linux"),
        patch("yap.output.shutil.which", return_value="/usr/bin/xdotool"),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        result = type_text("hello")
        mock_run.assert_called_once_with(
            ["xdotool", "type", "--delay", "10", "hello"], check=True
        )
        assert result is True


def test_type_text_macos():
    with (
        patch("yap.output.platform.system", return_value="Darwin"),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        result = type_text("hello")
        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "osascript"
        assert result is True


def test_type_text_wtype():
    with (
        patch("yap.output.platform.system", return_value="Linux"),
        patch(
            "yap.output.shutil.which",
            side_effect=lambda x: "/usr/bin/wtype" if x == "wtype" else None,
        ),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        result = type_text("hello")
        mock_run.assert_called_once_with(["wtype", "hello"], check=True)
        assert result is True


def test_type_text_no_tool():
    with (
        patch("yap.output.platform.system", return_value="Linux"),
        patch("yap.output.shutil.which", return_value=None),
    ):
        result = type_text("hello")
        assert result is False


def test_clipboard_linux():
    with (
        patch("yap.output.platform.system", return_value="Linux"),
        patch("yap.output.shutil.which", return_value=None),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        copy_to_clipboard("hello")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "xclip" in cmd


def test_clipboard_macos():
    with (
        patch("yap.output.platform.system", return_value="Darwin"),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        copy_to_clipboard("hello")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "pbcopy" in cmd


def test_clipboard_linux_wl_copy():
    with (
        patch("yap.output.platform.system", return_value="Linux"),
        patch("yap.output.shutil.which", return_value="/usr/bin/wl-copy"),
        patch("yap.output.subprocess.run") as mock_run,
    ):
        copy_to_clipboard("hello")
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert "wl-copy" in cmd


def test_escape_applescript():
    assert _escape_applescript('he said "hi"') == 'he said \\"hi\\"'
    assert _escape_applescript("back\\slash") == "back\\\\slash"



def test_type_text_windows():
    with (
        patch("yap.output.platform.system", return_value="Windows"),
        patch("yap.output._windows_type") as mock_wintype,
    ):
        result = type_text("hello world")
        mock_wintype.assert_called_once_with("hello world")
        assert result is True


def test_clipboard_windows():
    with (
        patch("yap.output.platform.system", return_value="Windows"),
        patch("yap.output._windows_clipboard") as mock_clip,
    ):
        copy_to_clipboard("hello")
        mock_clip.assert_called_once_with("hello")


