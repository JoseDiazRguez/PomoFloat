from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
    QApplication,
    # QComboBox,
    QMessageBox,
    QScrollArea,
)

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from pomofloat.core.timer import TimerEngine, TimerState
from pomofloat.ui.cycle_editor import CycleEditor
from pomofloat.services.cycle_storage import (
    CycleStorage,
)


class DraggableFrame(QFrame):
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            window_handle = window.windowHandle()

            if window_handle is not None:
                window_handle.startSystemMove()
                event.accept()
                return

        super().mousePressEvent(event)

class ResizeHandle(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setFixedSize(18, 18)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.preset_panel_previous_height: int | None = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            window_handle = window.windowHandle()

            if window_handle is not None:
                edges = (
                    Qt.Edge.RightEdge
                    | Qt.Edge.BottomEdge
                )

                window_handle.startSystemResize(edges)

                event.accept()
                return

        super().mousePressEvent(event)

class MainWindow(QWidget):
    NORMAL_SIZE = (360, 220)
    COMPACT_SIZE = (440, 64)

    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings("PomoFloat", "PomoFloat")

        self.compact_mode = False

        self.cycle_storage = CycleStorage()

        self.presets, active_preset_name = (
            self.cycle_storage.load_presets()
        )

        default_cycle = Cycle(
            name="Pomodoro clásico",
            phases=[
                Phase(
                    "Concentración",
                    25 * 60,
                ),
                Phase(
                    "Descanso",
                    5 * 60,
                ),
            ],
            repetitions=None,
        )

        if not self.presets:
            self.presets = [
                default_cycle
            ]

            self.active_preset_name = (
                default_cycle.name
            )

            self.cycle_storage.save_presets(
                self.presets,
                self.active_preset_name,
            )

        else:
            self.active_preset_name = (
                active_preset_name
            )

        active_cycle = next(
            (
                cycle
                for cycle in self.presets
                if cycle.name
                == self.active_preset_name
            ),
            self.presets[0],
        )

        self.active_preset_name = (
            active_cycle.name
        )

        self.engine = TimerEngine(
            active_cycle
        )

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._configure_window()
        self._create_ui()
        self._refresh_preset_selector()
        self._update_ui()
        self._restore_window_state()

    def _configure_window(self) -> None:
        self.setWindowTitle("PomoFloat")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setMinimumSize(300, 150)
        self.resize(*self.NORMAL_SIZE)

    def _create_ui(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(14, 10, 10, 8)
        self.main_layout.setSpacing(8)

        self._create_normal_view()
        self._create_compact_view()
        self._create_cycle_editor_view()

        self._apply_styles()

    def _create_cycle_editor_view(self) -> None:
        self.cycle_editor = CycleEditor(
            self.engine.cycle,
            self.presets,
            self,
        )

        self.cycle_editor.saved.connect(
            self._save_cycle_configuration
        )

        self.cycle_editor.cancelled.connect(
            self._close_cycle_editor
        )

        self.cycle_editor.delete_requested.connect(
            self._delete_preset
        )

        self.cycle_editor.hide()

        self.main_layout.addWidget(
            self.cycle_editor
        )

    def _create_normal_view(self) -> None:
        self.normal_view = QWidget()

        self.normal_layout = QVBoxLayout(self.normal_view)
        self.normal_layout.setContentsMargins(0, 0, 0, 0)
        self.normal_layout.setSpacing(8)

        original_layout = self.main_layout
        self.main_layout = self.normal_layout

        self._create_header()
        self._create_preset_panel()
        self._create_timer_area()
        self._create_controls()
        self._create_resize_area()

        self.main_layout = original_layout

        self.main_layout.addWidget(self.normal_view)

    def _create_header(self) -> None:
        self.header = DraggableFrame()

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        # self.phase_indicator = QLabel("●")

        self.phase_label = QLabel()
        self.phase_label.setObjectName("phaseLabel")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.preset_button = QPushButton()

        self.preset_button.setObjectName(
            "presetButton"
        )

        self.preset_button.setToolTip(
            "Seleccionar ciclo"
        )

        self.preset_button.clicked.connect(
            self._toggle_preset_panel
        )

        self.repetition_label = QLabel()
        self.repetition_label.setObjectName("secondaryLabel")

        # header_layout.addWidget(
        #    self.phase_indicator
        # )

        header_layout.addWidget(
            self.preset_button
        )

        header_layout.addStretch()

        header_layout.addWidget(self.repetition_label)

        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName(
            "windowButton"
        )
        self.settings_button.setToolTip(
            "Configurar ciclo"
        )
        self.settings_button.clicked.connect(
            self._open_cycle_editor
        )

        self.compact_button = QPushButton("▭")
        self.compact_button.setObjectName("windowButton")
        self.compact_button.setToolTip("Cambiar modo compacto")
        self.compact_button.clicked.connect(
            self._toggle_compact_mode
        )

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setToolTip("Cerrar PomoFloat")
        self.close_button.clicked.connect(self.close)

        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.compact_button)
        header_layout.addWidget(self.close_button)

        self.main_layout.addWidget(self.header)

    def _refresh_preset_selector(self) -> None:
        self.preset_button.setText(
            f"{self.active_preset_name} ▾"
        )

        while (
            self.preset_panel_layout.count()
            > 0
        ):
            item = (
                self.preset_panel_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        for preset in self.presets:
            button = QPushButton()

            if (
                preset.name
                == self.active_preset_name
            ):
                button.setText(
                    f"✓  {preset.name}"
                )
            else:
                button.setText(
                    f"   {preset.name}"
                )

            button.setObjectName(
                "presetItemButton"
            )

            button.setFixedHeight(
                32
            )

            button.clicked.connect(
                lambda checked=False,
                name=preset.name:
                self._select_preset(name)
            )

            self.preset_panel_layout.addWidget(
                button
            )

        self.preset_panel_layout.addStretch()

        self._update_preset_panel_height()

    def _change_preset(
        self,
        preset_name: str,
    ) -> None:
        if not preset_name:
            return

        cycle = next(
            (
                preset
                for preset in self.presets
                if preset.name == preset_name
            ),
            None,
        )

        if cycle is None:
            return

        self.active_preset_name = cycle.name

        self.cycle_storage.save_presets(
            self.presets,
            self.active_preset_name,
        )

        self._apply_cycle(cycle)

    def _create_timer_area(self) -> None:
        self.timer_container = QWidget()

        timer_layout = QVBoxLayout(self.timer_container)
        timer_layout.setContentsMargins(8, 4, 8, 4)
        timer_layout.setSpacing(8)

        self.time_label = QLabel()
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(6)

        self.state_label = QLabel()
        self.state_label.setObjectName("secondaryLabel")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        timer_layout.addStretch()
        timer_layout.addWidget(self.phase_label)
        timer_layout.addWidget(self.time_label)
        timer_layout.addWidget(self.progress_bar)
        timer_layout.addWidget(self.state_label)
        timer_layout.addStretch()

        self.main_layout.addWidget(self.timer_container)

    def _create_controls(self) -> None:
        self.controls_container = QWidget()

        controls_layout = QHBoxLayout(self.controls_container)
        controls_layout.setContentsMargins(20, 0, 20, 0)
        controls_layout.setSpacing(8)

        controls_layout.addStretch()

        self.start_pause_button = QPushButton("▶")
        self.start_pause_button.setToolTip("Iniciar")
        self.start_pause_button.clicked.connect(self._toggle_start_pause)

        self.reset_button = QPushButton("↻")
        self.reset_button.setToolTip("Reiniciar")
        self.reset_button.clicked.connect(self._reset)

        self.skip_button = QPushButton("»")
        self.skip_button.setToolTip("Saltar fase")
        self.skip_button.clicked.connect(self._skip)

        controls_layout.addWidget(self.start_pause_button)
        controls_layout.addWidget(self.reset_button)
        controls_layout.addWidget(self.skip_button)

        controls_layout.addStretch()

        self.main_layout.addWidget(self.controls_container)

    def _create_resize_area(self) -> None:
        resize_layout = QHBoxLayout()
        resize_layout.setContentsMargins(0, 0, 0, 0)

        resize_layout.addStretch()

        self.size_grip = ResizeHandle(self)
        self.size_grip.setToolTip("Redimensionar")

        resize_layout.addWidget(self.size_grip)

        self.main_layout.addLayout(resize_layout)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background-color: #202124;
                color: #f1f3f4;
                font-family: Arial;
            }

            #phaseLabel {
                font-size: 12px;
                font-weight: 700;
                color: #bdc1c6;
            }

            #timeLabel {
                font-size: 38px;
                font-weight: 700;
            }

            #secondaryLabel {
                color: #9aa0a6;
                font-size: 11px;
            }

            QPushButton {
                background-color: #303134;
                border: 1px solid #5f6368;
                border-radius: 8px;
                min-width: 38px;
                min-height: 30px;
                font-size: 16px;
            }

            QPushButton:hover {
                background-color: #3c4043;
            }

            QPushButton:pressed {
                background-color: #4a4d51;
            }

            #windowButton,
            #closeButton {
                background: transparent;
                border: none;
                min-width: 24px;
                min-height: 24px;
                font-size: 16px;
            }

            #windowButton:hover {
                background-color: #303134;
            }

            #closeButton:hover {
                background-color: #5f2120;
            }

            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #303134;
            }

            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #8ab4f8;
            }

            #compactPhaseLabel {
                font-size: 11px;
                font-weight: 600;
            }

            #compactTimeLabel {
                font-size: 16px;
                font-weight: 700;
            }

            #compactButton {
                background: transparent;
                border: none;
                min-width: 26px;
                min-height: 26px;
                font-size: 15px;
            }

            #compactButton:hover {
                background-color: #303134;
            }

            #presetButton {
                background-color: #303134;
                border: 1px solid #5f6368;
                border-radius: 4px;
                padding: 3px 8px;
                font-size: 11px;
                min-height: 20px;
            }

            #presetButton:hover {
                background-color: #3c4043;
            }

            #presetPanel {
                background-color: #292a2d;
                border: 1px solid #5f6368;
                border-radius: 8px;
            }

            #presetItemButton {
                background: transparent;
                border: none;
                border-radius: 4px;
                text-align: left;
                padding-left: 10px;
                padding-right: 10px;
                font-size: 12px;
            }

            #presetItemButton:hover {
                background-color: #3c4043;
            }

            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }

            QScrollArea QWidget {
                background: transparent;
                border: none;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 4px 2px 4px 2px;
            }

            QScrollBar::handle:vertical {
                background-color: #5f6368;
                border-radius: 4px;
                min-height: 24px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    def _toggle_start_pause(self) -> None:
        if self.engine.state == TimerState.IDLE:
            self.engine.start()
            self.timer.start()

        elif self.engine.state == TimerState.RUNNING:
            self.engine.pause()
            self.timer.stop()

        elif self.engine.state == TimerState.PAUSED:
            self.engine.resume()
            self.timer.start()

        elif self.engine.state == TimerState.WAITING:
            self.engine.continue_from_waiting()
            self.timer.start()

        self._update_ui()

    def _reset(self) -> None:
        self.timer.stop()
        self.engine.reset()
        self._update_ui()

    def _skip(self) -> None:
        self.engine.skip()

        if self.engine.state == TimerState.FINISHED:
            self.timer.stop()

        self._update_ui()

    def _on_tick(self) -> None:
        self.engine.tick()

        if self.engine.state in (
            TimerState.PAUSED,
            TimerState.WAITING,
            TimerState.FINISHED,
        ):
            self.timer.stop()

        self._update_ui()

    def _toggle_compact_mode(self) -> None:
        self._close_preset_panel()

        if not self.compact_mode:
            self.settings.setValue(
                "window/normal_size",
                self.size(),
            )

        self.compact_mode = not self.compact_mode

        if self.compact_mode:
            self.normal_view.hide()
            self.compact_view.show()

            self.setMinimumSize(420, 58)
            self.setMaximumHeight(64)
            self.resize(*self.COMPACT_SIZE)

        else:
            self.compact_view.hide()
            self.normal_view.show()

            self.setMaximumHeight(16777215)
            self.setMinimumSize(300, 150)

            normal_size = self.settings.value(
                "window/normal_size"
            )

            if normal_size is not None:
                self.resize(normal_size)
            else:
                self.resize(*self.NORMAL_SIZE)

        self._update_ui()

    def _update_ui(self) -> None:
        phase = self.engine.current_phase

        self.phase_label.setText(phase.name.upper())

        total_seconds = self.engine.remaining_seconds

        hours, remainder = divmod(
            total_seconds,
            3600,
        )

        minutes, seconds = divmod(
            remainder,
            60,
        )

        formatted_time = (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

        self.time_label.setText(formatted_time)

        if self.engine.cycle.is_infinite:
            repetition_text = f"{self.engine.current_repetition} / ∞"
        else:
            repetition_text = (
                f"{self.engine.current_repetition} / "
                f"{self.engine.cycle.repetitions}"
            )

        self.repetition_label.setText(repetition_text)

        self.compact_phase_label.setText(
            self._elide_text(
                self.compact_phase_label,
                phase.name,
                130,
            )
        )
        self.compact_time_label.setText(formatted_time)
        self.compact_repetition_label.setText(repetition_text)

        self.state_label.setText(
            self._state_text()
        )

        phase_duration = phase.duration_seconds

        elapsed_seconds = (
            phase_duration
            - self.engine.remaining_seconds
        )

        progress = int(
            elapsed_seconds
            / phase_duration
            * 100
        )

        self.progress_bar.setValue(progress)

        self._update_start_button()

        

    def _update_start_button(self) -> None:
        state = self.engine.state

        if state == TimerState.IDLE:
            symbol = "▶"
            tooltip = "Iniciar"

        elif state == TimerState.RUNNING:
            symbol = "Ⅱ"
            tooltip = "Pausar"

        elif state in (
            TimerState.PAUSED,
            TimerState.WAITING,
        ):
            symbol = "▶"
            tooltip = "Continuar"

        else:
            symbol = "✓"
            tooltip = "Finalizado"

        self.start_pause_button.setText(symbol)
        self.start_pause_button.setToolTip(tooltip)

        self.compact_start_button.setText(symbol)
        self.compact_start_button.setToolTip(tooltip)

    def _state_text(self) -> str:
        state_texts = {
            TimerState.IDLE: "Preparado",
            TimerState.RUNNING: "En marcha",
            TimerState.PAUSED: "Pausado",
            TimerState.WAITING: "Esperando continuación",
            TimerState.FINISHED: "Finalizado",
        }

        return state_texts[self.engine.state]

    def _create_compact_view(self) -> None:
        self.compact_view = DraggableFrame()

        layout = QHBoxLayout(self.compact_view)
        layout.setContentsMargins(10, 5, 6, 5)
        layout.setSpacing(8)

        # self.compact_indicator = QLabel("●")

        self.compact_phase_label = QLabel()
        self.compact_phase_label.setMinimumWidth(
            100
        )

        self.compact_phase_label.setMaximumWidth(
            130
        )
        self.compact_phase_label.setObjectName("compactPhaseLabel")

        self.compact_time_label = QLabel()
        self.compact_time_label.setMinimumWidth(
            90
        )

        self.compact_time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.compact_time_label.setObjectName("compactTimeLabel")

        self.compact_repetition_label = QLabel()
        self.compact_repetition_label.setMinimumWidth(
            34
        )
        self.compact_repetition_label.setMaximumWidth(
            150
        )
        self.compact_repetition_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.compact_repetition_label.setObjectName("secondaryLabel")

        self.compact_start_button = QPushButton("▶")
        self.compact_start_button.setObjectName("compactButton")
        self.compact_start_button.clicked.connect(
            self._toggle_start_pause
        )

        self.expand_button = QPushButton("□")
        self.expand_button.setObjectName("windowButton")
        self.expand_button.setToolTip("Modo normal")
        self.expand_button.clicked.connect(
            self._toggle_compact_mode
        )

        self.compact_settings_button = QPushButton("⚙")
        self.compact_settings_button.setObjectName(
            "windowButton"
        )
        self.compact_settings_button.setToolTip(
            "Configurar ciclo"
        )
        self.compact_settings_button.clicked.connect(
            self._open_cycle_editor
        )
        self.compact_close_button = QPushButton("×")
        self.compact_close_button.setObjectName("closeButton")
        self.compact_close_button.clicked.connect(self.close)

        # layout.addWidget(self.compact_indicator)
        layout.addWidget(self.compact_phase_label)

        layout.addStretch()

        center_layout = QHBoxLayout()
        center_layout.setSpacing(8)

        center_layout.addWidget(self.compact_time_label)
        center_layout.addWidget(self.compact_repetition_label)

        layout.addLayout(center_layout)

        layout.addStretch()

        layout.addWidget(self.compact_start_button)
        layout.addWidget(self.compact_settings_button)
        layout.addWidget(self.expand_button)
        layout.addWidget(self.compact_close_button)

        self.compact_view.hide()

        self.main_layout.addWidget(self.compact_view)

    def _restore_window_state(self) -> None:
        geometry = self.settings.value(
            "window/geometry"
        )

        if geometry is not None:
            self.restoreGeometry(geometry)

        normal_size = self.settings.value(
            "window/normal_size"
        )

        compact_mode = self.settings.value(
            "window/compact_mode",
            False,
            type=bool,
        )

        if normal_size is not None:
            self.resize(normal_size)

        if compact_mode:
            self._toggle_compact_mode()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.setValue(
            "window/geometry",
            self.saveGeometry(),
        )

        self.settings.setValue(
            "window/compact_mode",
            self.compact_mode,
        )

        if not self.compact_mode:
            self.settings.setValue(
                "window/normal_size",
                self.size(),
            )

        self.settings.sync()

        event.accept()

        QApplication.quit()

    def _apply_cycle(
        self,
        cycle: Cycle,
    ) -> None:
        self.timer.stop()

        self.engine = TimerEngine(
            cycle
        )

        self._update_ui()

    def _open_cycle_editor(self) -> None:
        self._close_preset_panel()

        self.cycle_editor.load_cycle(
            self.engine.cycle,
            self.presets,
        )

        self.normal_view.hide()
        self.compact_view.hide()

        self.setMaximumHeight(16777215)
        self.setMinimumSize(620, 420)
        self.resize(620, 420)

        self.cycle_editor.show()

    def _save_cycle_configuration(
        self,
        cycle: Cycle,
    ) -> None:
        original_name = (
            self.cycle_editor
            .original_preset_name
        )

        duplicate = next(
            (
                preset
                for preset in self.presets
                if (
                    preset.name == cycle.name
                    and preset.name
                    != original_name
                )
            ),
            None,
        )

        if duplicate is not None:
            QMessageBox.warning(
                self,
                "Nombre duplicado",
                (
                    "Ya existe un ciclo con "
                    "ese nombre."
                ),
            )
            return

        if original_name is None:
            self.presets.append(
                cycle
            )

        else:
            for index, preset in enumerate(
                self.presets
            ):
                if (
                    preset.name
                    == original_name
                ):
                    self.presets[index] = (
                        cycle
                    )
                    break

        self.active_preset_name = (
            cycle.name
        )

        self.cycle_storage.save_presets(
            self.presets,
            self.active_preset_name,
        )

        self._apply_cycle(
            cycle
        )

        self._refresh_preset_selector()

        self._close_cycle_editor()

    def _replace_active_preset(
        self,
        cycle: Cycle,
    ) -> None:

        for preset in self.presets:
            if (
                preset.name == cycle.name
                and preset.name
                != self.active_preset_name
            ):
                raise ValueError(
                    "Ya existe un ciclo con ese nombre."
                )
        
        for index, preset in enumerate(
            self.presets
        ):
            if (
                preset.name
                == self.active_preset_name
            ):
                self.presets[index] = cycle
                self.active_preset_name = (
                    cycle.name
                )
                return

        self.presets.append(cycle)
        self.active_preset_name = (
            cycle.name
        )

    def _close_cycle_editor(self) -> None:
        self.cycle_editor.hide()

        if self.compact_mode:
            self.compact_view.show()

            self.setMinimumSize(360, 58)
            self.setMaximumHeight(64)
            self.resize(*self.COMPACT_SIZE)

        else:
            self.normal_view.show()

            self.setMaximumHeight(16777215)
            self.setMinimumSize(300, 150)
            self.resize(*self.NORMAL_SIZE)

    def _delete_preset(
        self,
        preset_name: str,
    ) -> None:
        if len(self.presets) <= 1:
            return

        self.presets = [
            preset
            for preset in self.presets
            if preset.name != preset_name
        ]

        new_active_cycle = (
            self.presets[0]
        )

        self.active_preset_name = (
            new_active_cycle.name
        )

        self.cycle_storage.save_presets(
            self.presets,
            self.active_preset_name,
        )

        self._apply_cycle(
            new_active_cycle
        )

        self._refresh_preset_selector()

        self.cycle_editor.load_cycle(
            new_active_cycle,
            self.presets,
        )

    def _create_preset_panel(self) -> None:
        self.preset_panel = QFrame()
        self.preset_panel.setObjectName(
            "presetPanel"
        )

        panel_layout = QVBoxLayout(
            self.preset_panel
        )

        panel_layout.setContentsMargins(
            4,
            2,
            4,
            6,
        )

        self.preset_scroll = QScrollArea()

        self.preset_scroll.setWidgetResizable(
            True
        )

        self.preset_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.preset_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.preset_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.preset_list_container = QWidget()

        self.preset_panel_layout = QVBoxLayout(
            self.preset_list_container
        )

        self.preset_panel_layout.setContentsMargins(
            8,
            6,
            8,
            6,
        )

        self.preset_panel_layout.setSpacing(
            2
        )

        self.preset_panel_layout.addStretch()

        self.preset_scroll.setWidget(
            self.preset_list_container
        )

        panel_layout.addWidget(
            self.preset_scroll
        )

        self.preset_panel.hide()

        self.normal_layout.addWidget(
            self.preset_panel
        )

    def _toggle_preset_panel(self) -> None:
        if self.preset_panel.isVisible():
            self._close_preset_panel()
            return

        self._refresh_preset_selector()

        self.preset_panel_previous_height = (
            self.height()
        )

        self.preset_panel.show()

        extra_height = (
            self.preset_panel.height()
            + self.normal_layout.spacing()
            + 12
        )

        self.setMaximumHeight(16777215)

        self.resize(
            self.width(),
            self.height() + extra_height,
        )

    def _select_preset(
        self,
        preset_name: str,
    ) -> None:
        self._close_preset_panel()

        self._change_preset(
            preset_name
        )

        self._refresh_preset_selector()

    def _close_preset_panel(self) -> None:
        if not self.preset_panel.isVisible():
            return

        self.preset_panel.hide()

        if (
            self.preset_panel_previous_height
            is not None
        ):
            self.resize(
                self.width(),
                self.preset_panel_previous_height,
            )

        self.preset_panel_previous_height = None

    def _update_preset_panel_height(
        self,
    ) -> None:
        row_height = 32
        spacing = 2
        margins = 12

        preset_count = len(
            self.presets
        )

        visible_rows = min(
            preset_count,
            5,
        )

        panel_height = (
            visible_rows * row_height
            + max(
                0,
                visible_rows - 1,
            ) * spacing
            + margins
        )

        self.preset_panel.setFixedHeight(
            panel_height
        )

    def _elide_text(
        self,
        label: QLabel,
        text: str,
        width: int,
    ) -> str:
        return label.fontMetrics().elidedText(
            text,
            Qt.TextElideMode.ElideRight,
            width,
        )