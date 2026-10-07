from enum import Enum, auto

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase


class TimerState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    WAITING = auto()
    FINISHED = auto()


class TimerEngine:
    def __init__(self, cycle: Cycle) -> None:
        self.cycle = cycle
        self.state = TimerState.IDLE

        self.current_phase_index = 0
        self.current_repetition = 1
        self.remaining_seconds = self.current_phase.duration_seconds

    @property
    def current_phase(self) -> Phase:
        return self.cycle.phases[self.current_phase_index]

    def start(self) -> None:
        if self.state == TimerState.FINISHED:
            return

        self.state = TimerState.RUNNING

    def pause(self) -> None:
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED

    def resume(self) -> None:
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING

    def reset(self) -> None:
        self.state = TimerState.IDLE
        self.current_phase_index = 0
        self.current_repetition = 1
        self.remaining_seconds = self.current_phase.duration_seconds

    def skip(self) -> None:
        if self.state == TimerState.FINISHED:
            return

        self._advance_phase()

    def continue_from_waiting(self) -> None:
        if self.state != TimerState.WAITING:
            return

        self.state = TimerState.RUNNING

    def tick(self) -> None:
        if self.state != TimerState.RUNNING:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

        if self.remaining_seconds == 0:
            self._complete_current_phase()

    def _complete_current_phase(self) -> None:
        auto_start_next = self.current_phase.auto_start_next

        self._advance_phase()

        if self.state == TimerState.FINISHED:
            return

        if auto_start_next:
            self.state = TimerState.RUNNING
        else:
            self.state = TimerState.WAITING

    def _advance_phase(self) -> None:
        last_phase_index = len(self.cycle.phases) - 1

        if self.current_phase_index < last_phase_index:
            self.current_phase_index += 1
            self.remaining_seconds = self.current_phase.duration_seconds
            return

        if self.cycle.is_infinite:
            self.current_phase_index = 0
            self.current_repetition += 1
            self.remaining_seconds = self.current_phase.duration_seconds
            return

        if self.current_repetition < self.cycle.repetitions:
            self.current_repetition += 1
            self.current_phase_index = 0
            self.remaining_seconds = self.current_phase.duration_seconds
            return

        self.state = TimerState.FINISHED
        self.remaining_seconds = 0
