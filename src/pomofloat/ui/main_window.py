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
)

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from pomofloat.core.timer import TimerEngine, TimerState


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
    COMPACT_SIZE = (380, 64)

    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings("PomoFloat", "PomoFloat")

        self.compact_mode = False

        self.engine = TimerEngine(
            Cycle(
                name="Pomodoro clásico",
                phases=[
                    Phase("Concentración", 25 * 60),
                    Phase("Descanso", 5 * 60),
                ],
                repetitions=None,
            )
        )

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._on_tick)

        self._configure_window()
        self._create_ui()
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

        self._apply_styles()

    def _create_normal_view(self) -> None:
        self.normal_view = QWidget()

        self.normal_layout = QVBoxLayout(self.normal_view)
        self.normal_layout.setContentsMargins(0, 0, 0, 0)
        self.normal_layout.setSpacing(8)

        original_layout = self.main_layout
        self.main_layout = self.normal_layout

        self._create_header()
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

        self.phase_indicator = QLabel("●")

        self.phase_label = QLabel()
        self.phase_label.setObjectName("phaseLabel")

        self.repetition_label = QLabel()
        self.repetition_label.setObjectName("secondaryLabel")

        header_layout.addWidget(self.phase_indicator)
        header_layout.addWidget(self.phase_label)

        header_layout.addStretch()

        header_layout.addWidget(self.repetition_label)

        self.compact_button = QPushButton("▭")
        self.compact_button.setObjectName("windowButton")
        self.compact_button.setToolTip("Cambiar modo compacto")
        self.compact_button.clicked.connect(self._toggle_compact_mode)

        self.close_button = QPushButton("×")
        self.close_button.setObjectName("closeButton")
        self.close_button.setToolTip("Cerrar PomoFloat")
        self.close_button.clicked.connect(self.close)

        header_layout.addWidget(self.compact_button)
        header_layout.addWidget(self.close_button)

        self.main_layout.addWidget(self.header)

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
                font-size: 13px;
                font-weight: 700;
            }

            #timeLabel {
                font-size: 44px;
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
                font-size: 12px;
                font-weight: 600;
            }

            #compactTimeLabel {
                font-size: 18px;
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
        if not self.compact_mode:
            self.settings.setValue(
                "window/normal_size",
                self.size(),
            )

        self.compact_mode = not self.compact_mode

        if self.compact_mode:
            self.normal_view.hide()
            self.compact_view.show()

            self.setMinimumSize(360, 58)
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

        self.phase_label.setText(
            phase.name.upper()
            if not self.compact_mode
            else phase.name
        )

        minutes, seconds = divmod(
            self.engine.remaining_seconds,
            60,
        )

        formatted_time = f"{minutes:02d}:{seconds:02d}"

        self.time_label.setText(formatted_time)

        if self.engine.cycle.is_infinite:
            repetition_text = f"{self.engine.current_repetition} / ∞"
        else:
            repetition_text = (
                f"{self.engine.current_repetition} / "
                f"{self.engine.cycle.repetitions}"
            )

        self.repetition_label.setText(repetition_text)

        self.compact_phase_label.setText(phase.name)
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

        self.compact_indicator = QLabel("●")

        self.compact_phase_label = QLabel()
        self.compact_phase_label.setObjectName("compactPhaseLabel")

        self.compact_time_label = QLabel()
        self.compact_time_label.setObjectName("compactTimeLabel")

        self.compact_repetition_label = QLabel()
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

        self.compact_close_button = QPushButton("×")
        self.compact_close_button.setObjectName("closeButton")
        self.compact_close_button.clicked.connect(self.close)

        layout.addWidget(self.compact_indicator)
        layout.addWidget(self.compact_phase_label)

        layout.addStretch()

        layout.addWidget(self.compact_time_label)
        layout.addWidget(self.compact_repetition_label)
        layout.addWidget(self.compact_start_button)
        layout.addWidget(self.expand_button)
        layout.addWidget(self.compact_close_button)

        self.compact_view.hide()

        self.main_layout.addWidget(self.compact_view)

    def _restore_window_state(self) -> None:
        position = self.settings.value(
            "window/position"
        )

        if position is not None:
            self.move(position)

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
            "window/position",
            self.pos(),
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

        super().closeEvent(event)