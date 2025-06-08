import asyncio
import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .cmv import HeltyCMV

_LOGGER = logging.getLogger(__name__)


class HeltyDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator per gestire il polling dei dati dal dispositivo Helty."""

    def __init__(self, hass, device: HeltyCMV):
        """Inizializza il coordinator."""
        self.device = device
        super().__init__(
            hass,
            _LOGGER,
            name=f"Helty {device.name}",
            update_interval=timedelta(seconds=60),  # Polling ogni 60 secondi
        )

    async def _async_update_data(self):
        """Funzione che esegue il polling."""
        try:
            (
                op_status,
                indoor_temp,
                outdoor_temp,
                indoor_humidity,
                leds_on,
            ) = await asyncio.gather(
                self.device.get_cmv_op_status(),
                self.device.get_cmv_indoor_air_temperature(),
                self.device.get_cmv_outdoor_air_temperature(),
                self.device.get_cmv_indoor_humidity(),
                self.device.are_cmv_leds_on(),
            )
            # Combina tutti i risultati in un unico dizionario
            data = {
                "op_status": op_status,
                "indoor_temp": indoor_temp,
                "outdoor_temp": outdoor_temp,
                "indoor_humidity": indoor_humidity,
                "leds_on": leds_on,
            }
            # Unisci anche i dati di op_status se presenti
            if op_status:
                data.update(op_status)

            return data
        except ConnectionError as err:
            raise UpdateFailed(f"Errore di comunicazione con Helty: {err}")