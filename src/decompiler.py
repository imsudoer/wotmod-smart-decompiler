# -*- coding: utf-8 -*-
"""
Multi-engine decompiler runner integrating uncompyle6, pycdc, and automatic deobfuscation.
"""

import io
import os
import tempfile
import subprocess
from xdis.load import load_module
from xdis import marsh
import uncompyle6

from .deobfuscator import find_oep, deob_code_obj, init_marshal_patches
from .postprocessor import postprocess_source

init_marshal_patches()


def run_pycdc(pyc_path, pycdc_bin="pycdc"):
    """
    Executes pycdc executable on a given pyc file.
    """
    try:
        res = subprocess.run([pycdc_bin, pyc_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        return res.stdout.decode('utf-8', errors='replace')
    except Exception:
        return ''


def run_uncompyle6(pyc_path):
    """
    Executes uncompyle6 in-process.
    """
    buf = io.StringIO()
    try:
        uncompyle6.decompile_file(pyc_path, outstream=buf)
        return buf.getvalue(), None
    except Exception as e:
        return buf.getvalue(), str(e)


def decompile_bytecode(pyc_bytes, pycdc_bin="pycdc"):
    """
    Deobfuscates and decompiles Python 2.7 bytecode data.
    Returns: (decompiled_source_string, is_obfuscated)
    """
    with tempfile.NamedTemporaryFile(suffix='.pyc', delete=False) as tf:
        tf.write(pyc_bytes)
        tmp_pyc = tf.name

    try:
        version, timestamp, magic_int, co, is_pypy, source_size, sip_hash = load_module(tmp_pyc)
        is_pjo = (co.co_name == '<pjorion_obfuscated>' or find_oep(bytearray(co.co_code)) != 0)

        cleaned_co = co
        if is_pjo:
            cleaned_co = deob_code_obj(co)
            dumped = marsh.dumps(cleaned_co, python_version=(2, 7))
            header = bytes.fromhex('03f30d0a') + (timestamp or 0).to_bytes(4, 'little')
            with open(tmp_pyc, 'wb') as f:
                f.write(header + dumped)

        u6_out, u6_err = run_uncompyle6(tmp_pyc)
        cdc_out = run_pycdc(tmp_pyc, pycdc_bin) if pycdc_bin and os.path.exists(pycdc_bin) else ''

        if u6_out and not u6_err and 'Parse error at or near' not in u6_out:
            raw_code = u6_out
        elif cdc_out and len(cdc_out.splitlines()) > 5 and 'Unexpected end of stream' not in cdc_out:
            raw_code = cdc_out
        else:
            raw_code = u6_out or cdc_out or '# Decompilation failed'

        final_source = postprocess_source(raw_code, cleaned_co)
        return final_source, is_pjo
    finally:
        if os.path.exists(tmp_pyc):
            os.remove(tmp_pyc)
