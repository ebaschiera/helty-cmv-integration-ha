from __future__ import annotations
from typing import Any
import logging

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    PRESET_BOOST,
    PRESET_NIGHT,
    PRESET_COOLING,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_HIGHEST,
    FAN_OFF,
    DOMAIN
)
from homeassistant.components.fan import FanEntity, FanEntityFeature
from .coordinator import HeltyDataUpdateCoordinator # Importa il nuovo coordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    # Ottieni il coordinator creato in __init__.py invece dell'oggetto cmv
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HeltyCMVFan(coordinator)], True)


# Eredita da CoordinatorEntity invece che solo da FanEntity
class HeltyCMVFan(CoordinatorEntity, FanEntity):
    _attr_preset_modes = [
        PRESET_BOOST,
        PRESET_NIGHT,
        PRESET_COOLING
        ]
    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
    _attr_speed_count = 4

    _attr_has_entity_name = False

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        # Il costruttore ora riceve il coordinator
        super().__init__(coordinator)
        self._cmv = coordinator.device # Accediamo al dispositivo tramite il coordinator
        self._attr_unique_id = f"{self._cmv.cmv_id}_cmv_control"
        self._attr_name = f"{self._cmv.name} CMV Control"

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self._cmv.cmv_id)},
            name=self._cmv.name,
            manufacturer="Helty",
            model="Flow",
        )

    # La proprietà 'available' è ora GESTITA IN AUTOMATICO da CoordinatorEntity!
    # Non è più necessario definirla. Sarà True se l'ultimo aggiornamento
    # del coordinator è andato a buon fine.

    @property
    def is_on(self) -> bool | None:
        """Determina se la ventola è accesa basandosi sui dati del coordinator."""
        return (self.percentage is not None and self.percentage > 0) or (self.preset_mode is not None)

    @property
    def percentage(self) -> int | None:
        """Ottiene la velocità dai dati del coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("fan_mode")
        return None

    @property
    def preset_mode(self) -> str | None:
        """Ottiene il preset dai dati del coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("preset")
        return None

    # I metodi `async_set` rimangono simili, ma chiamano direttamente il dispositivo
    # e poi forzano un refresh del coordinator per aggiornare subito lo stato.
    async def async_set_percentage(self, percentage: int) -> None:
        if await self._cmv.set_cmv_mode(percentage):
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Impossibile impostare la percentuale a %s", percentage)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if await self._cmv.set_cmv_mode(preset_mode):
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Impossibile impostare il preset a %s", preset_mode)

    async def async_turn_off(self, **kwargs: Any) -> None:
        if await self._cmv.set_cmv_mode(FAN_OFF):
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Impossibile spegnere la ventola")

    async def async_turn_on(self, percentage=None, preset_mode=None, **kwargs: Any) -> None:
        if await self._cmv.set_cmv_mode(FAN_LOW):
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Impossibile accendere la ventola")

    # RIMUOVERE il metodo async_update()!
    # Il suo lavoro è ora svolto dal _async_update_data nel coordinator.