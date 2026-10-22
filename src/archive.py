# -*- coding: utf-8 -*-
"""
Archive unpacker and builder for .wotmod / .mtmod files.
"""

import os
import shutil
import zipfile
import tempfile
import subprocess


def unpack_archive(archive_path, extract_dir):
    """
    Unpacks an .mtmod/.wotmod archive and returns list of (internal_name, is_pyc).
    """
    os.makedirs(extract_dir, exist_ok=True)
    files = []
    with zipfile.ZipFile(archive_path, 'r') as z:
        for name in z.namelist():
            if name.endswith('/'):
                continue
            is_pyc = name.endswith('.pyc')
            files.append((name, is_pyc))
    return files


def compile_py_to_pyc(py_path, python27_path=r"C:\Python27\python.exe"):
    """
    Compiles a Python 2.7 source file to bytecode using Python 2.7 interpreter.
    """
    if not os.path.exists(python27_path):
        raise RuntimeError(f"Python 2.7 interpreter not found at {python27_path}")

    cmd = [python27_path, "-m", "py_compile", py_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Compilation failed for {py_path}:\n{res.stderr}")

    pyc_path = py_path + "c"
    if not os.path.exists(pyc_path):
        raise RuntimeError(f"Output pyc file not found: {pyc_path}")
    return pyc_path


def build_mod_archive(src_dir, out_archive_path, python27_path=r"C:\Python27\python.exe", backup=True):
    """
    Takes an unpacked/decompiled mod directory, compiles all .py into .pyc,
    and packages them along with resources (.dds, .xml, .model) into an .mtmod archive.
    """
    if not os.path.isdir(src_dir):
        raise ValueError(f"Source directory does not exist: {src_dir}")

    os.makedirs(os.path.dirname(os.path.abspath(out_archive_path)), exist_ok=True)

    if backup and os.path.exists(out_archive_path) and not os.path.exists(out_archive_path + ".bak"):
        shutil.copy2(out_archive_path, out_archive_path + ".bak")

    temp_build = tempfile.mkdtemp(prefix="wotmod_build_")
    try:
        pyc_count = 0
        res_count = 0

        for root, dirs, files in os.walk(src_dir):
            rel_dir = os.path.relpath(root, src_dir)
            target_dir = os.path.join(temp_build, rel_dir) if rel_dir != "." else temp_build
            os.makedirs(target_dir, exist_ok=True)

            for f in files:
                src_file = os.path.join(root, f)
                if f.endswith(".py"):
                    pyc_file = compile_py_to_pyc(src_file, python27_path)
                    dest_file = os.path.join(target_dir, f + "c")
                    shutil.move(pyc_file, dest_file)
                    pyc_count += 1
                elif not f.endswith(".pyc"):
                    dest_file = os.path.join(target_dir, f)
                    shutil.copy2(src_file, dest_file)
                    res_count += 1

        tmp_archive = out_archive_path + ".tmp"
        with zipfile.ZipFile(tmp_archive, "w", zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(temp_build):
                for f in files:
                    full_p = os.path.join(root, f)
                    archive_name = os.path.relpath(full_p, temp_build).replace("\\", "/")
                    z.write(full_p, archive_name)

        try:
            if os.path.exists(out_archive_path):
                os.replace(tmp_archive, out_archive_path)
            else:
                shutil.move(tmp_archive, out_archive_path)
        except PermissionError:
            new_target = out_archive_path + ".new"
            shutil.move(tmp_archive, new_target)
            return pyc_count, res_count, new_target

        return pyc_count, res_count, out_archive_path
    finally:
        shutil.rmtree(temp_build, ignore_errors=True)
