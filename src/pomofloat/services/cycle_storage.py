import json
from pathlib import Path

from pomofloat.core.cycle import Cycle
from pomofloat.core.phase import Phase


class CycleStorage:
    def __init__(
        self,
        storage_path: Path | None = None,
    ) -> None:
        if storage_path is None:
            storage_path = (
                Path.home()
                / ".pomofloat"
                / "presets.json"
            )

        self.storage_path = storage_path

    def load_presets(self) -> tuple[list[Cycle], str | None]:
        if not self.storage_path.exists():
            return [], None

        with self.storage_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        presets = [
            self._cycle_from_dict(item)
            for item in data.get(
                "presets",
                [],
            )
        ]

        active_preset = data.get(
            "active_preset"
        )

        return presets, active_preset

    def save_presets(
        self,
        presets: list[Cycle],
        active_preset: str | None,
    ) -> None:
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = {
            "active_preset": active_preset,
            "presets": [
                self._cycle_to_dict(cycle)
                for cycle in presets
            ],
        }

        with self.storage_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def _cycle_to_dict(
        self,
        cycle: Cycle,
    ) -> dict:
        return {
            "name": cycle.name,
            "repetitions": cycle.repetitions,
            "phases": [
                {
                    "name": phase.name,
                    "duration_seconds": (
                        phase.duration_seconds
                    ),
                    "auto_start_next": (
                        phase.auto_start_next
                    ),
                }
                for phase in cycle.phases
            ],
        }

    def _cycle_from_dict(
        self,
        data: dict,
    ) -> Cycle:
        phases = [
            Phase(
                name=phase_data["name"],
                duration_seconds=(
                    phase_data[
                        "duration_seconds"
                    ]
                ),
                auto_start_next=(
                    phase_data.get(
                        "auto_start_next",
                        True,
                    )
                ),
            )
            for phase_data
            in data["phases"]
        ]

        return Cycle(
            name=data["name"],
            phases=phases,
            repetitions=data.get(
                "repetitions",
                1,
            ),
        )