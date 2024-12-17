from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)

class GasMeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gas Meter."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration step."""
        _LOGGER.debug("Starting user configuration flow")
        errors = {}

        if user_input is not None:
            try:
                gas_meter_reading = float(user_input["gas_meter_reading"])
                gas_pcs = float(user_input["gas_pcs"])
                price_per_kwh = float(user_input["price_per_kwh"])

                if any(v < 0 for v in [gas_meter_reading, gas_pcs, price_per_kwh]):
                    raise ValueError("Values must be positive")

                _LOGGER.debug(
                    "User input valid: gas_meter_reading=%s, gas_pcs=%s, price_per_kwh=%s",
                    gas_meter_reading, gas_pcs, price_per_kwh,
                )

                return self.async_create_entry(
                    title="GasMeter Pro",
                    data={
                        "gas_meter_reading": gas_meter_reading,
                        "gas_pcs": gas_pcs,
                        "price_per_kwh": price_per_kwh,
                    },
                    options={
                        "gas_meter_reading_entity": "input_number.gas_meter_reading",
                        "gas_pcs_entity": "input_number.gas_pcs",
                        "price_per_kwh_entity": "input_number.price_per_kwh",
                    }
                )
            except ValueError:
                errors["base"] = "invalid_number"
                _LOGGER.error("Invalid number entered by user: %s", user_input)

        data_schema = vol.Schema({
            vol.Required("gas_meter_reading", default=0.0): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required("gas_pcs", default=0.0): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required("price_per_kwh", default=0.2910): vol.All(vol.Coerce(float), vol.Range(min=0)),
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return GasMeterOptionsFlowHandler(config_entry)


class GasMeterOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow handler for Gas Meter."""

    def __init__(self, config_entry):
        """Initialize the options flow handler."""
        self._entry_id = config_entry.entry_id  # Stocăm doar entry_id, nu întregul config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the Gas Meter integration."""
        errors = {}

        # Obținem config_entry folosind entry_id
        config_entry = self.hass.config_entries.async_get_entry(self._entry_id)

        # Preluăm friendly_name pentru input_number
        gas_meter_reading_name = self._get_friendly_name("input_number.gas_meter_reading", "Corecție index contor")
        gas_pcs_name = self._get_friendly_name("input_number.gas_pcs", "Puterea calorifică")
        price_per_kwh_name = self._get_friendly_name("input_number.price_per_kwh", "Preț pe kWh")

        # Citim valorile actuale
        gas_meter_reading = await self._get_current_input_value("input_number.gas_meter_reading")
        gas_pcs = await self._get_current_input_value("input_number.gas_pcs")
        price_per_kwh = config_entry.options.get("price_per_kwh", 0.2910)

        if user_input is not None:
            try:
                gas_meter_reading = float(user_input[gas_meter_reading_name])
                gas_pcs = float(user_input[gas_pcs_name])
                price_per_kwh = float(user_input[price_per_kwh_name])

                if any(v < 0 for v in [gas_meter_reading, gas_pcs, price_per_kwh]):
                    raise ValueError("Values must be positive")

                _LOGGER.debug(
                    "Options updated: gas_meter_reading=%s, gas_pcs=%s, price_per_kwh=%s",
                    gas_meter_reading, gas_pcs, price_per_kwh,
                )

                # Actualizăm ConfigEntry.options
                self.hass.config_entries.async_update_entry(
                    config_entry,
                    options={
                        "gas_meter_reading": gas_meter_reading,
                        "gas_pcs": gas_pcs,
                        "price_per_kwh": price_per_kwh,
                    },
                )

                # Sincronizăm direct input_number imediat
                await self.hass.data[DOMAIN][self._entry_id].sync_config_to_input_number()

                return self.async_create_entry(title="", data={})

            except ValueError:
                errors["base"] = "invalid_number"
                _LOGGER.error("Invalid number entered in options flow: %s", user_input)

        # Afișăm formularul cu nume user-friendly și valori curente
        data_schema = vol.Schema({
            vol.Required(gas_meter_reading_name, default=gas_meter_reading): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required(gas_pcs_name, default=gas_pcs): vol.All(vol.Coerce(float), vol.Range(min=0)),
            vol.Required(price_per_kwh_name, default=price_per_kwh): vol.All(vol.Coerce(float), vol.Range(min=0)),
        })

        return self.async_show_form(step_id="init", data_schema=data_schema, errors=errors)

    def _get_friendly_name(self, entity_id, default_name):
        """Retrieve the friendly name for an entity."""
        state = self.hass.states.get(entity_id)
        if state and "friendly_name" in state.attributes:
            return state.attributes["friendly_name"]
        return default_name

    async def _get_current_input_value(self, entity_id):
        """Helper to get the current state of an input_number entity."""
        state = self.hass.states.get(entity_id)
        if state and state.state not in (None, "unknown", "unavailable"):
            _LOGGER.debug("Fetched current value for %s: %s", entity_id, state.state)
            return float(state.state)

        # Fallback la ConfigEntry.options
        config_entry = self.hass.config_entries.async_get_entry(self._entry_id)
        fallback = config_entry.options.get(entity_id.split(".")[-1], 0.0)
        return fallback
