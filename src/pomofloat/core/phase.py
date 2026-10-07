from dataclasses import dataclass


@dataclass
class Phase:
    name: str
    duration_seconds: int
    auto_start_next: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Phase name cannot be empty.")

        if self.duration_seconds <= 0:
            raise ValueError("Phase duration must be greater than 0 seconds.")
