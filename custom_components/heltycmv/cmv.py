import asyncio
import logging
from .const import (
    NAME_CMD,
    SENSORS_CMD,
    CONFIG_GET_CMD,
    CMV_NAME_PREFIX,
    PRESET_BOOST,
    PRESET_NIGHT,
    PRESET_COOLING,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_HIGHEST,
    MODE_CMDS,
    LED_OFF_CMD,
    LED_ON_CMD,
    RESET_FILTER,
)

_LOGGER = logging.getLogger(__name__)


class HeltyCMV:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self.name = host
        self._id = host.lower()
        self.online = True

    @property
    def cmv_id(self) -> str:
        return self._id

    async def test_connection(self) -> bool:
        """Test connectivity to the Dummy hub is OK."""
        cmv_name = await self.get_cmv_name()
        if not cmv_name:
            return False
        return True

    async def _execute_cmv_cmd_async(self, cmd):
        """
        Versione asincrona che non blocca Home Assistant.
        Gestisce anche gli errori di connessione.
        """
        try:
            # Imposta un timeout per l'intera operazione
            async with asyncio.timeout(10):
                reader, writer = await asyncio.open_connection(self._host, self._port)

                writer.write(cmd)
                await writer.drain()

                data = await reader.read(1024)

                writer.close()
                await writer.wait_closed()

                # La connessione è andata a buon fine, quindi il dispositivo è online
                if not self.online:
                    _LOGGER.info("Dispositivo Helty %s è tornato online", self.name)
                    self.online = True

                return data.decode('ASCII').strip()

        except (asyncio.TimeoutError, ConnectionRefusedError, OSError) as e:
            # Se c'è un errore di rete, il dispositivo è offline
            if self.online:
                _LOGGER.warning("Impossibile connettersi a Helty %s: %s. Il dispositivo è offline.", self.name, e)
                self.online = False
            # Solleva un'eccezione che può essere gestita dai metodi chiamanti
            raise ConnectionError from e

    async def get_cmv_name(self):
        try:
            data = await self._execute_cmv_cmd_async(NAME_CMD)
            return data.removeprefix(CMV_NAME_PREFIX).strip()
        except ConnectionError:
            return None

    async def get_cmv_indoor_air_temperature(self):
        try:
            indoor_air_temp = None
            raw_data = await self._execute_cmv_cmd_async(SENSORS_CMD)
            data = raw_data.strip().split(',')
            if data[0] == "VMGI":
                indoor_air_temp = float(int(data[1]) / 10)
            return indoor_air_temp
        except (ConnectionError, IndexError, ValueError):
            return None

    async def get_cmv_outdoor_air_temperature(self):
        try:
            outdoor_air_temp = None
            raw_data = await self._execute_cmv_cmd_async(SENSORS_CMD)
            data = raw_data.strip().split(',')
            if data[0] == "VMGI":
                outdoor_air_temp = float(int(data[2]) / 10)
            return outdoor_air_temp
        except (ConnectionError, IndexError, ValueError):
            return None

    async def get_cmv_indoor_humidity(self):
        try:
            indoor_air_humidity = None
            raw_data = await self._execute_cmv_cmd_async(SENSORS_CMD)
            data = raw_data.strip().split(',')
            if data[0] == "VMGI":
                indoor_air_humidity = float(int(data[3]) / 10)
            return indoor_air_humidity
        except (ConnectionError, IndexError, ValueError):
            return None

    async def get_cmv_op_status(self):
        try:
            raw_data = await self._execute_cmv_cmd_async(CONFIG_GET_CMD)
            data = raw_data.strip().split(',')
            if data[0] == "VMGO":
                op_state_int = int(data[1])
                if op_state_int == 1:
                    return {"preset": None, "fan_mode": FAN_LOW}
                elif op_state_int == 2:
                    return {"preset": None, "fan_mode": FAN_MEDIUM}
                elif op_state_int == 3:
                    return {"preset": None, "fan_mode": FAN_HIGH}
                elif op_state_int == 4:
                    return {"preset": None, "fan_mode": FAN_HIGHEST}
                elif op_state_int == 5:
                    return {"preset": PRESET_BOOST, "fan_mode": None}
                elif op_state_int == 6:
                    return {"preset": PRESET_NIGHT, "fan_mode": None}
                elif op_state_int == 7:
                    return {"preset": PRESET_COOLING, "fan_mode": None}
                else:
                    return None
            return None
        except (ConnectionError, IndexError, ValueError) as e:
            _LOGGER.debug("Errore durante l'aggiornamento dello stato: %s", e)
            return None

    async def set_cmv_mode(self, mode):
        try:
            exec_result = await self._execute_cmv_cmd_async(MODE_CMDS.get(mode, NAME_CMD))
            return exec_result == "OK"
        except ConnectionError:
            return False

    async def are_cmv_leds_on(self):
        try:
            led_state_int = None
            raw_data = await self._execute_cmv_cmd_async(CONFIG_GET_CMD)
            data = raw_data.strip().split(',')
            if data[0] == "VMGO":
                led_state_int = int(data[2])
            if led_state_int == 10:
                return True
            elif led_state_int == 0:
                return False
            else:
                return None
        except (ConnectionError, IndexError, ValueError):
            return None

    async def turn_cmv_leds_off(self):
        exec_result = await self._execute_cmv_cmd_async(LED_OFF_CMD)
        if exec_result == "OK":
            return True
        return False

    async def turn_cmv_leds_on(self):
        exec_result = await self._execute_cmv_cmd_async(LED_ON_CMD)
        if exec_result == "OK":
            return True
        return False

    async def reset_cmv_filters(self):
        exec_result = await self._execute_cmv_cmd_async(RESET_FILTER)
        if exec_result == "OK":
            return True
        return False