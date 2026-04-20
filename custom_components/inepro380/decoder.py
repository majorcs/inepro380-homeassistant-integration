"""Register decoding helpers for the inepro380 integration."""

from __future__ import annotations

import struct
from typing import Final

from .const import DEFAULT_NAME
from .models import IneproDeviceMetadata

IDENTITY_BLOCK_START: Final = 0x4000


def decode_float_abcd(registers: list[int]) -> float:
    """Decode a two-register IEEE754 float in ABCD byte order."""

    if len(registers) != 2:
        raise ValueError(f"Expected 2 registers for float decode, got {len(registers)}")

    payload = registers[0].to_bytes(2, byteorder="big") + registers[1].to_bytes(
        2, byteorder="big"
    )
    return round(struct.unpack(">f", payload)[0], 6)


def decode_signed_int16(registers: list[int]) -> int:
    """Decode a signed 16-bit integer."""

    if len(registers) != 1:
        raise ValueError(f"Expected 1 register for signed decode, got {len(registers)}")

    value = registers[0]
    if value >= 0x8000:
        value -= 0x10000
    return value


def decode_uint16(registers: list[int]) -> int:
    """Decode an unsigned 16-bit integer."""

    if len(registers) != 1:
        raise ValueError(f"Expected 1 register for uint16 decode, got {len(registers)}")
    return registers[0]


def decode_hex16(registers: list[int]) -> str:
    """Decode a single register as an uppercase hexadecimal string."""

    return f"{decode_uint16(registers):04X}"


def decode_hex32(registers: list[int]) -> str:
    """Decode two registers as an uppercase hexadecimal string."""

    if len(registers) != 2:
        raise ValueError(f"Expected 2 registers for hex32 decode, got {len(registers)}")
    return f"{registers[0]:04X}{registers[1]:04X}"


def decode_ascii_word(registers: list[int]) -> str:
    """Decode a single 16-bit register as up to two ASCII characters."""

    if len(registers) != 1:
        raise ValueError(f"Expected 1 register for ASCII decode, got {len(registers)}")

    payload = registers[0].to_bytes(2, byteorder="big")
    visible_bytes = [byte for byte in payload if byte != 0]
    if visible_bytes and not all(32 <= byte <= 126 for byte in visible_bytes):
        return f"0x{registers[0]:04X}"

    decoded = payload.decode("ascii", errors="strict").replace("\x00", "").strip()
    if decoded and all(character.isprintable() for character in decoded):
        return decoded
    return f"0x{registers[0]:04X}"


def format_version(registers: list[int]) -> str:
    """Decode a float register pair and render it as a compact version string."""

    return f"{decode_float_abcd(registers):.2f}"


def parse_identity_metadata(identity_registers: list[int]) -> IneproDeviceMetadata:
    """Build device metadata from the 0x4000 identity block."""

    serial_number = decode_hex32(identity_registers[0:2])
    return IneproDeviceMetadata(
        serial_number=serial_number,
        default_name=f"{DEFAULT_NAME} {serial_number}",
        meter_code=decode_hex16(identity_registers[2:3]),
        protocol_version=format_version(identity_registers[5:7]),
        software_version=format_version(identity_registers[7:9]),
        hardware_version=format_version(identity_registers[9:11]),
    )