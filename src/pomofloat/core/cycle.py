from dataclasses import dataclass, field

from pomofloat.core.phase import Phase


@dataclass
class Cycle:
    name: str
    phases: list[Phase] = field(default_factory=list)
    repetitions: int | None = 1

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Cycle name cannot be empty.")

        if not self.phases:
            raise ValueError("Cycle must contain at least one phase.")

        if self.repetitions is not None and self.repetitions <= 0:
            raise ValueError(
                "Cycle repetitions must be greater than 0 or None for infinite."
            )

    @property
    def is_infinite(self) -> bool:
        return self.repetitions is None

    @property
    def duration_seconds(self) -> int | None:
        if self.is_infinite:
            return None

        phase_duration = sum(
            phase.duration_seconds
            for phase in self.phases
        )

        return phase_duration * self.repetitions
