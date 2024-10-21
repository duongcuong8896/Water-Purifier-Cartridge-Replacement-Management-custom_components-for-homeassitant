from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorStateClass,
)

from .const import ID_REMAIN_TIMES

@dataclass
class Entity:
    """Describe the sensor entities."""

    id: str
    friendly_name: str
    entity_class: str
    unit: str
    icon: str
    state_class: SensorStateClass or None
@dataclass
class MLNRequiredKeysMixin:
    """Mixin for required keys."""

    value_fn: Callable[[Any], float]

@dataclass
class MLNSensorEntityDescription(SensorEntityDescription, MLNRequiredKeysMixin):
    """Describes MLN sensor entity."""

    dynamic_name: None | bool = False
    dynamic_icon: None | bool = False


MLN_SENSORS: tuple[MLNSensorEntityDescription, ...] = tuple(
    # Current day
     MLNSensorEntityDescription(
        key=id_remain_time,
        name=f"Cartridges {i + 1} - ",
        icon="mdi:water-circle",
        value_fn=lambda data, key=id_remain_time: data[key],
        dynamic_name=True,
    )
    for i, id_remain_time in enumerate(ID_REMAIN_TIMES)
)