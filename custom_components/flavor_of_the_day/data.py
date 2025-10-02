"""Data structures for the Flavor of the Day integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .coordinator import FlavorUpdateCoordinator
    from .providers.base import BaseFlavorProvider


@dataclass
class FlavorOfTheDayData:
    """Runtime data for the Flavor of the Day integration."""

    coordinator: FlavorUpdateCoordinator
    provider: BaseFlavorProvider
