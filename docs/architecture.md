# inepro380 integration architecture

## Purpose

The `inepro380` integration is a Home Assistant custom integration for the inepro PRO380-Mod energy meter. It groups the device's Modbus register map into a single Home Assistant device with native sensor entities.

## Scope of current implementation

- Home Assistant custom integration under `custom_components/inepro380`
- Config-flow based setup from the Home Assistant UI
- Modbus TCP transport
- Configurable polling interval with a default of 30 seconds
- Single device per config entry
- Batched polling of three validated register blocks
- Native `sensor` entities for live values, totals, and diagnostics
- HACS-oriented repository layout
- Offline fixture-based tests derived from a live device snapshot

## Key architectural decisions

### Integration domain

- Domain: `inepro380`
- One config entry represents one physical meter
- Device identity is based on the meter serial number read from register `0x4000`

### Transport model

The integration uses a transport wrapper in `client.py`.

Current state:
- Implemented: Modbus TCP
- Deferred: Modbus RTU / serial

This keeps polling and decoding logic independent from the transport implementation.

### Polling model

A single `DataUpdateCoordinator` instance is created per config entry.

The coordinator update interval is configurable per device. The default is 30 seconds.

The coordinator polls three validated register blocks:
- `0x4000` length `0x20` for identity and diagnostics
- `0x5000` length `0x32` for live measurements
- `0x6000` length `0x4B` for totals and tariff values

The coordinator decodes all values into a single normalized snapshot and shares it with all entities.

### Entity model

All exposed entities currently use the `sensor` platform.

Entity categories:
- Core measurements: enabled by default
- Energy totals: enabled by default
- Diagnostics / configuration-like sensors: created but disabled by default

No write-capable entities are implemented.

### Device model

All sensor entities point to one Home Assistant device created from:
- manufacturer: `inepro`
- model: `PRO380-Mod`
- serial number: decoded from `0x4000`
- software version: decoded from identity registers
- hardware version: decoded from identity registers

## Runtime data flow

1. User starts config flow from the Home Assistant UI.
2. The integration validates TCP connection settings.
3. The flow also stores a polling interval, defaulting to 30 seconds.
4. The integration probes register block `0x4000` and reads the serial number.
5. The config entry unique ID is set to the serial number.
6. On setup, the integration creates a Modbus TCP client wrapper.
7. A coordinator fetches the three register blocks at the configured interval.
8. Decoders transform raw registers into typed sensor values.
9. Sensor entities read from the coordinator snapshot.
10. Diagnostics expose redacted config-entry and raw-block information.

## Module layout

### Core package

- `custom_components/inepro380/__init__.py`
  - Entry setup and unload
- `custom_components/inepro380/manifest.json`
  - Integration metadata and requirements
- `custom_components/inepro380/const.py`
  - Shared constants and register block definitions
- `custom_components/inepro380/models.py`
  - Shared dataclasses for connection parameters, metadata, and snapshots

### Runtime logic

- `custom_components/inepro380/client.py`
  - Modbus TCP access wrapper
- `custom_components/inepro380/coordinator.py`
  - Polling and snapshot assembly
- `custom_components/inepro380/decoder.py`
  - Register decoding utilities
- `custom_components/inepro380/descriptions.py`
  - Static sensor descriptions and register mapping
- `custom_components/inepro380/entity.py`
  - Shared coordinator entity behavior
- `custom_components/inepro380/sensor.py`
  - Sensor platform implementation

### Home Assistant UX

- `custom_components/inepro380/config_flow.py`
  - UI configuration flow
- `custom_components/inepro380/strings.json`
  - Config-flow strings
- `custom_components/inepro380/translations/en.json`
  - English translations
- `custom_components/inepro380/diagnostics.py`
  - Diagnostics export

### Repository support

- `README.md`
- `hacs.json`
- `custom_components/inepro380/brand/`
- `.github/workflows/ci.yml`

Exported installation archives intentionally exclude the repository root `brand/`
directory while keeping `custom_components/inepro380/brand/`, because Home
Assistant reads local custom integration brand assets from the integration
directory itself.

## Register grouping strategy

### Identity and diagnostics block

Registers in the `0x4000` block provide:
- serial number
- meter code
- protocol / software / hardware versions
- Modbus ID and baud rate
- current transformer related values
- status word / checksum / error code

### Live measurements block

Registers in the `0x5000` block provide:
- voltage
- current
- frequency
- active power
- reactive power
- apparent power
- power factor

### Totals block

Registers in the `0x6000` block provide:
- total active energy
- import / export active energy
- total reactive energy
- import / export reactive energy
- tariff-specific values
- daily resettable counter

## Validation notes

Live validation against `192.168.88.49:502` confirmed:
- documented addresses are read directly as hexadecimal register addresses
- `Lebegő ABCD` values decode as IEEE754 float in big-endian word order
- serial number decoded to `22091039`

## Known gaps

- RTU transport is not implemented yet
- enum decoding is still mostly raw numeric output
- only polling options are currently configurable
- full Home Assistant integration test environment is not yet installed locally

## Planned next steps

1. Run the full Home Assistant custom-component test stack locally
2. Refine entity metadata against Home Assistant statistics rules
3. Add options flow for scan interval and transport options
4. Implement Modbus RTU support
5. Expand diagnostics and enum decoding
