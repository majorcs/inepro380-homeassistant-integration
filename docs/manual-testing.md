# Manual Home Assistant testing

This repository includes a local launcher for manual end-to-end testing of the `inepro380` integration against the real TCP device at `192.168.88.49:502`.

## What it does

The launcher script:

- creates a dedicated virtual environment in `.venv-manual-ha`
- installs `homeassistant==2026.4.3`
- installs `pymodbus>=3.11.2,<3.12`
- creates a local Home Assistant config directory in `.manual-homeassistant`
- links the repository `custom_components` directory into that config
- pre-seeds a config entry for:
  - protocol: `tcp`
  - host: `192.168.88.49`
  - port: `502`
  - slave ID: `1`
  - scan interval: `30`

## Prepare only

Use the launcher in prepare-only mode to build the environment without starting Home Assistant:

- [scripts/run_manual_homeassistant.py](../scripts/run_manual_homeassistant.py)

Example:

`/home/major/Work/inepro380-homeassistant-integration/.venv/bin/python /home/major/Work/inepro380-homeassistant-integration/scripts/run_manual_homeassistant.py --prepare-only`

## Run Home Assistant

Start Home Assistant with the prepared config:

`/home/major/Work/inepro380-homeassistant-integration/.venv/bin/python /home/major/Work/inepro380-homeassistant-integration/scripts/run_manual_homeassistant.py`

After startup, open:

- `http://127.0.0.1:8123`

## Reset the manual config

To recreate the manual config directory from scratch:

`/home/major/Work/inepro380-homeassistant-integration/.venv/bin/python /home/major/Work/inepro380-homeassistant-integration/scripts/run_manual_homeassistant.py --reset`

## VS Code tasks

Two tasks are available in [.vscode/tasks.json](../.vscode/tasks.json):

- `Prepare manual Home Assistant test`
- `Run manual Home Assistant test`

## Notes

- The manual Home Assistant config is isolated from the repository development venv.
- The manual launcher keeps the `pymodbus` version aligned with the integration manifest and Home Assistant 2026.3+ compatibility.
- The pre-seeded entry uses the validated serial number `22091039` as the unique ID.
- On first startup, Home Assistant may still require normal onboarding in the browser.
