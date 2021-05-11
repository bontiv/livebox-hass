__requires__ = ["sysbus"]

from .const import DOMAIN, PLATFORMS
from datetime import timedelta
import logging
from homeassistant.helpers.reload import async_setup_reload_service
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    conf = config.get(DOMAIN)

    if conf:
        from sysbus import sysbus
        
        password = config[DOMAIN].get("password")
        if password is not None:
            sysbus.PASSWORD_LIVEBOX = password

        hostname = config[DOMAIN].get("host")
        if hostname is not None:
            sysbus.URL_LIVEBOX = "http://{}/".format(hostname)

        if sysbus.auth():
            async def async_update_data():
                result = sysbus.requete("Hosts.Host:get")
                if not result:
                    raise UpdateFailed()
                
                hosts = dict()
                for _, host in result['status'].items():
                    _LOGGER.debug("Found host {} {}".format(host['HostName'], "alive" if host['Active'] else "offline"))
                    hosts[host['HostName']] = host
                return hosts

            coordinator = DataUpdateCoordinator(
                    hass,
                    _LOGGER,
                    name="Livebox Host",
                    update_method=async_update_data,
                    update_interval=timedelta(minutes=5),
                )
            hass.data[DOMAIN] = {
                'password': password,
                'hostname': hostname,
                'coordinator': coordinator
            }
            _LOGGER.debug("Authentication success")
            await coordinator.async_refresh()
            await async_setup_reload_service(hass, DOMAIN, PLATFORMS)
        else:
            _LOGGER.error("Authentication error with {} on {}".format(PASSWORD_LIVEBOX, URL_LIVEBOX))

    return True

