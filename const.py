# type: ignore
"""Constants for the Ecactus Ecos integration."""

from ecactusecos.const import (
    SOURCE_TYPE_BATTERY_SOC,
    SOURCE_TYPE_BATTERY_POWER,
    SOURCE_TYPE_EPS_POWER,
    SOURCE_TYPE_GRID_POWER,
    SOURCE_TYPE_HOME_POWER,
    SOURCE_TYPE_METER_POWER,
    SOURCE_TYPE_SOLAR_POWER,
)

DATA_COORDINATOR = "coordinator"

DOMAIN = "ecactusecos"

"""Interval in seconds between polls to Ecactus Ecos, same as on cloud side to inverter."""
POLLING_INTERVAL = 10

"""Timeout for fetching sensor data"""
FETCH_TIMEOUT = 10

SENSOR_TYPE_RATE = "rate"

SOURCE_TYPES = [
    SOURCE_TYPE_BATTERY_SOC,
    SOURCE_TYPE_BATTERY_POWER,
    SOURCE_TYPE_EPS_POWER,
    SOURCE_TYPE_GRID_POWER,
    SOURCE_TYPE_HOME_POWER,
    SOURCE_TYPE_METER_POWER,
    SOURCE_TYPE_SOLAR_POWER,
]
