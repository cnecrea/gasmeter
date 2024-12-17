from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Gas Meter sensors from a config entry."""
    _LOGGER.debug("Starting async_setup_entry for sensor platform")
    
    # Adăugăm ambele entități
    async_add_entities([
        GasMeterPriceSensor(hass, entry),
        GasMeterConsumptionSensor(hass, entry),  # Adăugăm Consum în kWh
    ], True)
    _LOGGER.debug("Gas Meter sensors added successfully")


class GasMeterPriceSensor(SensorEntity):
    """Representation of the Gas Meter Price Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Preț pe m³"
        self._attr_unique_id = f"{entry.entry_id}_price_per_m3"
        self._state = None
        self._entry = entry
        self._gas_pcs = 0.0
        self._price_per_kwh = 0.0

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        _LOGGER.debug("Gas Meter Price Sensor added to hass")
        self._update_values()

        # Ascultăm modificările input_number
        async_track_state_change_event(
            self.hass,
            ["input_number.gas_pcs", "input_number.price_per_kwh"],
            self._handle_state_change,
        )

    @callback
    def _handle_state_change(self, event):
        """Handle state changes of input_number entities."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id == "input_number.gas_pcs" and new_state:
            self._gas_pcs = float(new_state.state)
            _LOGGER.debug("Updated gas_pcs to: %s", self._gas_pcs)

        elif entity_id == "input_number.price_per_kwh" and new_state:
            self._price_per_kwh = float(new_state.state)
            _LOGGER.debug("Updated price_per_kwh to: %s", self._price_per_kwh)

        self._calculate_state()
        self.async_write_ha_state()

    def _update_values(self):
        """Update initial values."""
        gas_pcs_state = self.hass.states.get("input_number.gas_pcs")
        price_per_kwh_state = self.hass.states.get("input_number.price_per_kwh")

        self._gas_pcs = (
            float(gas_pcs_state.state) if gas_pcs_state and gas_pcs_state.state not in (None, "unknown", "unavailable")
            else self._entry.options.get("gas_pcs", self._entry.data.get("gas_pcs", 0.0))
        )
        self._price_per_kwh = (
            float(price_per_kwh_state.state) if price_per_kwh_state and price_per_kwh_state.state not in (None, "unknown", "unavailable")
            else self._entry.options.get("price_per_kwh", self._entry.data.get("price_per_kwh", 0.2910))
        )

        _LOGGER.debug(
            "Initialized values: gas_pcs=%s, price_per_kwh=%s", self._gas_pcs, self._price_per_kwh
        )
        self._calculate_state()

    def _calculate_state(self):
        """Calculate the state of the sensor."""
        try:
            self._state = round(self._gas_pcs * self._price_per_kwh, 2)
            _LOGGER.debug("Calculated sensor state: %s", self._state)
        except Exception as e:
            _LOGGER.error("Error calculating sensor state: %s", e)
            self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "RON/m³"

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return "mdi:gas-cylinder"


class GasMeterConsumptionSensor(SensorEntity):
    """Representation of the Gas Meter Consumption Sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Consum în kWh"
        self._attr_unique_id = f"{entry.entry_id}_consumption_kwh"
        self._state = None
        self._entry = entry
        self._gas_meter_reading = 0.0
        self._gas_pcs = 0.0

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        _LOGGER.debug("Gas Meter Consumption Sensor added to hass")
        self._update_values()

        # Ascultăm modificările input_number
        async_track_state_change_event(
            self.hass,
            ["input_number.gas_meter_reading", "input_number.gas_pcs"],
            self._handle_state_change,
        )

    @callback
    def _handle_state_change(self, event):
        """Handle state changes of input_number entities."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id == "input_number.gas_meter_reading" and new_state:
            self._gas_meter_reading = float(new_state.state)
            _LOGGER.debug("Updated gas_meter_reading to: %s", self._gas_meter_reading)

        elif entity_id == "input_number.gas_pcs" and new_state:
            self._gas_pcs = float(new_state.state)
            _LOGGER.debug("Updated gas_pcs to: %s", self._gas_pcs)

        self._calculate_state()
        self.async_write_ha_state()

    def _update_values(self):
        """Update initial values."""
        gas_meter_reading_state = self.hass.states.get("input_number.gas_meter_reading")
        gas_pcs_state = self.hass.states.get("input_number.gas_pcs")

        self._gas_meter_reading = (
            float(gas_meter_reading_state.state)
            if gas_meter_reading_state and gas_meter_reading_state.state not in ("unknown", "unavailable")
            else self._entry.options.get("gas_meter_reading", self._entry.data.get("gas_meter_reading", 0.0))
        )
        self._gas_pcs = (
            float(gas_pcs_state.state)
            if gas_pcs_state and gas_pcs_state.state not in ("unknown", "unavailable")
            else self._entry.options.get("gas_pcs", self._entry.data.get("gas_pcs", 0.0))
        )

        _LOGGER.debug("Initialized values: gas_meter_reading=%s, gas_pcs=%s", self._gas_meter_reading, self._gas_pcs)
        self._calculate_state()

    def _calculate_state(self):
        """Calculate the state of the sensor."""
        try:
            self._state = round(self._gas_meter_reading * self._gas_pcs, 3)
            _LOGGER.debug("Calculated sensor state: %s", self._state)
        except Exception as e:
            _LOGGER.error("Error calculating consumption state: %s", e)
            self._state = None

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "kWh"

    @property
    def icon(self):
        """Return the icon for the sensor."""
        return "mdi:gas-burner"
