"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature

from .const import DOMAIN
from .coordinator import HeltyDataUpdateCoordinator


async def async_setup_entry(hass, config_entry, async_add_entities):
    # Ottieni il coordinator
    coordinator: HeltyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    # Aggiungi le entità passando il coordinator
    async_add_entities(
        [
            CMVIndoorTemperature(coordinator),
            CMVOutdoorTemperature(coordinator),
            CMVIndoorHumidity(coordinator),
        ],
        True,
    )


# La classe base ora eredita da CoordinatorEntity
class CMVBaseSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = False

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        """Inizializza il sensore base."""
        super().__init__(coordinator)
        self._cmv = coordinator.device

    @property
    def device_info(self):
        """Informazioni dispositivo."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._cmv.cmv_id)},
            name=self._cmv.name,
            manufacturer="Helty",
            model="Flow",
        )


class CMVIndoorTemperature(CMVBaseSensor):
    """Sensore di Temperatura Interna."""
    device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._cmv.cmv_id}_indoor_temp"
        self._attr_name = f"{self._cmv.name} Indoor Temperature"

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore dal coordinator."""
        # Leggi il valore direttamente dai dati del coordinator
        if self.coordinator.data:
            return self.coordinator.data.get("indoor_temp")
        return None


class CMVOutdoorTemperature(CMVBaseSensor):
    """Sensore di Temperatura Esterna."""
    device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._cmv.cmv_id}_outdoor_temp"
        self._attr_name = f"{self._cmv.name} Outdoor Temperature"

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore dal coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("outdoor_temp")
        return None

    # RIMUOVI il metodo async_update()


class CMVIndoorHumidity(CMVBaseSensor):
    """Sensore di Umidità Interna."""
    device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, coordinator: HeltyDataUpdateCoordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._cmv.cmv_id}_indoor_humidity"
        self._attr_name = f"{self._cmv.name} Indoor Humidity"

    @property
    def native_value(self) -> float | None:
        """Restituisce il valore dal coordinator."""
        if self.coordinator.data:
            return self.coordinator.data.get("indoor_humidity")
        return None

    # RIMUOVI il metodo async_update()