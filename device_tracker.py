from datetime import timedelta
import logging
import asyncio
import voluptuous as vol

from homeassistant.components.device_tracker import PLATFORM_SCHEMA
from homeassistant.components.device_tracker.const import (
    CONF_SCAN_INTERVAL,
    SCAN_INTERVAL,
    SOURCE_TYPE_ROUTER,
)

from homeassistant import const, util
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_point_in_utc_time

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
interval = timedelta(minutes=5)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(const.CONF_HOSTS): {cv.slug: cv.string},
    }
)

async def async_setup_scanner(hass, config, async_see, discovery_info=None):
    """Set up the Host objects and return the update function."""
    
    async def async_update(now):
            if hass.data[DOMAIN] is None or hass.data[DOMAIN]["coordinator"] is None:
                _LOGGER.warn('Livebox not connected')
                return

            coordinator = hass.data[DOMAIN]["coordinator"]
            await asyncio.gather(
                *[
                    async_see(dev_id=dev_id, source_type=SOURCE_TYPE_ROUTER)
                    for dev_id, host in config[const.CONF_HOSTS].items()
                    if coordinator.data[host] is not None and coordinator.data[host]['Active']
                ]
            )

    async def _async_update_interval(now):
        try:
            await async_update(now)
        finally:
            if not hass.is_stopping:
                async_track_point_in_utc_time(
                    hass, _async_update_interval, util.dt.utcnow() + interval
                )

    await _async_update_interval(None)
    return True