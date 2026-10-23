import sys
from ctypes import wintypes
import ctypes

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget


def enforce_always_on_top(
    window: QWidget,
) -> None:
    """
    Keep the PomoFloat window above normal application windows.

    Qt provides the cross-platform behavior.

    On native Windows, HWND_TOPMOST is also applied through
    the Win32 API to reinforce the topmost state.
    """

    _apply_qt_always_on_top(window)

    if sys.platform == "win32":
        _apply_windows_topmost(window)


def _apply_qt_always_on_top(
    window: QWidget,
) -> None:
    window.setWindowFlag(
        Qt.WindowType.WindowStaysOnTopHint,
        True,
    )


def _apply_windows_topmost(
    window: QWidget,
) -> None:
    hwnd = int(window.winId())

    user32 = ctypes.WinDLL(
        "user32",
        use_last_error=True,
    )

    set_window_pos = user32.SetWindowPos

    set_window_pos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint,
    ]

    set_window_pos.restype = wintypes.BOOL

    HWND_TOPMOST = -1

    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_NOACTIVATE = 0x0010
    SWP_SHOWWINDOW = 0x0040

    flags = (
        SWP_NOSIZE
        | SWP_NOMOVE
        | SWP_NOACTIVATE
        | SWP_SHOWWINDOW
    )

    result = set_window_pos(
        hwnd,
        HWND_TOPMOST,
        0,
        0,
        0,
        0,
        flags,
    )

    if not result:
        error_code = ctypes.get_last_error()

        raise OSError(
            error_code,
            "Could not set PomoFloat as a topmost window.",
        )