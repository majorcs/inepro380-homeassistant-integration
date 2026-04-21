# inepro380 technical specification

## Product target

Custom Home Assistant integration for inepro PRO380-Mod energy meters using Modbus.

## Versioning specification

Integration releases use the format `YYYY.MM.DD.SEQ`.

Rules:

- `YYYY` is the four-digit release year
- `MM` is the two-digit release month
- `DD` is the two-digit release day
- `SEQ` is the per-day release sequence starting at `1`

Examples:

- `2026.04.20.1`
- `2026.04.20.2`
- `2026.04.20.4`
- `2026.04.21.1`

## Functional requirements

### Required behavior

- Setup from the Home Assistant UI
- Support multiple devices through multiple config entries
- Read meter data through Modbus TCP
- Group all exposed entities under one Home Assistant device
- Use the serial number as a stable device identifier
- Expose readable values as native sensor entities
- Assign units and `state_class` where applicable
- Do not implement any register writes
- Keep repository HACS-compatible

### Deferred behavior

- Modbus RTU / serial transport
- Write support
- Full enum translation for all labeled status/config values

## Configuration specification

### Current config flow fields

- `host`: TCP host or IP
- `port`: TCP port, default `502`
- `slave_id`: Modbus slave ID, default `1`
- `scan_interval`: polling interval in seconds, default `30`
- `name`: optional user-defined display name

### Current options flow fields

- `scan_interval`: polling interval in seconds, default `30`

### Current reconfigure flow fields

- `host`: TCP host or IP
- `port`: TCP port, default `502`
- `slave_id`: Modbus slave ID, default `1`

### Unique ID strategy

- Probe register `0x4000`
- Decode serial number from two registers as uppercase hex
- Use the serial number as the config entry unique ID

## Transport specification

### Protocol

- Modbus TCP
- Read holding registers only
- No write function codes used by the integration

### Timeouts

- Current TCP timeout: `3` seconds in the client wrapper

### Poll interval

- Default polling interval: `30` seconds
- Current minimum accepted interval: `5` seconds
- The effective interval is resolved from options first, then config-entry data, then the default

### Read plan

The integration performs three contiguous reads per refresh cycle:

| Block | Start | Length | Purpose |
|---|---:|---:|---|
| Identity | `0x4000` | `0x20` | Metadata and diagnostics |
| Live | `0x5000` | `0x32` | Real-time measurements |
| Totals | `0x6000` | `0x4B` | Energy totals and tariff values |

## Register decoding specification

### Supported decoders

- `decode_float_abcd()`
  - two-register IEEE754 float
  - big-endian word order
- `decode_signed_int16()`
  - one-register signed integer
- `decode_uint16()`
  - one-register unsigned integer
- `decode_hex16()`
  - one-register uppercase hex string
- `decode_hex32()`
  - two-register uppercase hex string
- `decode_ascii_word()`
  - one-register ASCII text if bytes are printable, otherwise hex fallback
- `format_version()`
  - float formatted with two decimal places

### Identity register decoding

| Register | Purpose | Decode |
|---|---|---|
| `0x4000-0x4001` | Serial number | `hex32` |
| `0x4002` | Meter code | `hex16` |
| `0x4005-0x4006` | Protocol version | `float -> version` |
| `0x4007-0x4008` | Software version | `float -> version` |
| `0x4009-0x400A` | Hardware version | `float -> version` |

### Live measurement decoding

The `0x5000` block uses float decoding for measurement values.

Current sensor families:
- voltage
- current
- frequency
- active power
- reactive power
- apparent power
- power factor

### Totals decoding

The `0x6000` block uses float decoding for energy totals.

Current sensor families:
- total active energy
- import active energy
- export active energy
- total reactive energy
- import reactive energy
- export reactive energy
- tariff-specific totals
- daily resettable energy

## Entity specification

### Core measurements

- Platform: `sensor`
- Default enabled: yes
- Expected state class: `measurement`

### Totals

- Platform: `sensor`
- Default enabled: yes, except resettable daily counter
- Expected state class: `total`
- Daily resettable counter currently modeled as `total_increasing` and disabled by default pending runtime confirmation

### Diagnostics

- Platform: `sensor`
- Entity category: `diagnostic`
- Default enabled: no

## Device specification

### Device registry data

- identifier: `(inepro380, <serial>)`
- manufacturer: `inepro`
- model: `PRO380-Mod`
- name: config entry title
- serial number: decoded serial
- software version: decoded from `0x4007`
- hardware version: decoded from `0x4009`

## Coordinator specification

### Responsibility

The coordinator is the single source of truth for runtime device state.

It must:
- fetch all configured blocks
- decode every described entity value
- expose metadata and raw register blocks
- raise update failures on communication errors

### Snapshot structure

`IneproSnapshot` contains:
- `values`: decoded entity values keyed by description key
- `raw_blocks`: raw register arrays keyed by block start address
- `metadata`: device metadata dataclass

## Diagnostics specification

Diagnostics output currently includes:
- config entry data with host redacted
- decoded metadata
- decoded values
- raw register blocks

## Repository specification

### Expected repository artifacts

- `custom_components/inepro380/`
- `custom_components/inepro380/brand/`
- `README.md`
- `hacs.json`
- `.github/workflows/ci.yml`
- `tests/`

Archive/export behavior:

- exported installation archives must include `custom_components/inepro380/brand/`
- the repository root `brand/` directory is optional repo metadata and is excluded from exported installation archives

### Python dependency

Runtime dependency:
- `pymodbus>=3.11.2,<3.12`

Test dependencies tracked in `requirements_test.txt`:
- `pytest`
- `pytest-homeassistant-custom-component`

## Validation status

### Completed

- Live Modbus connectivity test against the provided TCP device
- Address-space validation for `0x4000`, `0x5000`, `0x6000`
- Decoder validation for representative float values
- Offline unit tests for decoder and client modules

### Pending

- Full Home Assistant runtime validation
- Full config-flow and entity-platform test execution with Home Assistant test tooling
- Modbus RTU / serial support

## Risks and constraints

- Some register labels in the source map appear OCR-damaged or translated inconsistently
- Several enum-like registers are exposed as raw values until mappings are confirmed
- Daily resettable energy behavior still needs runtime confirmation
- RTU requirements are not fully specified yet
