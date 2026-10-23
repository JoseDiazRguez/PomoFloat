import pytest

from pomofloat.core.phase import Phase


def test_phase_creation() -> None:
    phase = Phase(
        name="Concentración",
        duration_seconds=1500,
    )

    assert phase.name == "Concentración"
    assert phase.duration_seconds == 1500
    assert phase.auto_start_next is True


def test_phase_can_disable_auto_start() -> None:
    phase = Phase(
        name="Descanso",
        duration_seconds=300,
        auto_start_next=False,
    )

    assert phase.auto_start_next is False


def test_phase_name_cannot_be_empty() -> None:
    with pytest.raises(ValueError):
        Phase(
            name="",
            duration_seconds=1500,
        )


def test_phase_duration_must_be_positive() -> None:
    with pytest.raises(ValueError):
        Phase(
            name="Concentración",
            duration_seconds=0,
        )
