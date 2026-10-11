from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from pomofloat.core.app_settings import AppSettings


class SettingsView(QWidget):
    saved = Signal(object)
    cancelled = Signal()
    preview_changed = Signal(object)

    def __init__(
        self,
        settings: AppSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.settings = settings

        self._create_ui()
        self.load_settings(settings)

    def _create_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        main_layout.setSpacing(12)

        title = QLabel("Ajustes")
        title.setObjectName("settingsTitle")

        main_layout.addWidget(title)

        self._create_appearance_section(
            main_layout
        )

        self._create_sound_section(
            main_layout
        )

        self._create_notifications_section(
            main_layout
        )

        self._create_behavior_section(
            main_layout
        )

        main_layout.addStretch()

        self._create_buttons(
            main_layout
        )

    def _create_appearance_section(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        section_title = QLabel("Apariencia")
        section_title.setObjectName(
            "settingsSectionTitle"
        )

        parent_layout.addWidget(
            section_title
        )

        theme_layout = QHBoxLayout()

        theme_label = QLabel("Tema")

        self.theme_selector = QComboBox()
        self.theme_selector.addItem(
            "Sistema",
            "system",
        )
        self.theme_selector.addItem(
            "Oscuro",
            "dark",
        )
        self.theme_selector.addItem(
            "Claro",
            "light",
        )

        self.theme_selector.currentIndexChanged.connect(
            self._emit_preview
        )

        theme_layout.addWidget(
            theme_label
        )

        theme_layout.addStretch()

        theme_layout.addWidget(
            self.theme_selector
        )

        parent_layout.addLayout(
            theme_layout
        )

        opacity_layout = QHBoxLayout()

        opacity_label = QLabel(
            "Opacidad"
        )

        self.opacity_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.opacity_slider.setRange(
            20,
            100,
        )

        self.opacity_slider.setSingleStep(
            1
        )

        self.opacity_value_label = QLabel()

        self.opacity_value_label.setMinimumWidth(
            42
        )

        self.opacity_value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.opacity_slider.valueChanged.connect(
            self._opacity_changed
        )

        opacity_layout.addWidget(
            opacity_label
        )

        opacity_layout.addWidget(
            self.opacity_slider,
            1,
        )

        opacity_layout.addWidget(
            self.opacity_value_label
        )

        parent_layout.addLayout(
            opacity_layout
        )

    def _create_sound_section(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        section_title = QLabel("Sonido")
        section_title.setObjectName(
            "settingsSectionTitle"
        )

        parent_layout.addWidget(
            section_title
        )

        self.sound_checkbox = QCheckBox(
            "Sonido al finalizar fase"
        )

        self.sound_checkbox.toggled.connect(
            self._sound_enabled_changed
        )

        parent_layout.addWidget(
            self.sound_checkbox
        )

        volume_layout = QHBoxLayout()

        volume_label = QLabel(
            "Volumen"
        )

        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        self.volume_slider.setRange(
            0,
            100,
        )

        self.volume_value_label = QLabel()

        self.volume_value_label.setMinimumWidth(
            42
        )

        self.volume_value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        self.volume_slider.valueChanged.connect(
            self._volume_changed
        )

        volume_layout.addWidget(
            volume_label
        )

        volume_layout.addWidget(
            self.volume_slider,
            1,
        )

        volume_layout.addWidget(
            self.volume_value_label
        )

        parent_layout.addLayout(
            volume_layout
        )

    def _create_notifications_section(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        section_title = QLabel(
            "Notificaciones"
        )

        section_title.setObjectName(
            "settingsSectionTitle"
        )

        parent_layout.addWidget(
            section_title
        )

        self.notifications_checkbox = QCheckBox(
            "Mostrar notificación al terminar fase"
        )

        parent_layout.addWidget(
            self.notifications_checkbox
        )

    def _create_behavior_section(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        section_title = QLabel(
            "Comportamiento"
        )

        section_title.setObjectName(
            "settingsSectionTitle"
        )

        parent_layout.addWidget(
            section_title
        )

        self.messages_checkbox = QCheckBox(
            "Mensajes de PomoFloat"
        )

        self.start_with_system_checkbox = (
            QCheckBox(
                "Iniciar con el sistema"
            )
        )

        parent_layout.addWidget(
            self.messages_checkbox
        )

        parent_layout.addWidget(
            self.start_with_system_checkbox
        )

    def _create_buttons(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()

        cancel_button = QPushButton(
            "Cancelar"
        )

        save_button = QPushButton(
            "Guardar"
        )

        cancel_button.clicked.connect(
            self.cancelled.emit
        )

        save_button.clicked.connect(
            self._save
        )

        buttons_layout.addWidget(
            cancel_button
        )

        buttons_layout.addWidget(
            save_button
        )

        parent_layout.addLayout(
            buttons_layout
        )

    def load_settings(
        self,
        settings: AppSettings,
    ) -> None:
        self.settings = settings

        theme_index = (
            self.theme_selector.findData(
                settings.theme
            )
        )

        if theme_index >= 0:
            self.theme_selector.setCurrentIndex(
                theme_index
            )

        self.opacity_slider.setValue(
            settings.window_opacity
        )

        self.sound_checkbox.setChecked(
            settings.sound_enabled
        )

        self.volume_slider.setValue(
            settings.volume
        )

        self.notifications_checkbox.setChecked(
            settings.notifications_enabled
        )

        self.messages_checkbox.setChecked(
            settings.messages_enabled
        )

        self.start_with_system_checkbox.setChecked(
            settings.start_with_system
        )

        self._update_value_labels()
        self._update_sound_controls()

    def build_settings(self) -> AppSettings:
        return AppSettings(
            theme=self.theme_selector.currentData(),
            sound_enabled=self.sound_checkbox.isChecked(),
            volume=self.volume_slider.value(),
            notifications_enabled=(
                self.notifications_checkbox.isChecked()
            ),
            messages_enabled=(
                self.messages_checkbox.isChecked()
            ),
            start_with_system=(
                self.start_with_system_checkbox.isChecked()
            ),
            window_opacity=(
                self.opacity_slider.value()
            ),
        )

    def _save(self) -> None:
        settings = self.build_settings()

        self.settings = settings

        self.saved.emit(
            settings
        )

    def _emit_preview(self) -> None:
        self.preview_changed.emit(
            self.build_settings()
        )

    def _opacity_changed(
        self,
        value: int,
    ) -> None:
        self.opacity_value_label.setText(
            f"{value} %"
        )

        self._emit_preview()

    def _volume_changed(
        self,
        value: int,
    ) -> None:
        self.volume_value_label.setText(
            f"{value} %"
        )

    def _sound_enabled_changed(
        self,
        checked: bool,
    ) -> None:
        self._update_sound_controls()

    def _update_sound_controls(
        self,
    ) -> None:
        self.volume_slider.setEnabled(
            self.sound_checkbox.isChecked()
        )

    def _update_value_labels(
        self,
    ) -> None:
        self.opacity_value_label.setText(
            f"{self.opacity_slider.value()} %"
        )

        self.volume_value_label.setText(
            f"{self.volume_slider.value()} %"
        )