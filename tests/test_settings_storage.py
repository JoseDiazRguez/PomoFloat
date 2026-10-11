from pathlib import Path

from PySide6.QtCore import QSettings

from pomofloat.core.app_settings import AppSettings
from pomofloat.services.settings_storage import (
    SettingsStorage,
)


def create_test_storage(
    tmp_path: Path,
) -> SettingsStorage:
    settings = QSettings(
        str(tmp_path / "settings.ini"),
        QSettings.Format.IniFormat,
    )

    return SettingsStorage(
        settings
    )


def test_load_default_settings(
    tmp_path: Path,
) -> None:
    storage = create_test_storage(
        tmp_path
    )

    settings = storage.load()

    assert settings == AppSettings()


def test_save_and_load_settings(
    tmp_path: Path,
) -> None:
    storage = create_test_storage(
        tmp_path
    )

    original = AppSettings(
        theme="dark",
        sound_enabled=False,
        volume=42,
        notifications_enabled=False,
        messages_enabled=True,
        start_with_system=True,
        window_opacity=75,
    )

    storage.save(
        original
    )

    loaded = storage.load()

    assert loaded == original