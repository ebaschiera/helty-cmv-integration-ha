from __future__ import annotations
from typing import Any
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HeltyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator: HeltyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HeltyCMVLeds(coordinator)], True)


class HeltyCMVLeds(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        """Inizializza lo switch."""
        super().__init__(coordinator)
        self._cmv = coordinator.device
        self._attr_unique_id = f"{self._cmv.cmv_id}_panel_leds"
        self._attr_name = f"{self._cmv.name} CMV Panel Leds"

    @property
    def device_info(self):
        """Informazioni dispositivo."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._cmv.cmv_id)},
            name=self._cmv.name,
            manufacturer="Helty",
            model="Flow",
        )

    # La proprietà 'available' è gestita da CoordinatorEntity.

    @property
    def is_on(self) -> bool | None:
        """Restituisce lo stato (on/off) dai dati del coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("leds_on")
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Accende i LED."""
        await self._cmv.turn_cmv_leds_on()
        # Richiede un aggiornamento immediato per riflettere il nuovo stato
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Spegne i LED."""
        await self._cmv.turn_cmv_leds_off()
        # Richiede un aggiornamento immediato per riflettere il nuovo stato
        await self.coordinator.async_request_refresh()

    # RIMUOVI il metodo async_update()