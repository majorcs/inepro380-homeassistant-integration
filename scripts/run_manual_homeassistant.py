#!/usr/bin/env python3
"""Prepare and run a local Home Assistant instance for manual inepro380 testing."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import venv
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANUAL_VENV = REPO_ROOT / ".venv-manual-ha"
MANUAL_CONFIG_DIR = REPO_ROOT / ".manual-homeassistant"
CUSTOM_COMPONENTS_SOURCE = REPO_ROOT / "custom_components"
CUSTOM_COMPONENTS_TARGET = MANUAL_CONFIG_DIR / "custom_components"
STORAGE_DIR = MANUAL_CONFIG_DIR / ".storage"
CONFIG_ENTRY_PATH = STORAGE_DIR / "core.config_entries"
CONFIGURATION_YAML_PATH = MANUAL_CONFIG_DIR / "configuration.yaml"
SECRETS_YAML_PATH = MANUAL_CONFIG_DIR / "secrets.yaml"

HOME_ASSISTANT_VERSION = "2026.4.3"
PYMODBUS_REQUIREMENT = "pymodbus>=3.11.2,<3.12"
MANUAL_ENTRY_ID = "manual_inepro380_tcp"
MANUAL_UNIQUE_ID = "22091039"
DEFAULT_HOST = "192.168.88.49"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_SCAN_INTERVAL = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local Home Assistant instance for manual inepro380 testing."
    )
    parser.add_argument("--prepare-only", action="store_true", help="Prepare the venv and config, then exit.")
    parser.add_argument("--reset", action="store_true", help="Delete the manual test config directory before preparing it.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Target inepro380 TCP host.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Target inepro380 TCP port.")
    parser.add_argument("--slave-id", type=int, default=DEFAULT_SLAVE_ID, help="Target Modbus slave ID.")
    parser.add_argument("--scan-interval", type=int, default=DEFAULT_SCAN_INTERVAL, help="Polling interval in seconds.")
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def ensure_manual_venv() -> Path:
    python_path = MANUAL_VENV / "bin" / "python"
    if not python_path.exists():
        print(f"Creating manual test venv in {MANUAL_VENV}")
        venv.EnvBuilder(with_pip=True).create(MANUAL_VENV)

    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
    run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            f"homeassistant=={HOME_ASSISTANT_VERSION}",
            PYMODBUS_REQUIREMENT,
        ]
    )
    return python_path


def ensure_manual_config(args: argparse.Namespace) -> None:
    if args.reset and MANUAL_CONFIG_DIR.exists():
        print(f"Removing previous manual config directory: {MANUAL_CONFIG_DIR}")
        shutil.rmtree(MANUAL_CONFIG_DIR)

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    CONFIGURATION_YAML_PATH.write_text(
        "api:\n"
        "config:\n"
        "frontend:\n"
        "history:\n"
        "logger:\n"
        "  default: info\n"
        "  logs:\n"
        "    custom_components.inepro380: debug\n"
        "logbook:\n"
        "map:\n"
        "person:\n"
        "sun:\n"
        "system_health:\n"
        "homeassistant:\n"
        "  name: inepro380 Manual Test\n",
        encoding="utf-8",
    )
    SECRETS_YAML_PATH.write_text("", encoding="utf-8")

    if CUSTOM_COMPONENTS_TARGET.exists() or CUSTOM_COMPONENTS_TARGET.is_symlink():
        if CUSTOM_COMPONENTS_TARGET.is_symlink() and CUSTOM_COMPONENTS_TARGET.resolve() == CUSTOM_COMPONENTS_SOURCE:
            pass
        else:
            if CUSTOM_COMPONENTS_TARGET.is_dir() and not CUSTOM_COMPONENTS_TARGET.is_symlink():
                shutil.rmtree(CUSTOM_COMPONENTS_TARGET)
            else:
                CUSTOM_COMPONENTS_TARGET.unlink()

    if not CUSTOM_COMPONENTS_TARGET.exists():
        try:
            CUSTOM_COMPONENTS_TARGET.symlink_to(CUSTOM_COMPONENTS_SOURCE, target_is_directory=True)
        except OSError:
            shutil.copytree(CUSTOM_COMPONENTS_SOURCE, CUSTOM_COMPONENTS_TARGET)

    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "created_at": now,
        "data": {
            "protocol": "tcp",
            "host": args.host,
            "port": args.port,
            "slave_id": args.slave_id,
            "scan_interval": args.scan_interval,
        },
        "discovery_keys": {},
        "disabled_by": None,
        "domain": "inepro380",
        "entry_id": MANUAL_ENTRY_ID,
        "minor_version": 1,
        "modified_at": now,
        "options": {},
        "pref_disable_new_entities": False,
        "pref_disable_polling": False,
        "source": "user",
        "subentries": [],
        "title": f"Inepro PRO380 {MANUAL_UNIQUE_ID}",
        "unique_id": MANUAL_UNIQUE_ID,
        "version": 1,
    }
    storage_payload = {
        "version": 1,
        "minor_version": 5,
        "key": "core.config_entries",
        "data": {"entries": [entry]},
    }
    CONFIG_ENTRY_PATH.write_text(
        json.dumps(storage_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def print_summary(args: argparse.Namespace) -> None:
    print("Manual Home Assistant test environment is ready.")
    print(f"Config directory: {MANUAL_CONFIG_DIR}")
    print(f"Custom integration source: {CUSTOM_COMPONENTS_SOURCE}")
    print(f"Configured device: tcp://{args.host}:{args.port} slave_id={args.slave_id}")
    print("Expected Home Assistant URL: http://127.0.0.1:8123")


def main() -> int:
    args = parse_args()
    python_path = ensure_manual_venv()
    ensure_manual_config(args)
    print_summary(args)

    if args.prepare_only:
        return 0

    command = [
        str(python_path),
        "-m",
        "homeassistant",
        "--config",
        str(MANUAL_CONFIG_DIR),
    ]
    print("Starting Home Assistant...")
    return subprocess.run(command).returncode


if __name__ == "__main__":
    raise SystemExit(main())
