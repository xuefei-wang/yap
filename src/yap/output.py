"""Text output: type into window or copy to clipboard (Linux / macOS / Windows)."""

import platform
import shutil
import subprocess
import time


def type_text(text):
    """Type text into the active window. Returns True on success, False if no tool found."""
    system = platform.system()
    if system == "Darwin":
        script = f'tell application "System Events" to keystroke "{_escape_applescript(text)}"'
        subprocess.run(["osascript", "-e", script], check=True)
        return True
    elif system == "Windows":
        _windows_type(text)
        return True
    elif shutil.which("xdotool"):
        time.sleep(0.2)
        subprocess.run(["xdotool", "type", "--delay", "10", text], check=True)
        return True
    elif shutil.which("wtype"):
        subprocess.run(["wtype", text], check=True)
        return True
    return False


def _windows_type(text):
    """Type text on Windows via clipboard-paste (supports Unicode)."""
    import pyperclip
    import pyautogui

    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")


def copy_to_clipboard(text):
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["pbcopy"], input=text.encode(), check=True)
    elif system == "Windows":
        _windows_clipboard(text)
    elif shutil.which("wl-copy"):
        subprocess.run(["wl-copy", text], check=True)
    else:
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode(),
            check=True,
        )


def _windows_clipboard(text):
    """Copy to clipboard on Windows."""
    import pyperclip

    pyperclip.copy(text)



def _escape_applescript(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')
