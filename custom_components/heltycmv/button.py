from __future__ import annotations
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeltyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator: HeltyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HeltyCMVResetFilter(coordinator)], True)


class HeltyCMVResetFilter(CoordinatorEntity, ButtonEntity):

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        super().__init__(coordinator)
        self._cmv = coordinator.device
        self._attr_unique_id = f"{self._cmv.cmv_id}_filter_reset"
        self._attr_name = f"{self._cmv.name} CMV Filter Usage Reset"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._cmv.cmv_id)},
            name=self._cmv.name,
            manufacturer="Helty",
            model="Flow",
        )

    async def async_press(self) -> None:
        await self._cmv.reset_cmv_filters()