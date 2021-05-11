from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    PLATFORM_SCHEMA,
    BinarySensorEntity,
)

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
import logging

from .const import DOMAIN
CONF_HOST = "host"
CONF_NAME = "name"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME): cv.string,
    }
)

DEFAULT_NAME = "Host"
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    """Set up the Ping Binary sensor."""
    host = config[CONF_HOST]
    name = config.get(CONF_NAME, f"{DEFAULT_NAME} {host}")
    _LOGGER.debug("Add livebox host {} ({})".format(host, name))

    if hass.data[DOMAIN] is None or hass.data[DOMAIN]["coordinator"] is None:
        _LOGGER.error("Host {} not configured. Livebox connection failed.".format(name))
        return

    async_add_entities(
        [LiveboxHostBinarySensor(hass.data[DOMAIN]["coordinator"], name, host)]
    )

class LiveboxHostBinarySensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, name: str, host: str) -> None:
        super().__init__(coordinator)
        self._name = name
        self._host = host
        self._available = False

    @property
    def name(self):
        return self._name


    @property
    def device_class(self) -> str:
        """Return the class of this sensor."""
        return DEVICE_CLASS_CONNECTIVITY

    @property
    def should_poll(self):
        return False

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None:
            return False

        if not self.coordinator.data[self._host]:
            _LOGGER.debug("Host {} not found.".format(self._host))
            return False
        _LOGGER.debug("Host {} active: {}".format(self._host, self.coordinator.data[self._host]['Active']))
        return self.coordinator.data[self._host]['Active']

