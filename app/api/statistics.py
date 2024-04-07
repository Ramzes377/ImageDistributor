from dataclasses import dataclass, field

from app.api import container


@dataclass
class Statistics:
    quantity: int | None = field(
        default_factory=lambda: len(
            list(container.cache.unregistered_images(container.sort_directory))
        )
    )
    counter: int = 0

    def incr(self):
        self.counter += 1

    @property
    def complete_percent(self) -> int:
        if self.quantity == 0:
            return 0

        return int(100 * self.counter / self.quantity)
