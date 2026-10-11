from dataclasses import dataclass


@dataclass
class AppSettings:
    theme: str = "system"

    sound_enabled: bool = True
    volume: int = 70

    notifications_enabled: bool = True
    messages_enabled: bool = True

    start_with_system: bool = False

    window_opacity: int = 100

    def __post_init__(self) -> None:
        valid_themes = {
            "system",
            "dark",
            "light",
        }

        if self.theme not in valid_themes:
            raise ValueError(
                f"Invalid theme: {self.theme}"
            )

        if not 0 <= self.volume <= 100:
            raise ValueError(
                "Volume must be between 0 and 100."
            )

        if not 20 <= self.window_opacity <= 100:
            raise ValueError(
                "Window opacity must be between 20 and 100."
            )