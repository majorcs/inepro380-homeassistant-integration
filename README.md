# inepro380 Home Assistant integration

Custom Home Assistant integration for the inepro PRO380-Mod energy meter.

## Current scope

- Native Home Assistant custom integration under `custom_components/inepro380`
- UI-only setup through a config flow
- Modbus TCP support
- Configurable polling interval, defaulting to 30 seconds
- One Home Assistant device per physical meter
- Batched register reads for identity, live measurements, and energy totals
- Offline fixture-based tests using a real-device snapshot

## Live validation notes

The initial implementation was validated against `192.168.88.49:502`.

- The documented register addresses are read directly as hexadecimal-style offsets such as `0x4000`, `0x5000`, and `0x6000`
- `Lebegő ABCD` values decode correctly as IEEE754 floats in big-endian word order
- The serial number at `0x4000` decoded to `22091039`

## Installation

1. Add this repository as a custom repository in HACS.
2. Select the default branch or a published tag/release.
3. Restart Home Assistant.
4. Add `inepro PRO380` from the integrations UI.

HACS can install this integration directly from the GitHub repository archive.

The repository export is configured to include only:

- `README.md`
- `custom_components/inepro380/`

Development, test, documentation, and prompt files are excluded from exported archives.

## Release package

No custom zip asset is required for HACS.

The release tag should match the integration version from `manifest.json`.

For the first release, use:

- `2026.04.20.1`

## Versioning

This integration uses the release version format `YYYY.MM.DD.SEQ`.

- `YYYY`: release year
- `MM`: release month
- `DD`: release day
- `SEQ`: sequence number for additional releases on the same day

Example:

- `2026.04.20.1` = first release on 20 April 2026
- `2026.04.20.2` = second release on 20 April 2026

## Planned follow-up work

- Modbus RTU / serial transport
- richer diagnostics and enum decoding
- options flow for scan interval and transport settings
- CI validation against Home Assistant custom component tooling
