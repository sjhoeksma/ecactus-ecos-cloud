# type: ignore
"""The Ecactus Ecos integration."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from ecactusecos import EcactusEcos, EcactusEcosException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    FETCH_TIMEOUT,
    POLLING_INTERVAL,
    SENSOR_TYPE_RATE,
    SOURCE_TYPES,
)

from ecactusecos.const import (
    DEVICE_ALIAS_NAME,
)

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ecactus Ecos  from a config entry."""
    # Create the EcactusEcos client
    ecactusecos = EcactusEcos(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        api_host=entry.data[CONF_HOST],
        source_types=SOURCE_TYPES,
        request_timeout=FETCH_TIMEOUT,
    )

    # Attempt authentication. If this fails, an exception is thrown
    try:
        await ecactusecos.authenticate()
    except EcactusEcosException as exception:
        _LOGGER.error("Authentication failed: %s", str(exception))
        return False

    async def async_update_data() -> dict[str, dict[str, Any]]:
        return await async_update_ecactusecos(ecactusecos)

    # Create a coordinator for polling updates
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=POLLING_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    # Load the client in the data of home assistant
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {DATA_COORDINATOR: coordinator}

    # Offload the loading of entities to the platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Forward the unloading of the entry to the platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    # If successful, unload the client
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_ecactusecos(
    ecactusecos: EcactusEcos,
) -> dict[str, dict[str, Any]]:
    """Update the data by performing a request to EcactusEcos."""
    try:
        # Note: TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with asyncio.timeout(FETCH_TIMEOUT):
            if not ecactusecos.is_authenticated():
                _LOGGER.warning("ecactusecos is unauthenticated. Reauthenticating")
                await ecactusecos.authenticate()

            current_measurements = await ecactusecos.current_measurements()
            # The base types
            result = {
                source_type: {
                    SENSOR_TYPE_RATE: _get_measurement_rate(
                        current_measurements, source_type
                    ),
                }
                for source_type in SOURCE_TYPES
            }
            await ecactusecos.device_overview()
            for deviceId, device in ecactusecos._devices.items():
                for source_type in SOURCE_TYPES:
                    if device[DEVICE_ALIAS_NAME] is not None:
                        key = f"{device[DEVICE_ALIAS_NAME].lower()}{source_type[:1].upper() + source_type[1:]}"
                        result[key] = {
                            SENSOR_TYPE_RATE: _get_measurement_rate(
                                current_measurements, key
                            )
                        }
            return result
    except EcactusEcosException as exception:
        raise UpdateFailed(f"Error communicating with API: {exception}") from exception


def _get_measurement_rate(current_measurements: dict, source_type: str):
    if source_type in current_measurements:
        return current_measurements[source_type]
    else:
        _LOGGER.error(
            "Source type %s not present in %s", source_type, current_measurements
        )
    return None
