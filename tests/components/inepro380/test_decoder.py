"""Decoder tests for inepro380."""

from __future__ import annotations

import pytest

from custom_components.inepro380.decoder import (
    decode_ascii_word,
    decode_float_abcd,
    decode_hex32,
    format_version,
    parse_identity_metadata,
)


def test_parse_identity_metadata_from_live_snapshot(raw_blocks) -> None:
    """The captured live snapshot should decode into stable identity metadata."""

    metadata = parse_identity_metadata(raw_blocks[0x4000])

    assert metadata.serial_number == "22091039"
    assert metadata.meter_code == "0102"
    assert metadata.protocol_version == "3.20"
    assert metadata.software_version == "2.18"
    assert metadata.hardware_version == "1.32"


def test_float_decoder_matches_live_l1_voltage(raw_blocks) -> None:
    """ABCD float decoding should match the validated live voltage value."""

    assert decode_float_abcd(raw_blocks[0x5000][2:4]) == pytest.approx(234.300003)
    assert decode_float_abcd(raw_blocks[0x5000][8:10]) == pytest.approx(49.979999)


def test_hex_and_version_helpers(raw_blocks) -> None:
    """Hex and version helpers should preserve the live identity values."""

    assert decode_hex32(raw_blocks[0x4000][0:2]) == "22091039"
    assert format_version(raw_blocks[0x4000][5:7]) == "3.20"


def test_ascii_decoder_falls_back_to_hex_for_non_printable_register() -> None:
    """ASCII decoding should fall back to a hex label when bytes are not printable."""

    assert decode_ascii_word([0x3156]) == "1V"
    assert decode_ascii_word([0xC256]) == "0xC256"
