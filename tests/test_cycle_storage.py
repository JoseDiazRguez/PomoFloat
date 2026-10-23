from pathlib import Path

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from pomofloat.services.cycle_storage import CycleStorage


def test_load_presets_returns_empty_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    presets, active_preset = (
        storage.load_presets()
    )

    assert presets == []
    assert active_preset is None


def test_save_and_load_single_preset(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    cycle = Cycle(
        name="Trabajo",
        phases=[
            Phase(
                name="Concentración",
                duration_seconds=25 * 60,
                auto_start_next=True,
            ),
            Phase(
                name="Descanso",
                duration_seconds=5 * 60,
                auto_start_next=False,
            ),
        ],
        repetitions=4,
    )

    storage.save_presets(
        [cycle],
        "Trabajo",
    )

    presets, active_preset = (
        storage.load_presets()
    )

    assert active_preset == "Trabajo"
    assert len(presets) == 1

    loaded_cycle = presets[0]

    assert loaded_cycle.name == "Trabajo"
    assert loaded_cycle.repetitions == 4
    assert len(loaded_cycle.phases) == 2

    assert loaded_cycle.phases[0].name == (
        "Concentración"
    )

    assert (
        loaded_cycle.phases[0]
        .duration_seconds
        == 25 * 60
    )

    assert (
        loaded_cycle.phases[0]
        .auto_start_next
        is True
    )

    assert loaded_cycle.phases[1].name == (
        "Descanso"
    )

    assert (
        loaded_cycle.phases[1]
        .duration_seconds
        == 5 * 60
    )

    assert (
        loaded_cycle.phases[1]
        .auto_start_next
        is False
    )


def test_save_and_load_multiple_presets(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    work_cycle = Cycle(
        name="Trabajo",
        phases=[
            Phase(
                name="Trabajo",
                duration_seconds=50 * 60,
            ),
            Phase(
                name="Descanso",
                duration_seconds=10 * 60,
            ),
        ],
        repetitions=4,
    )

    study_cycle = Cycle(
        name="Estudio",
        phases=[
            Phase(
                name="Estudiar",
                duration_seconds=40 * 60,
            ),
            Phase(
                name="Descanso",
                duration_seconds=10 * 60,
            ),
        ],
        repetitions=3,
    )

    storage.save_presets(
        [
            work_cycle,
            study_cycle,
        ],
        "Estudio",
    )

    presets, active_preset = (
        storage.load_presets()
    )

    assert len(presets) == 2
    assert active_preset == "Estudio"

    assert presets[0].name == "Trabajo"
    assert presets[1].name == "Estudio"


def test_infinite_repetitions_are_preserved(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    cycle = Cycle(
        name="Infinito",
        phases=[
            Phase(
                name="Trabajo",
                duration_seconds=60,
            )
        ],
        repetitions=None,
    )

    storage.save_presets(
        [cycle],
        "Infinito",
    )

    presets, _ = storage.load_presets()

    assert presets[0].repetitions is None
    assert presets[0].is_infinite is True


def test_phase_order_is_preserved(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    cycle = Cycle(
        name="Orden",
        phases=[
            Phase(
                name="Primera",
                duration_seconds=10,
            ),
            Phase(
                name="Segunda",
                duration_seconds=20,
            ),
            Phase(
                name="Tercera",
                duration_seconds=30,
            ),
        ],
        repetitions=1,
    )

    storage.save_presets(
        [cycle],
        "Orden",
    )

    presets, _ = storage.load_presets()

    phase_names = [
        phase.name
        for phase in presets[0].phases
    ]

    assert phase_names == [
        "Primera",
        "Segunda",
        "Tercera",
    ]


def test_seconds_are_preserved_exactly(
    tmp_path: Path,
) -> None:
    storage = CycleStorage(
        tmp_path / "presets.json"
    )

    cycle = Cycle(
        name="Segundos",
        phases=[
            Phase(
                name="Prueba",
                duration_seconds=90,
            )
        ],
        repetitions=1,
    )

    storage.save_presets(
        [cycle],
        "Segundos",
    )

    presets, _ = storage.load_presets()

    assert (
        presets[0]
        .phases[0]
        .duration_seconds
        == 90
    )


def test_storage_creates_parent_directory(
    tmp_path: Path,
) -> None:
    storage_path = (
        tmp_path
        / "config"
        / "pomofloat"
        / "presets.json"
    )

    storage = CycleStorage(
        storage_path
    )

    cycle = Cycle(
        name="Trabajo",
        phases=[
            Phase(
                name="Trabajo",
                duration_seconds=60,
            )
        ],
        repetitions=1,
    )

    storage.save_presets(
        [cycle],
        "Trabajo",
    )

    assert storage_path.exists()