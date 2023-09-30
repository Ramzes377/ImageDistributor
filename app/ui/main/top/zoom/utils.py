from dataclasses import dataclass, asdict


@dataclass(frozen=True, slots=True)
class SliderRange:
    from_: int | float
    to: int | float
    resolution: int | float

    dict = asdict


@dataclass(frozen=True, slots=True)
class SliderSettings:
    name: str
    default: int | float
    range: SliderRange
