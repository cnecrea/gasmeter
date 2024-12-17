from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
import logging

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gas Meter integration from a config entry."""
    _LOGGER.debug("Setting up Gas Meter integration")

    # Adăugăm funcția de sincronizare în hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = GasMeterData(hass, entry)

    # Sincronizăm valorile ConfigEntry.options cu input_number
    await hass.data[DOMAIN][entry.entry_id].sync_config_to_input_number()

    # Ascultăm modificările input_number
    async_setup_listeners(hass, entry)

    # Forwardăm platforma 'sensor'
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    _LOGGER.debug("Gas Meter integration setup complete")
    return True

class GasMeterData:
    """Handle data management for Gas Meter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        self.hass = hass
        self.entry = entry

    async def sync_config_to_input_number(self):
        """Sync ConfigEntry options to input_number entities."""
        _LOGGER.debug("Starting sync_config_to_input_number for Gas Meter integration")

        # Preluăm valorile din ConfigEntry.options (fallback la ConfigEntry.data)
        gas_meter_reading = self.entry.options.get("gas_meter_reading", self.entry.data.get("gas_meter_reading", 0.0))
        gas_pcs = self.entry.options.get("gas_pcs", self.entry.data.get("gas_pcs", 0.0))
        price_per_kwh = self.entry.options.get("price_per_kwh", self.entry.data.get("price_per_kwh", 0.2910))

        # Actualizăm input_number entities
        await self._set_input_number_value("input_number.gas_meter_reading", gas_meter_reading)
        _LOGGER.debug("Synced input_number.gas_meter_reading to %s", gas_meter_reading)

        await self._set_input_number_value("input_number.gas_pcs", gas_pcs)
        _LOGGER.debug("Synced input_number.gas_pcs to %s", gas_pcs)

        await self._set_input_number_value("input_number.price_per_kwh", price_per_kwh)
        _LOGGER.debug("Synced input_number.price_per_kwh to %s", price_per_kwh)

        _LOGGER.info(
            "Sync completed: gas_meter_reading=%s, gas_pcs=%s, price_per_kwh=%s",
            gas_meter_reading, gas_pcs, price_per_kwh
        )

    async def _set_input_number_value(self, entity_id, value):
        """Helper to set an input_number value."""
        if self.hass.states.get(entity_id):
            _LOGGER.debug("Setting %s to %s", entity_id, value)
            await self.hass.services.async_call(
                "input_number",
                "set_value",
                {"entity_id": entity_id, "value": value},
                blocking=True,
            )

def async_setup_listeners(hass: HomeAssistant, entry: ConfigEntry):
    """Set up listeners to track input_number changes."""

    @callback
    def state_change_listener(event):
        """Handle state changes of input_number entities."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id == "input_number.gas_meter_reading":
            new_value = float(new_state.state)
            _LOGGER.debug("input_number.gas_meter_reading changed to %s", new_value)
            update_config_entry(hass, entry, "gas_meter_reading", new_value)

        elif entity_id == "input_number.gas_pcs":
            new_value = float(new_state.state)
            _LOGGER.debug("input_number.gas_pcs changed to %s", new_value)
            update_config_entry(hass, entry, "gas_pcs", new_value)

        elif entity_id == "input_number.price_per_kwh":
            new_value = float(new_state.state)
            _LOGGER.debug("input_number.price_per_kwh changed to %s", new_value)
            update_config_entry(hass, entry, "price_per_kwh", new_value)

    async_track_state_change_event(
        hass,
        [
            "input_number.gas_meter_reading",
            "input_number.gas_pcs",
            "input_number.price_per_kwh",
        ],
        state_change_listener,
    )
    _LOGGER.debug("Listeners for input_number changes set up")


@callback
def update_config_entry(hass: HomeAssistant, entry: ConfigEntry, key: str, value: float):
    """Update ConfigEntry with the new value."""
    options = {**entry.options, key: value}
    hass.config_entries.async_update_entry(entry, options=options)
    _LOGGER.debug("Updated ConfigEntry options: %s = %s", key, value)
