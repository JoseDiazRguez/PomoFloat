import pytest

from pomofloat.core.app_settings import AppSettings


def test_default_settings() -> None:
    settings = AppSettings()

    assert settings.theme == "system"
    assert settings.sound_enabled is True
    assert settings.volume == 70
    assert settings.notifications_enabled is True
    assert settings.messages_enabled is True
    assert settings.start_with_system is False
    assert settings.window_opacity == 100


def test_custom_settings() -> None:
    settings = AppSettings(
        theme="dark",
        sound_enabled=False,
        volume=35,
        notifications_enabled=False,
        messages_enabled=False,
        start_with_system=True,
        window_opacity=80,
    )

    assert settings.theme == "dark"
    assert settings.sound_enabled is False
    assert settings.volume == 35
    assert settings.notifications_enabled is False
    assert settings.messages_enabled is False
    assert settings.start_with_system is True
    assert settings.window_opacity == 80

@pytest.mark.parametrize(
    "volume",
    [
        -1,
        101,
    ],
)
def test_invalid_volume(
    volume: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="Volume must be between",
    ):
        AppSettings(
            volume=volume
        )

@pytest.mark.parametrize(
    "opacity",
    [
        19,
        101,
    ],
)
def test_invalid_window_opacity(
    opacity: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="Window opacity must be between",
    ):
        AppSettings(
            window_opacity=opacity
        )

def test_invalid_theme() -> None:
    with pytest.raises(
        ValueError,
        match="Invalid theme",
    ):
        AppSettings(
            theme="purple"
        )