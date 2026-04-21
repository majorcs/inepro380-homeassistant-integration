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

Home Assistant 2026.3.1 is supported. The integration intentionally allows the
Home Assistant bundled `pymodbus` 3.11.x version instead of pinning one exact
patch release.

The repository export is configured to include only:

- `README.md`
- `custom_components/inepro380/`

Development, test, documentation, and prompt files are excluded from exported archives.

Important branding note:

- Home Assistant local brand assets must live in `custom_components/inepro380/brand/`
- the repository root `brand/` directory is excluded from exported archives
- the integration-local `custom_components/inepro380/brand/` directory is included in exported archives and is the one used by Home Assistant

## Release package

No custom zip asset is required for HACS.

The release tag should match the integration version from `manifest.json`.

Latest published hotfix examples:

- `2026.04.20.3` = brand asset set for HACS and Home Assistant UI
- `2026.04.20.4` = archive export fix to ensure `custom_components/inepro380/brand/` is included in installed copies
- `2026.04.21.1` = configuration UI update with boxed integer slave ID input and reconfigure support for transport settings

## Versioning

This integration uses the release version format `YYYY.MM.DD.SEQ`.

- `YYYY`: release year
- `MM`: release month
- `DD`: release day
- `SEQ`: sequence number for additional releases on the same day

Example:

- `2026.04.20.1` = first release on 20 April 2026
- `2026.04.20.2` = second release on 20 April 2026
- `2026.04.20.4` = fourth release on 20 April 2026
- `2026.04.21.1` = first release on 21 April 2026

## Planned follow-up work

- Modbus RTU / serial transport
- richer diagnostics and enum decoding
- reconfigure flow for transport settings beyond initial setup
- CI validation against Home Assistant custom component tooling
