from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    # QDialog, --> ya no se usa, se reemplaza por QDialogButtonBox
    QDialogButtonBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    # QTableWidgetItem, --> ya no se usa, se reemplaza por QLineEdit y QSpinBox
    QVBoxLayout,
    QWidget,
    
)

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from copy import deepcopy



class CycleEditor(QWidget):
    saved = Signal(object)
    cancelled = Signal()
    delete_requested = Signal(str)
    def __init__(
        self,
        cycle: Cycle,
        presets: list[Cycle],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.cycle = cycle
        self.presets = presets
        self.original_preset_name: str | None = (
            cycle.name
        )
        self._create_ui()
        self._load_cycle()

    def _create_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        self._create_cycle_settings(main_layout)
        self._create_preset_buttons(main_layout)
        self._create_delete_confirmation(main_layout)
        self._create_phase_table(main_layout)
        self._create_phase_buttons(main_layout)
        self._create_dialog_buttons(main_layout)

    def _create_cycle_settings(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        name_layout = QHBoxLayout()

        name_label = QLabel("Nombre del ciclo:")
        self.name_input = QLineEdit()

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)

        parent_layout.addLayout(name_layout)

        repetition_layout = QHBoxLayout()

        repetition_label = QLabel("Repeticiones:")

        self.repetitions_input = QSpinBox()
        self.repetitions_input.setRange(1, 999)
        self.repetitions_input.setValue(1)

        self.infinite_checkbox = QCheckBox("Infinito")
        self.infinite_checkbox.toggled.connect(
            self._toggle_infinite
        )

        repetition_layout.addWidget(repetition_label)
        repetition_layout.addWidget(self.repetitions_input)
        repetition_layout.addWidget(self.infinite_checkbox)
        repetition_layout.addStretch()

        parent_layout.addLayout(repetition_layout)

    def _create_phase_table(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        phases_label = QLabel("Fases")
        parent_layout.addWidget(phases_label)

        self.phase_table = QTableWidget(0, 4)

        self.phase_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.phase_table.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.phase_table.setHorizontalHeaderLabels(
            [
                "Nombre",
                "Min",
                "Seg",
                "Auto iniciar siguiente",
            ]
        )

        header = self.phase_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.phase_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        parent_layout.addWidget(self.phase_table)

    def _create_phase_buttons(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        buttons_layout = QHBoxLayout()

        add_button = QPushButton("+ Añadir fase")
        remove_button = QPushButton("- Eliminar fase")
        move_up_button = QPushButton("↑ Subir")
        move_down_button = QPushButton("↓ Bajar")
        
        add_button.clicked.connect(self._add_phase)
        remove_button.clicked.connect(self._remove_phase)
        move_up_button.clicked.connect(self._move_phase_up)
        move_down_button.clicked.connect(self._move_phase_down)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)

        buttons_layout.addStretch()

        parent_layout.addLayout(buttons_layout)

    def _create_dialog_buttons(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        self.dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.dialog_buttons.accepted.connect(
            self._save
        )

        self.dialog_buttons.rejected.connect(
            self.cancelled.emit
        )

        parent_layout.addWidget(self.dialog_buttons)

    def _load_cycle(self) -> None:
        self._populate_form(
            self.cycle
        )

        self.name_input.setFocus()

    def _append_phase_row(
        self,
        phase: Phase | None = None,
    ) -> None:
        row = self.phase_table.rowCount()
        self.phase_table.insertRow(row)

        if phase is None:
            phase = Phase(
                name="Nueva fase",
                duration_seconds=5 * 60,
                auto_start_next=True,
            )

        name_input = QLineEdit()
        name_input.setText(
            phase.name
        )

        minutes_input = QSpinBox()
        minutes_input.setRange(
            0,
            999,
        )

        seconds_input = QSpinBox()
        seconds_input.setRange(
            0,
            59,
        )

        minutes, seconds = divmod(
            phase.duration_seconds,
            60,
        )

        minutes_input.setValue(
            minutes
        )

        seconds_input.setValue(
            seconds
        )

        auto_checkbox = QCheckBox()
        auto_checkbox.setChecked(
            phase.auto_start_next
        )

        auto_container = QWidget()
        auto_layout = QHBoxLayout(
            auto_container
        )

        auto_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        auto_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        auto_layout.addWidget(
            auto_checkbox
        )

        self.phase_table.setCellWidget(
            row,
            0,
            name_input,
        )

        self.phase_table.setCellWidget(
            row,
            1,
            minutes_input,
        )

        self.phase_table.setCellWidget(
            row,
            2,
            seconds_input,
        )

        self.phase_table.setCellWidget(
            row,
            3,
            auto_container,
        )

    def _add_phase(self) -> None:
        self._append_phase_row()

    def _remove_phase(self) -> None:
        selected_rows = {
            index.row()
            for index
            in self.phase_table.selectedIndexes()
        }

        for row in sorted(
            selected_rows,
            reverse=True,
        ):
            self.phase_table.removeRow(row)

    def _toggle_infinite(
        self,
        checked: bool,
    ) -> None:
        self.repetitions_input.setEnabled(
            not checked
        )

    def _save(self) -> None:
        try:
            cycle = self._build_cycle()

            for preset in self.presets:
                if (
                    preset.name == cycle.name
                    and preset is not self.cycle
                ):
                    QMessageBox.warning(
                        self,
                        "Nombre duplicado",
                        (
                            "Ya existe un ciclo con "
                            "ese nombre."
                        ),
                    )
                    return

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Configuración no válida",
                str(error),
            )
            return

        self.cycle = cycle
        self.saved.emit(cycle)

    def _build_cycle(self) -> Cycle:
        name = self.name_input.text().strip()

        phases: list[Phase] = []

        for row in range(
            self.phase_table.rowCount()
        ):
            name_input = self.phase_table.cellWidget(
                row,
                0,
            )

            minutes_input = self.phase_table.cellWidget(
                row,
                1,
            )

            seconds_input = self.phase_table.cellWidget(
                row,
                2,
            )

            auto_container = self.phase_table.cellWidget(
                row,
                3,
            )

            if not isinstance(
                name_input,
                QLineEdit,
            ):
                raise ValueError(
                    "No se pudo leer el nombre de una fase."
                )

            if not isinstance(
                minutes_input,
                QSpinBox,
            ):
                raise ValueError(
                    "No se pudieron leer los minutos."
                )

            if not isinstance(
                seconds_input,
                QSpinBox,
            ):
                raise ValueError(
                    "No se pudieron leer los segundos."
                )

            phase_name = (
                name_input.text().strip()
            )

            if not phase_name:
                raise ValueError(
                    "Todas las fases deben tener nombre."
                )

            duration_seconds = (
                minutes_input.value() * 60
                + seconds_input.value()
            )

            if duration_seconds <= 0:
                raise ValueError(
                    "La duración debe ser mayor que 0 segundos."
                )

            auto_checkbox = (
                auto_container.findChild(
                    QCheckBox
                )
            )

            if auto_checkbox is None:
                raise ValueError(
                    "No se pudo leer la configuración automática."
                )

            phases.append(
                Phase(
                    name=phase_name,
                    duration_seconds=duration_seconds,
                    auto_start_next=(
                        auto_checkbox.isChecked()
                    ),
                )
            )

        repetitions = (
            None
            if self.infinite_checkbox.isChecked()
            else self.repetitions_input.value()
        )

        return Cycle(
            name=name,
            phases=phases,
            repetitions=repetitions,
        )

    def _create_preset_buttons(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        layout = QHBoxLayout()

        self.new_preset_button = QPushButton(
            "+ Nuevo"
        )

        self.duplicate_preset_button = QPushButton(
            "Duplicar"
        )

        self.delete_preset_button = QPushButton(
            "Eliminar"
        )

        self.new_preset_button.clicked.connect(
            self._new_preset
        )

        self.duplicate_preset_button.clicked.connect(
            self._duplicate_preset
        )

        self.delete_preset_button.clicked.connect(
            self._delete_preset
        )

        layout.addWidget(
            self.new_preset_button
        )

        layout.addWidget(
            self.duplicate_preset_button
        )

        layout.addWidget(
            self.delete_preset_button
        )

        layout.addStretch()

        parent_layout.addLayout(layout)

    def _new_preset(self) -> None:
        new_cycle = Cycle(
            name=self._unique_name(
                "Nuevo ciclo"
            ),
            phases=[
                Phase(
                    name="Concentración",
                    duration_seconds=25 * 60,
                    auto_start_next=True,
                ),
                Phase(
                    name="Descanso",
                    duration_seconds=5 * 60,
                    auto_start_next=True,
                ),
            ],
            repetitions=1,
        )

        self.cycle = new_cycle

        self.original_preset_name = None

        self._populate_form(
            new_cycle
        )

        self.delete_preset_button.setEnabled(
            False
        )

        self.name_input.setFocus()
        self.name_input.selectAll()

    def _duplicate_preset(self) -> None:
        try:
            current_cycle = self._build_cycle()

        except ValueError as error:
            QMessageBox.warning(
                self,
                "Configuración no válida",
                str(error),
            )
            return

        duplicate = deepcopy(
            current_cycle
        )

        duplicate.name = self._unique_name(
            f"{current_cycle.name} - copia"
        )

        self.cycle = duplicate
        self.original_preset_name = None

        self._populate_form(
            duplicate
        )

        self.delete_preset_button.setEnabled(
            False
        )

        self.name_input.setFocus()
        self.name_input.selectAll()

    def load_cycle(
        self,
        cycle: Cycle,
        presets: list[Cycle] | None = None,
    ) -> None:
        self.cycle = cycle

        if presets is not None:
            self.presets = presets

        self.original_preset_name = (
            cycle.name
        )

        self._populate_form(
            cycle
        )

        self.delete_preset_button.setEnabled(
            True
        )

        self.delete_confirm_container.hide()

    def _populate_form(
        self,
        cycle: Cycle,
    ) -> None:
        self.name_input.setText(
            cycle.name
        )

        if cycle.is_infinite:
            self.infinite_checkbox.setChecked(
                True
            )
        else:
            self.infinite_checkbox.setChecked(
                False
            )

            self.repetitions_input.setValue(
                cycle.repetitions
            )

        self.phase_table.setRowCount(0)

        for phase in cycle.phases:
            self._append_phase_row(
                phase
            )

    def _unique_name(
        self,
        base_name: str,
    ) -> str:
        existing_names = {
            preset.name
            for preset in self.presets
        }

        if base_name not in existing_names:
            return base_name

        counter = 2

        while True:
            candidate = (
                f"{base_name} {counter}"
            )

            if candidate not in existing_names:
                return candidate

            counter += 1

    def _delete_preset(self) -> None:
        if self.original_preset_name is None:
            return

        if len(self.presets) <= 1:
            self.delete_confirm_label.setText(
                "PomoFloat debe conservar al menos un ciclo."
            )

            self.delete_yes_button.hide()
            self.delete_no_button.setText("Cerrar")

            self.delete_confirm_container.show()
            return

        self.delete_confirm_label.setText(
            f"¿Eliminar el ciclo "
            f"'{self.original_preset_name}'?"
        )

        self.delete_yes_button.show()
        self.delete_no_button.setText("Cancelar")

        self.delete_confirm_container.show()

    def _create_delete_confirmation(
        self,
        parent_layout: QVBoxLayout,
    ) -> None:
        self.delete_confirm_container = QWidget()

        layout = QHBoxLayout(
            self.delete_confirm_container
        )

        layout.setContentsMargins(
            0,
            4,
            0,
            4,
        )

        self.delete_confirm_label = QLabel()

        self.delete_yes_button = QPushButton(
            "Sí, eliminar"
        )

        self.delete_no_button = QPushButton(
            "Cancelar"
        )

        self.delete_yes_button.clicked.connect(
            self._confirm_delete_preset
        )

        self.delete_no_button.clicked.connect(
            self._cancel_delete_preset
        )

        layout.addWidget(
            self.delete_confirm_label
        )

        layout.addStretch()

        layout.addWidget(
            self.delete_yes_button
        )

        layout.addWidget(
            self.delete_no_button
        )

        self.delete_confirm_container.hide()

        parent_layout.addWidget(
            self.delete_confirm_container
        )

    def _confirm_delete_preset(self) -> None:
        if self.original_preset_name is None:
            return

        preset_name = (
            self.original_preset_name
        )

        self.delete_confirm_container.hide()

        self.delete_requested.emit(
            preset_name
        )

    def _cancel_delete_preset(self) -> None:
        self.delete_confirm_container.hide()

    def _selected_phase_row(
        self,
    ) -> int | None:
        indexes = (
            self.phase_table
            .selectionModel()
            .selectedRows()
        )

        if not indexes:
            return None

        return indexes[0].row()

    def _selected_phase_row(
        self,
    ) -> int | None:
        indexes = (
            self.phase_table
            .selectionModel()
            .selectedRows()
        )

        if not indexes:
            return None

        return indexes[0].row()

    def _phase_from_row(
        self,
        row: int,
    ) -> Phase:
        name_input = self.phase_table.cellWidget(
            row,
            0,
        )

        minutes_input = self.phase_table.cellWidget(
            row,
            1,
        )

        seconds_input = self.phase_table.cellWidget(
            row,
            2,
        )

        auto_container = self.phase_table.cellWidget(
            row,
            3,
        )

        if not isinstance(
            name_input,
            QLineEdit,
        ):
            raise ValueError(
                "No se pudo leer la fase."
            )

        if not isinstance(
            minutes_input,
            QSpinBox,
        ):
            raise ValueError(
                "No se pudieron leer los minutos."
            )

        if not isinstance(
            seconds_input,
            QSpinBox,
        ):
            raise ValueError(
                "No se pudieron leer los segundos."
            )

        auto_checkbox = (
            auto_container.findChild(
                QCheckBox
            )
        )

        if auto_checkbox is None:
            raise ValueError(
                "No se pudo leer el auto inicio."
            )

        duration_seconds = (
            minutes_input.value() * 60
            + seconds_input.value()
        )

        return Phase(
            name=name_input.text().strip(),
            duration_seconds=duration_seconds,
            auto_start_next=(
                auto_checkbox.isChecked()
            ),
        )

    def _current_phases(
        self,
    ) -> list[Phase]:
        return [
            self._phase_from_row(row)
            for row in range(
                self.phase_table.rowCount()
            )
        ]

    def _set_phases(
        self,
        phases: list[Phase],
    ) -> None:
        self.phase_table.setRowCount(0)

        for phase in phases:
            self._append_phase_row(
                phase
            )

    def _move_phase_up(self) -> None:
        row = self._selected_phase_row()

        if row is None:
            return

        if row <= 0:
            return

        phases = self._current_phases()

        phases[row - 1], phases[row] = (
            phases[row],
            phases[row - 1],
        )

        self._set_phases(
            phases
        )

        self.phase_table.selectRow(
            row - 1
        )

    def _move_phase_down(self) -> None:
        row = self._selected_phase_row()

        if row is None:
            return

        last_row = (
            self.phase_table.rowCount()
            - 1
        )

        if row >= last_row:
            return

        phases = self._current_phases()

        phases[row + 1], phases[row] = (
            phases[row],
            phases[row + 1],
        )

        self._set_phases(
            phases
        )

        self.phase_table.selectRow(
            row + 1
        )