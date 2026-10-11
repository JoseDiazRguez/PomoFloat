from PySide6.QtCore import QSettings

from pomofloat.core.app_settings import AppSettings


class SettingsStorage:
    def __init__(
        self,
        settings: QSettings | None = None,
    ) -> None:
        self.settings = (
            settings
            if settings is not None
            else QSettings(
                "PomoFloat",
                "PomoFloat",
            )
        )

    def load(self) -> AppSettings:
        return AppSettings(
            theme=self.settings.value(
                "app/theme",
                "system",
                type=str,
            ),
            sound_enabled=self.settings.value(
                "sound/enabled",
                True,
                type=bool,
            ),
            volume=self.settings.value(
                "sound/volume",
                70,
                type=int,
            ),
            notifications_enabled=(
                self.settings.value(
                    "notifications/enabled",
                    True,
                    type=bool,
                )
            ),
            messages_enabled=self.settings.value(
                "messages/enabled",
                True,
                type=bool,
            ),
            start_with_system=self.settings.value(
                "system/start_with_system",
                False,
                type=bool,
            ),

            window_opacity=self.settings.value(
                "window/opacity",
                100,
                type=int,
            ),
        )

    def save(
        self,
        app_settings: AppSettings,
    ) -> None:
        self.settings.setValue(
            "app/theme",
            app_settings.theme,
        )

        self.settings.setValue(
            "sound/enabled",
            app_settings.sound_enabled,
        )

        self.settings.setValue(
            "sound/volume",
            app_settings.volume,
        )

        self.settings.setValue(
            "notifications/enabled",
            app_settings.notifications_enabled,
        )

        self.settings.setValue(
            "messages/enabled",
            app_settings.messages_enabled,
        )

        self.settings.setValue(
            "system/start_with_system",
            app_settings.start_with_system,
        )

        self.settings.setValue(
            "window/opacity",
            app_settings.window_opacity,
        )

        self.settings.sync()