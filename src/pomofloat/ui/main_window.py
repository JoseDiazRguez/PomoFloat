from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizeGrip,
    QVBoxLayout,
    QWidget,
)

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from pomofloat.core.timer import TimerEngine, TimerState


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self._drag_position: QPoint | None = None

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

    def _configure_window(self) -> None:
        self.setWindowTitle("PomoFloat")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        self.setMinimumSize(280, 160)
        self.resize(340, 200)

    def _create_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        self.phase_label = QLabel()
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.state_label = QLabel()
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_pause_button = QPushButton("Iniciar")
        self.start_pause_button.clicked.connect(self._toggle_start_pause)

        self.reset_button = QPushButton("Reiniciar")
        self.reset_button.clicked.connect(self._reset)

        self.skip_button = QPushButton("Saltar")
        self.skip_button.clicked.connect(self._skip)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_pause_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.skip_button)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.size_grip = QSizeGrip(self)
        bottom_layout.addWidget(self.size_grip)

        main_layout.addWidget(self.phase_label)
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.state_label)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(bottom_layout)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #202124;
                color: #f1f3f4;
                font-family: Arial;
            }

            QLabel {
                background: transparent;
            }

            QPushButton {
                background-color: #303134;
                border: 1px solid #5f6368;
                border-radius: 8px;
                padding: 7px 12px;
            }

            QPushButton:hover {
                background-color: #3c4043;
            }

            QPushButton:pressed {
                background-color: #4a4d51;
            }
            """
        )

        self.phase_label.setStyleSheet(
            """
            font-size: 16px;
            font-weight: 600;
            """
        )

        self.time_label.setStyleSheet(
            """
            font-size: 42px;
            font-weight: 700;
            """
        )

        self.state_label.setStyleSheet(
            """
            font-size: 11px;
            color: #9aa0a6;
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

    def _update_ui(self) -> None:
        self.phase_label.setText(self.engine.current_phase.name)

        minutes, seconds = divmod(
            self.engine.remaining_seconds,
            60,
        )

        self.time_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        self.state_label.setText(
            f"{self.engine.state.name} · "
            f"Repetición {self.engine.current_repetition}"
        )

        if self.engine.state == TimerState.IDLE:
            self.start_pause_button.setText("Iniciar")

        elif self.engine.state == TimerState.RUNNING:
            self.start_pause_button.setText("Pausar")

        elif self.engine.state == TimerState.PAUSED:
            self.start_pause_button.setText("Continuar")

        elif self.engine.state == TimerState.WAITING:
            self.start_pause_button.setText("Continuar")

        elif self.engine.state == TimerState.FINISHED:
            self.start_pause_button.setText("Finalizado")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_position = None
        super().mouseReleaseEvent(event)
