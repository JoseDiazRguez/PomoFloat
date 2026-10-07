from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase
from pomofloat.core.timer import TimerEngine, TimerState


def create_test_cycle() -> Cycle:
    return Cycle(
        name="Ciclo de prueba",
        phases=[
            Phase("Trabajo", 3),
            Phase("Descanso", 2),
        ],
        repetitions=2,
    )


def test_timer_initial_state() -> None:
    engine = TimerEngine(create_test_cycle())

    assert engine.state == TimerState.IDLE
    assert engine.current_phase.name == "Trabajo"
    assert engine.current_phase_index == 0
    assert engine.current_repetition == 1
    assert engine.remaining_seconds == 3


def test_timer_can_start() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()

    assert engine.state == TimerState.RUNNING


def test_timer_can_pause_and_resume() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()
    engine.pause()

    assert engine.state == TimerState.PAUSED

    engine.resume()

    assert engine.state == TimerState.RUNNING


def test_tick_reduces_remaining_time() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()
    engine.tick()

    assert engine.remaining_seconds == 2


def test_tick_does_nothing_when_paused() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()
    engine.pause()
    engine.tick()

    assert engine.remaining_seconds == 3


def test_timer_advances_to_next_phase() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()

    engine.tick()
    engine.tick()
    engine.tick()

    assert engine.current_phase.name == "Descanso"
    assert engine.current_phase_index == 1
    assert engine.remaining_seconds == 2


def test_timer_moves_to_next_repetition() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()

    for _ in range(5):
        engine.tick()

    assert engine.current_repetition == 2
    assert engine.current_phase.name == "Trabajo"
    assert engine.remaining_seconds == 3


def test_timer_finishes_after_last_repetition() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()

    for _ in range(10):
        engine.tick()

    assert engine.state == TimerState.FINISHED
    assert engine.remaining_seconds == 0


def test_timer_reset() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()
    engine.tick()
    engine.tick()

    engine.reset()

    assert engine.state == TimerState.IDLE
    assert engine.current_phase.name == "Trabajo"
    assert engine.current_phase_index == 0
    assert engine.current_repetition == 1
    assert engine.remaining_seconds == 3


def test_timer_skip_phase() -> None:
    engine = TimerEngine(create_test_cycle())

    engine.start()
    engine.skip()

    assert engine.current_phase.name == "Descanso"
    assert engine.remaining_seconds == 2


def test_manual_phase_waits_for_confirmation() -> None:
    cycle = Cycle(
        name="Manual",
        phases=[
            Phase(
                "Trabajo",
                1,
                auto_start_next=False,
            ),
            Phase("Descanso", 2),
        ],
    )

    engine = TimerEngine(cycle)

    engine.start()
    engine.tick()

    assert engine.current_phase.name == "Descanso"
    assert engine.state == TimerState.WAITING

    engine.continue_from_waiting()

    assert engine.state == TimerState.RUNNING


def test_infinite_cycle_never_finishes() -> None:
    cycle = Cycle(
        name="Infinito",
        phases=[
            Phase("Trabajo", 1),
            Phase("Descanso", 1),
        ],
        repetitions=None,
    )

    engine = TimerEngine(cycle)

    engine.start()

    for _ in range(100):
        engine.tick()

    assert engine.state == TimerState.RUNNING
    assert engine.current_repetition == 51
