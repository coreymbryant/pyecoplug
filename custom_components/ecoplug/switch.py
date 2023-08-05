from __future__ import annotations

import logging

import homeassistant.helpers.config_validation as cv

from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.const import CONF_NAME, CONF_MAC, CONF_IP_ADDRESS, CONF_PORT
from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.helpers.device_registry import format_mac

import voluptuous as vol

from pyecoplug import EcoPlug
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=5)
DEFAULT_NAME = "EcoPlug - Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_MAC): cv.string,
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_PORT): cv.string,
    vol.Required(CONF_NAME): cv.string,
    })

def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None,
        ) -> None:
    """Set up the switch platform."""
    # Version # (e.g. '1.7.1')
    #data[1]
    version = '1.7.1'.encode()
    # Name
    name = config[CONF_NAME].encode()
    # Partial Mac (e.g. '780C44F0')
    mac_addr = config[CONF_MAC].encode()
    # unique ID - Partial MAC (e.g. 'ECO-780C44F0')
    unique_id = ('ECO-'+config[CONF_MAC]).encode()
    # IP Address ('10.8.70.77')
    ip_addr = config[CONF_IP_ADDRESS]
    # Port (e.g. 80)
    port = int(config[CONF_PORT])

    data=[0]
    data.append(version)
    data.append(unique_id)
    data.append(name)
    data.append(mac_addr)
    data.append(ip_addr)
    data.append(port)

    add_entities([EcoPlugSwitch(data)])

class EcoPlugSwitch(SwitchEntity):
    """Representation of a sensor"""
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self,data) -> None:
        super().__init__()
        self._plug = EcoPlug(data)
        self._name = self._plug.name
        self._is_on = self._plug.is_on()
        self._attr_name = self._plug.name
        self._attr_unique_id = format_mac(data[4].decode())


    @property
    def should_poll(self):
        return True

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._is_on

    def turn_on(self):
        self._plug.turn_on()
        self.update()

    def turn_off(self):
        self._plug.turn_off()
        self.update()

    def update(self):
        _LOGGER.info('update')
        self._is_on = self._plug.is_on()


