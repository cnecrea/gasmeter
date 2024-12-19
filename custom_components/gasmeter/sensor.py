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
    
    # Obținem entity_id-urile din options
    gas_pcs_entity = entry.options.get("gas_pcs_entity", "input_number.gas_pcs")
    price_per_kwh_entity = entry.options.get("price_per_kwh_entity", "input_number.price_per_kwh")
    gas_meter_reading_entity = entry.options.get("gas_meter_reading_entity", "input_number.gas_meter_reading")

    # Adăugăm senzorii
    async_add_entities([
        GasMeterPriceSensor(hass, entry, gas_pcs_entity, price_per_kwh_entity),
        GasMeterConsumptionSensor(hass, entry, gas_meter_reading_entity, gas_pcs_entity),
    ], True)
    _LOGGER.debug("Gas Meter sensors added successfully")


class GasMeterPriceSensor(SensorEntity):
    """Representation of the Gas Meter Price Sensor."""

    def __init__(self, hass, entry, gas_pcs_entity, price_per_kwh_entity):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Preț pe m³"
        self._attr_unique_id = f"{entry.entry_id}_price_per_m3"
        self._state = None
        self._entry = entry
        self._gas_pcs_entity = gas_pcs_entity
        self._price_per_kwh_entity = price_per_kwh_entity
        self._gas_pcs = 0.0
        self._price_per_kwh = 0.0

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        _LOGGER.debug("Gas Meter Price Sensor added to hass")
        self._update_values()

        async_track_state_change_event(
            self.hass,
            [self._gas_pcs_entity, self._price_per_kwh_entity],
            self._handle_state_change,
        )

    @callback
    def _handle_state_change(self, event):
        """Handle state changes of input_number entities."""
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id == self._gas_pcs_entity and new_state:
            self._gas_pcs = float(new_state.state)
            _LOGGER.debug("Updated gas_pcs to: %s", self._gas_pcs)

        elif entity_id == self._price_per_kwh_entity and new_state:
            self._price_per_kwh = float(new_state.state)
            _LOGGER.debug("Updated price_per_kwh to: %s", self._price_per_kwh)

        self._calculate_state()
        self.async_write_ha_state()

    def _update_values(self):
        """Update initial values."""
        gas_pcs_state = self.hass.states.get("input_number.gas_pcs")
        price_per_kwh_state = self.hass.states.get("input_number.price_per_kwh")

        if gas_pcs_state and gas_pcs_state.state not in (None, "unknown", "unavailable"):
            self._gas_pcs = float(gas_pcs_state.state)
        else:
            self._gas_pcs = self._entry.options.get("gas_pcs", self._entry.data.get("gas_pcs", 0.0))

        if price_per_kwh_state and price_per_kwh_state.state not in (None, "unknown", "unavailable"):
            self._price_per_kwh = float(price_per_kwh_state.state)
        else:
            self._price_per_kwh = self._entry.options.get("price_per_kwh", self._entry.data.get("price_per_kwh", 0.2910))

        _LOGGER.debug(
            "Initialized values for Preț pe m³: gas_pcs=%s, price_per_kwh=%s", 
            self._gas_pcs, 
            self._price_per_kwh
        )
        self._calculate_state()

    def _calculate_state(self):
        """Calculate the state of the sensor."""
        try:
            _LOGGER.debug(
                "Calculating Preț pe m³ with gas_pcs=%s and price_per_kwh=%s", 
                self._gas_pcs, 
                self._price_per_kwh
            )
            self._state = round(self._gas_pcs * self._price_per_kwh, 2)
            _LOGGER.debug("Calculated sensor state (Preț pe m³): %s", self._state)
        except Exception as e:
            _LOGGER.error("Error calculating sensor state: %s", e)
            self._state = None

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "RON/m³"

    @property
    def icon(self):
        return "mdi:cube"


class GasMeterConsumptionSensor(SensorEntity):
    """Representation of the Gas Meter Consumption Sensor."""

    def __init__(self, hass, entry, gas_meter_reading_entity, gas_pcs_entity):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = "Consum în kWh"
        self._attr_unique_id = f"{entry.entry_id}_consumption_kwh"
        self._state = None
        self._entry = entry
        self._gas_meter_reading_entity = gas_meter_reading_entity
        self._gas_pcs_entity = gas_pcs_entity
        self._gas_meter_reading = 0.0
        self._gas_pcs = 0.0

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        _LOGGER.debug("Gas Meter Consumption Sensor added to hass")
        self._update_values()

        async_track_state_change_event(
            self.hass,
            [self._gas_meter_reading_entity, self._gas_pcs_entity],
            self._handle_state_change,
        )

    @callback
    def _handle_state_change(self, event):
        entity_id = event.data.get("entity_id")
        new_state = event.data.get("new_state")

        if entity_id == self._gas_meter_reading_entity and new_state:
            self._gas_meter_reading = float(new_state.state)

        elif entity_id == self._gas_pcs_entity and new_state:
            self._gas_pcs = float(new_state.state)

        self._calculate_state()
        self.async_write_ha_state()

    def _update_values(self):
        gas_meter_reading_state = self.hass.states.get(self._gas_meter_reading_entity)
        gas_pcs_state = self.hass.states.get(self._gas_pcs_entity)

        self._gas_meter_reading = float(gas_meter_reading_state.state) if gas_meter_reading_state else 0.0
        self._gas_pcs = float(gas_pcs_state.state) if gas_pcs_state else 0.0

        self._calculate_state()

    def _calculate_state(self):
        try:
            self._state = round(self._gas_meter_reading * self._gas_pcs, 3)
        except Exception as e:
            _LOGGER.error("Error calculating consumption state: %s", e)
            self._state = None

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "kWh"

    @property
    def icon(self):
        return "mdi:gas-burner"
