# 📊 GasMeter Pro Integration for Home Assistant

**GasMeter Pro** is a custom integration for [Home Assistant](https://www.home-assistant.io/), designed to monitor gas consumption and calculate costs dynamically based on user input.

---

## 🔧 Features

✅ Real-time calculation of gas price and consumption.  
✅ Provides two sensors:
   - **`sensor.pret_pe_m3`**: Gas price per cubic meter (RON/m³).  
   - **`sensor.consum_in_kwh`**: Gas consumption in kilowatt-hours (kWh).  

✅ Configurable directly through the Home Assistant UI.  
✅ Syncs with `input_number` entities for manual overrides.

---

## 📋 Requirements

1. **Home Assistant** (2023.12 or higher).  
2. Manual configuration of `input_number` entities.

---

## ⚙️ Configuration

### Step 1: Add `input_number` to `configuration.yaml`

```yaml
input_number:
  gas_meter_reading:
    name: Corrected Meter Index
    min: 0
    max: 999999
    step: 0.001
    unit_of_measurement: "m³"
    mode: box

  gas_pcs:
    name: Calorific Value (PCS)
    min: 0
    max: 999999
    step: 0.001
    unit_of_measurement: "pcs"
    mode: box
```
Or include them in a separate file:
```yaml
input_number: !include includes/input_numbers.yaml
```

## 🚀 Step 2: Install GasMeter Pro Integration

### A. Via HACS (Home Assistant Community Store)

1. Go to **HACS** > **Integrations**.
2. Click the three-dot menu in the top right and select **Custom Repositories**.
3. Add this repository's URL (`https://github.com/cnecrea/gasmeter`) as a custom repository.
4. Search for `GasMeter Pro` and click **Download**.
5. Restart Home Assistant after installation.

### B. Manual Installation

1. Download this repository as a ZIP file.
2. Extract the contents and copy the folder `gasmeter` into:  
   `config/custom_components/`.
3. Restart Home Assistant after installation.

## 📊 Sensors Provided

The following sensors are automatically created by the GasMeter Pro integration:

Gas Price per Cubic Meter

```yaml
sensor:
  - platform: gasmeter
    name: Gas Meter Price per m³
    unique_id: pret_pe_m3
    icon: mdi:gas-cylinder
```
Gas Consumption in kWh
```yaml
sensor:
  - platform: gasmeter
    name: Gas Consumption in kWh
    unique_id: gas_meter_consum_in_kwh
    icon: mdi:gas-burner
```
## 🛠️ Usage

To display these sensors in a Lovelace dashboard, add the following YAML configuration:
```yaml
type: entities
title: GasMeter Pro
entities:
  - entity: sensor.pret_pe_m3
    name: Gas Price per Cubic Meter
  - entity: sensor.gas_meter_consum_in_kwh
    name: Gas Consumption in kWh
  - entity: input_number.gas_meter_reading
    name: Corrected Meter Index
  - entity: input_number.gas_pcs
    name: Calorific Value (PCS)
```

## 🔑 Key Points
- The integration synchronizes between ConfigEntry and input_number.
- Values updated manually in UI (input_number) are reflected automatically in the sensors.
- Restarting Home Assistant does not reset values.

 ## 🧑‍💻 Contributions

Contributions are welcome! Feel free to submit a pull request or report issues [here](https://github.com/cnecrea/gasmeter/issues).

## 🌟 Support
- If you like this integration, give it a ⭐ on [GitHub](https://github.com/cnecrea/smsto/)! 😊
