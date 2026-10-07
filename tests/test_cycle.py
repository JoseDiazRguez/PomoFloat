import pytest

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase


def test_cycle_creation() -> None:
    cycle = Cycle(
        name="Pomodoro clásico",
        phases=[
            Phase("Concentración", 1500),
            Phase("Descanso", 300),
        ],
        repetitions=4,
    )

    assert cycle.name == "Pomodoro clásico"
    assert len(cycle.phases) == 2
    assert cycle.repetitions == 4


def test_cycle_duration() -> None:
    cycle = Cycle(
        name="Pomodoro clásico",
        phases=[
            Phase("Concentración", 1500),
            Phase("Descanso", 300),
        ],
        repetitions=4,
    )

    assert cycle.duration_seconds == 7200


def test_infinite_cycle() -> None:
    cycle = Cycle(
        name="Trabajo continuo",
        phases=[
            Phase("Trabajo", 3000),
            Phase("Descanso", 600),
        ],
        repetitions=None,
    )

    assert cycle.is_infinite is True
    assert cycle.duration_seconds is None


def test_cycle_name_cannot_be_empty() -> None:
    with pytest.raises(ValueError):
        Cycle(
            name="",
            phases=[
                Phase("Concentración", 1500),
            ],
        )


def test_cycle_requires_at_least_one_phase() -> None:
    with pytest.raises(ValueError):
        Cycle(
            name="Ciclo vacío",
            phases=[],
        )


def test_cycle_repetitions_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Cycle(
            name="Ciclo inválido",
            phases=[
                Phase("Concentración", 1500),
            ],
            repetitions=0,
        )
