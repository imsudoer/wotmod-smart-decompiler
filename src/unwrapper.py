# -*- coding: utf-8 -*-
"""
PJOrion Layer 1 Container Unwrapper.
Handles bit-reversed zlib payloads embedded inside <pjorion_protected> code objects.
"""

import zlib
from xdis.load import load_module_from_file_object
import io

_BIT_REV_TABLE = bytes([int(bin(b)[2:].rjust(8, '0')[::-1], 2) for b in range(256)])


def is_pjorion_container(co):
    if getattr(co, 'co_name', '') == '<pjorion_protected>':
        return True
    if hasattr(co, 'co_code') and len(co.co_code) > 13:
        # Check zlib header signature (0x78) at offset 13
        if co.co_code[13] in (0x78, 120):
            return True
    return False


def unwrap_pjorion_bytes(pyc_bytes):
    """
    Detects and unwraps outer PJOrion bit-reversal + zlib layer.
    Returns: (unwrapped_pyc_bytes, was_unwrapped)
    """
    if len(pyc_bytes) < 16:
        return pyc_bytes, False

    bio = io.BytesIO(pyc_bytes)
    try:
        version, timestamp, magic_int, co, is_pypy, source_size, sip_hash = load_module_from_file_object(bio)
    except Exception:
        return pyc_bytes, False

    if not is_pjorion_container(co):
        return pyc_bytes, False

    try:
        compressed_payload = co.co_code[13:]
        decompressed = zlib.decompress(compressed_payload)
        unwrapped_marshaled = decompressed.translate(_BIT_REV_TABLE)

        # Prepend standard Python 2.7 header (magic + timestamp)
        header = bytes.fromhex('03f30d0a') + (timestamp or 0).to_bytes(4, 'little')
        return header + unwrapped_marshaled, True
    except Exception:
        return pyc_bytes, False
