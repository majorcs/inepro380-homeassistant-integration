"""Entity descriptions for inepro380 sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.helpers.entity import EntityCategory

from .decoder import (
    decode_ascii_word,
    decode_float_abcd,
    decode_hex16,
    decode_hex32,
    decode_signed_int16,
    decode_uint16,
    format_version,
)

REACTIVE_POWER_DEVICE_CLASS = getattr(SensorDeviceClass, "REACTIVE_POWER", None)
APPARENT_POWER_DEVICE_CLASS = getattr(SensorDeviceClass, "APPARENT_POWER", None)
REACTIVE_ENERGY_DEVICE_CLASS = getattr(SensorDeviceClass, "REACTIVE_ENERGY", None)
POWER_FACTOR_DEVICE_CLASS = getattr(SensorDeviceClass, "POWER_FACTOR", None)

DecoderType = Callable[[list[int]], Any]


@dataclass(frozen=True, kw_only=True)
class IneproSensorDescription(SensorEntityDescription):
    """Describe a PRO380-backed Home Assistant sensor."""

    address: int
    register_count: int
    decoder: DecoderType


def _diagnostic(
    *,
    key: str,
    name: str,
    address: int,
    register_count: int,
    decoder: DecoderType,
    native_unit_of_measurement: str | None = None,
    icon: str | None = None,
) -> IneproSensorDescription:
    return IneproSensorDescription(
        key=key,
        name=name,
        address=address,
        register_count=register_count,
        decoder=decoder,
        native_unit_of_measurement=native_unit_of_measurement,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        icon=icon,
    )


def _measurement(
    *,
    key: str,
    name: str,
    address: int,
    native_unit_of_measurement: str | None,
    device_class: SensorDeviceClass | str | None = None,
) -> IneproSensorDescription:
    return IneproSensorDescription(
        key=key,
        name=name,
        address=address,
        register_count=2,
        decoder=decode_float_abcd,
        native_unit_of_measurement=native_unit_of_measurement,
        device_class=device_class,
        state_class=SensorStateClass.MEASUREMENT,
    )


def _total(
    *,
    key: str,
    name: str,
    address: int,
    native_unit_of_measurement: str,
    device_class: SensorDeviceClass | str | None,
    state_class: SensorStateClass = SensorStateClass.TOTAL,
    enabled_default: bool = True,
) -> IneproSensorDescription:
    return IneproSensorDescription(
        key=key,
        name=name,
        address=address,
        register_count=2,
        decoder=decode_float_abcd,
        native_unit_of_measurement=native_unit_of_measurement,
        device_class=device_class,
        state_class=state_class,
        entity_registry_enabled_default=enabled_default,
    )


IDENTITY_SENSORS: tuple[IneproSensorDescription, ...] = (
    _diagnostic(key="serial_number", name="Serial number", address=0x4000, register_count=2, decoder=decode_hex32),
    _diagnostic(key="meter_code", name="Meter code", address=0x4002, register_count=1, decoder=decode_hex16),
    _diagnostic(key="modbus_id", name="Modbus ID", address=0x4003, register_count=1, decoder=decode_uint16),
    _diagnostic(key="baud_rate", name="Baud rate", address=0x4004, register_count=1, decoder=decode_uint16),
    _diagnostic(key="protocol_version", name="Protocol version", address=0x4005, register_count=2, decoder=format_version),
    _diagnostic(key="software_version", name="Software version", address=0x4007, register_count=2, decoder=format_version),
    _diagnostic(key="hardware_version", name="Hardware version", address=0x4009, register_count=2, decoder=format_version),
    _diagnostic(key="device_current_rating", name="Meter amps", address=0x400B, register_count=1, decoder=decode_uint16, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE)),
    _diagnostic(key="current_transformer_ratio", name="CT ratio", address=0x400C, register_count=1, decoder=decode_uint16, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE)),
    _diagnostic(key="s0_pulse_ratio", name="S0 output rate", address=0x400D, register_count=2, decoder=decode_float_abcd, native_unit_of_measurement="imp/kWh"),
    _diagnostic(key="combination_code", name="Combination code", address=0x400F, register_count=1, decoder=decode_uint16),
    _diagnostic(key="lcd_cycle_time", name="LCD cycle time", address=0x4010, register_count=1, decoder=decode_uint16, native_unit_of_measurement="s"),
    _diagnostic(key="parity_setting", name="Parity setting", address=0x4011, register_count=1, decoder=decode_uint16),
    _diagnostic(key="current_direction", name="Current direction", address=0x4012, register_count=1, decoder=decode_ascii_word),
    _diagnostic(key="l2_current_direction", name="L2 current direction", address=0x4013, register_count=1, decoder=decode_ascii_word),
    _diagnostic(key="l3_current_direction", name="L3 current direction", address=0x4014, register_count=1, decoder=decode_ascii_word),
    _diagnostic(key="error_code", name="Error code", address=0x4015, register_count=1, decoder=decode_signed_int16),
    _diagnostic(key="disconnect_counter", name="Power down counter", address=0x4016, register_count=1, decoder=decode_uint16),
    _diagnostic(key="quadrant", name="Present quadrant", address=0x4017, register_count=1, decoder=decode_uint16),
    _diagnostic(key="l1_quadrant", name="L1 Quadrant", address=0x4018, register_count=1, decoder=decode_uint16),
    _diagnostic(key="l2_quadrant", name="L2 Quadrant", address=0x4019, register_count=1, decoder=decode_uint16),
    _diagnostic(key="l3_quadrant", name="L3 Quadrant", address=0x401A, register_count=1, decoder=decode_uint16),
    _diagnostic(key="checksum", name="Checksum", address=0x401B, register_count=2, decoder=decode_hex32),
    _diagnostic(key="active_status_word", name="Active status word", address=0x401D, register_count=2, decoder=decode_hex32),
    _diagnostic(key="current_transformer_mode", name="CT mode", address=0x401F, register_count=1, decoder=decode_uint16),
)

MEASUREMENT_SENSORS: tuple[IneproSensorDescription, ...] = (
    _measurement(key="voltage", name="Voltage", address=0x5000, native_unit_of_measurement=str(UnitOfElectricPotential.VOLT), device_class=SensorDeviceClass.VOLTAGE),
    _measurement(key="l1_voltage", name="L1 Voltage", address=0x5002, native_unit_of_measurement=str(UnitOfElectricPotential.VOLT), device_class=SensorDeviceClass.VOLTAGE),
    _measurement(key="l2_voltage", name="L2 Voltage", address=0x5004, native_unit_of_measurement=str(UnitOfElectricPotential.VOLT), device_class=SensorDeviceClass.VOLTAGE),
    _measurement(key="l3_voltage", name="L3 Voltage", address=0x5006, native_unit_of_measurement=str(UnitOfElectricPotential.VOLT), device_class=SensorDeviceClass.VOLTAGE),
    _measurement(key="grid_frequency", name="Grid frequency", address=0x5008, native_unit_of_measurement=str(UnitOfFrequency.HERTZ), device_class=SensorDeviceClass.FREQUENCY),
    _measurement(key="current", name="Current", address=0x500A, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE), device_class=SensorDeviceClass.CURRENT),
    _measurement(key="l1_current", name="L1 Current", address=0x500C, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE), device_class=SensorDeviceClass.CURRENT),
    _measurement(key="l2_current", name="L2 Current", address=0x500E, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE), device_class=SensorDeviceClass.CURRENT),
    _measurement(key="l3_current", name="L3 Current", address=0x5010, native_unit_of_measurement=str(UnitOfElectricCurrent.AMPERE), device_class=SensorDeviceClass.CURRENT),
    _measurement(key="active_power", name="Total active power", address=0x5012, native_unit_of_measurement=str(UnitOfPower.KILO_WATT), device_class=SensorDeviceClass.POWER),
    _measurement(key="l1_active_power", name="L1 Active power", address=0x5014, native_unit_of_measurement=str(UnitOfPower.KILO_WATT), device_class=SensorDeviceClass.POWER),
    _measurement(key="l2_active_power", name="L2 Active power", address=0x5016, native_unit_of_measurement=str(UnitOfPower.KILO_WATT), device_class=SensorDeviceClass.POWER),
    _measurement(key="l3_active_power", name="L3 Active power", address=0x5018, native_unit_of_measurement=str(UnitOfPower.KILO_WATT), device_class=SensorDeviceClass.POWER),
    _measurement(key="reactive_power", name="Total reactive power", address=0x501A, native_unit_of_measurement="kvar", device_class=REACTIVE_POWER_DEVICE_CLASS),
    _measurement(key="l1_reactive_power", name="L1 Reactive power", address=0x501C, native_unit_of_measurement="kvar", device_class=REACTIVE_POWER_DEVICE_CLASS),
    _measurement(key="l2_reactive_power", name="L2 Reactive power", address=0x501E, native_unit_of_measurement="kvar", device_class=REACTIVE_POWER_DEVICE_CLASS),
    _measurement(key="l3_reactive_power", name="L3 Reactive power", address=0x5020, native_unit_of_measurement="kvar", device_class=REACTIVE_POWER_DEVICE_CLASS),
    _measurement(key="apparent_power", name="Total apparent power", address=0x5022, native_unit_of_measurement="kVA", device_class=APPARENT_POWER_DEVICE_CLASS),
    _measurement(key="l1_apparent_power", name="L1 Apparent power", address=0x5024, native_unit_of_measurement="kVA", device_class=APPARENT_POWER_DEVICE_CLASS),
    _measurement(key="l2_apparent_power", name="L2 Apparent Power", address=0x5026, native_unit_of_measurement="kVA", device_class=APPARENT_POWER_DEVICE_CLASS),
    _measurement(key="l3_apparent_power", name="L3 Apparent Power", address=0x5028, native_unit_of_measurement="kVA", device_class=APPARENT_POWER_DEVICE_CLASS),
    _measurement(key="power_factor", name="Power factor", address=0x502A, native_unit_of_measurement=None, device_class=POWER_FACTOR_DEVICE_CLASS),
    _measurement(key="l1_power_factor", name="L1 Power factor", address=0x502C, native_unit_of_measurement=None, device_class=POWER_FACTOR_DEVICE_CLASS),
    _measurement(key="l2_power_factor", name="L2 Power factor", address=0x502E, native_unit_of_measurement=None, device_class=POWER_FACTOR_DEVICE_CLASS),
    _measurement(key="l3_power_factor", name="L3 Power factor", address=0x5030, native_unit_of_measurement=None, device_class=POWER_FACTOR_DEVICE_CLASS),
)

ENERGY_SENSORS: tuple[IneproSensorDescription, ...] = (
    _total(key="total_energy", name="Total active energy", address=0x6000, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_1_total_energy", name="T1 Total active energy", address=0x6002, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_2_total_energy", name="T2 Total active energy", address=0x6004, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l1_total_energy", name="L1 Total active energy", address=0x6006, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l2_total_energy", name="L2 Total active energy", address=0x6008, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l3_total_energy", name="L3 Total active energy", address=0x600A, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="import_active_energy", name="Forward active energy", address=0x600C, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_1_import_active_energy", name="T1 Forward active energy", address=0x600E, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_2_import_active_energy", name="T2 Forward active energy", address=0x6010, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l1_import_active_energy", name="L1 Forward active energy", address=0x6012, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l2_import_active_energy", name="L2 Forward active energy", address=0x6014, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l3_import_active_energy", name="L3 Forward active energy", address=0x6016, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="export_active_energy", name="Reverse active energy", address=0x6018, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_1_export_active_energy", name="T1 Reverse active energy", address=0x601A, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="tariff_2_export_active_energy", name="T2 Reverse Active Energy", address=0x601C, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l1_export_active_energy", name="L1 Reverse active energy", address=0x601E, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l2_export_active_energy", name="L2 Reverse active energy", address=0x6020, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="l3_export_active_energy", name="L3 Reverse active energy", address=0x6022, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY),
    _total(key="total_reactive_energy", name="Total reactive energy", address=0x6024, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_1_total_reactive_energy", name="T1 Total reactive energy", address=0x6026, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_2_total_reactive_energy", name="T2 Total reactive energy", address=0x6028, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l1_total_reactive_energy", name="L1 Total reactive energy", address=0x602A, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l2_total_reactive_energy", name="L2 Total reactive energy", address=0x602C, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l3_total_reactive_energy", name="L3 Total reactive energy", address=0x602E, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="import_reactive_energy", name="Forward reactive energy", address=0x6030, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_1_import_reactive_energy", name="T1 Forward reactive energy", address=0x6032, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_2_import_reactive_energy", name="T2 Forward reactive energy", address=0x6034, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l1_import_reactive_energy", name="L1 Forward reactive energy", address=0x6036, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l2_import_reactive_energy", name="L2 Forward reactive energy", address=0x6038, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l3_import_reactive_energy", name="L3 Forward reactive energy", address=0x603A, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="export_reactive_energy", name="Reverse reactive energy", address=0x603C, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_1_export_reactive_energy", name="T1 Reverse reactive energy", address=0x603E, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="tariff_2_export_reactive_energy", name="T2 Reverse reactive energy", address=0x6040, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l1_export_reactive_energy", name="L1 Reverse reactive energy", address=0x6042, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l2_export_reactive_energy", name="L2 Reverse reactive energy", address=0x6044, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    _total(key="l3_export_reactive_energy", name="L3 Reverse reactive energy", address=0x6046, native_unit_of_measurement="kvarh", device_class=REACTIVE_ENERGY_DEVICE_CLASS),
    IneproSensorDescription(key="tariff", name="Tariff", address=0x6048, register_count=1, decoder=decode_uint16, entity_category=EntityCategory.DIAGNOSTIC, entity_registry_enabled_default=False),
    _total(key="daily_resettable_energy", name="Resettable day counter", address=0x6049, native_unit_of_measurement=str(UnitOfEnergy.KILO_WATT_HOUR), device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING, enabled_default=False),
)

SENSOR_DESCRIPTIONS: tuple[IneproSensorDescription, ...] = (
    *IDENTITY_SENSORS,
    *MEASUREMENT_SENSORS,
    *ENERGY_SENSORS,
)
