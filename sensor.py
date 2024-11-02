# type: ignore
"""Platform for sensor integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any
import re

from ecactusecos.const import (
    SOURCE_TYPE_BATTERY_SOC,
    SOURCE_TYPE_BATTERY_POWER,
    SOURCE_TYPE_EPS_POWER,
    SOURCE_TYPE_GRID_POWER,
    SOURCE_TYPE_HOME_POWER,
    SOURCE_TYPE_METER_POWER,
    SOURCE_TYPE_SOLAR_POWER,
)

from homeassistant.const import PERCENTAGE
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ID,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    SENSOR_TYPE_RATE,
)

_LOGGER = logging.getLogger(__name__)


def name_key(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


@dataclass(frozen=True)
class EcactusEcosSensorEntityDescription(SensorEntityDescription):
    """Class describing Airly sensor entities."""

    sensor_type: str = SENSOR_TYPE_RATE


SENSORS_INFO = [
    EcactusEcosSensorEntityDescription(
        translation_key="battery_soc",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_BATTERY_SOC)}",
        key=SOURCE_TYPE_BATTERY_SOC,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="battery_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_BATTERY_POWER)}",
        key=SOURCE_TYPE_BATTERY_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="eps_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_EPS_POWER)}",
        key=SOURCE_TYPE_EPS_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="grid_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_GRID_POWER)}",
        key=SOURCE_TYPE_GRID_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="home_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_HOME_POWER)}",
        key=SOURCE_TYPE_HOME_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="meter_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_METER_POWER)}",
        key=SOURCE_TYPE_METER_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    EcactusEcosSensorEntityDescription(
        translation_key="solar_power",
        sensor_type=SENSOR_TYPE_RATE,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        name=f"{DOMAIN}_{name_key(SOURCE_TYPE_SOLAR_POWER)}",
        key=SOURCE_TYPE_SOLAR_POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: DataUpdateCoordinator[dict[str, dict[str, Any]]] = hass.data[DOMAIN][
        config_entry.entry_id
    ][DATA_COORDINATOR]
    user_id = config_entry.data[CONF_ID]

    """The static Sensors """
    async_add_entities(
        EcactusEcosSensor(coordinator, user_id, description)
        for description in SENSORS_INFO
    )

    # """The dynamic Sensors"""
    # username = config_entry.data[CONF_USERNAME]
    # password = config_entry.data[CONF_PASSWORD]

    # ecactusecos = EcactusEcos(username, password)

    # # Attempt authentication. If this fails, an EcactusEcosException will be thrown
    # await ecactusecos.authenticate()

    # if ecactusecos.is_authenticated():
    #     async_add_entities(
    #         EcactusEcosSensor(coordinator, user_id, description)
    #         for description in SENSORS_INFO
    #     )


class EcactusEcosSensor(
    CoordinatorEntity[DataUpdateCoordinator[dict[str, dict[str, Any]]]], SensorEntity
):
    """Defines a EcactusEcos sensor."""

    entity_description: EcactusEcosSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[dict[str, dict[str, Any]]],
        user_id: str,
        description: EcactusEcosSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._source_type = description.key
        self._sensor_type = description.sensor_type
        self._attr_unique_id = (
            f"{DOMAIN}_{user_id}_{description.key}_{description.sensor_type}"
        )

    @property
    def native_value(self) -> int | float | None:
        """Return the state of the sensor."""
        if (
            data := self.coordinator.data[self.entity_description.key][
                self.entity_description.sensor_type
            ]
        ) is not None:
            return data
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return bool(
            super().available
            and self.coordinator.data
            and self._source_type in self.coordinator.data
            and self.coordinator.data[self._source_type]
        )
