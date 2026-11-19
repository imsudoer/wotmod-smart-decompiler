#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PJOrion Smart Decompiler & Deobfuscator
CLI utility for analyzing, unpacking, deobfuscating, and decompiling
Python 2.7 bytecode and game modifications protected with PJOrion
(World of Tanks, Mir Tankov, World of Warplanes, BigWorld Engine).
"""

import sys
import os
import argparse
import glob
import zipfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.decompiler import decompile_bytecode
    from src.archive import build_mod_archive
    from src.postprocessor import sanitize_syntax
except ImportError:
    from decompiler import decompile_bytecode
    from archive import build_mod_archive
    from postprocessor import sanitize_syntax


def decompile_file_or_dir(target_path, output_dir, pycdc_bin=None):
    if not pycdc_bin:
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "misc", "pycdc.exe")
        if os.path.exists(candidate):
            pycdc_bin = candidate
        else:
            pycdc_bin = shutil.which("pycdc") or "pycdc"

    # Single standalone .pyc file handling
    if os.path.isfile(target_path) and target_path.lower().endswith('.pyc'):
        mod_name = os.path.splitext(os.path.basename(target_path))[0]
        os.makedirs(output_dir, exist_ok=True)
        dest_path = os.path.join(output_dir, f"{mod_name}.py")
        print(f"=== Decompiling standalone bytecode: {os.path.basename(target_path)} ===")
        with open(target_path, 'rb') as f:
            data = f.read()
        try:
            src_code, is_pjo = decompile_bytecode(data, pycdc_bin=pycdc_bin)
            status = "[PJOrion Deobfuscated]" if is_pjo else "[Clean]"
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(src_code)
            print(f"  [+] {os.path.basename(target_path)} -> {os.path.basename(dest_path)} {status} ({len(src_code.splitlines())} lines)")
            print(f"[OK] Completed: {dest_path}\n")
        except Exception as e:
            print(f"  [!] Decompilation failed: {e}")
        return

    # Mod archives (.wotmod / .mtmod) or directory of archives
    if os.path.isdir(target_path):
        archives = sorted(glob.glob(os.path.join(target_path, "*.mtmod")) + glob.glob(os.path.join(target_path, "*.wotmod")))
        if not archives:
            archives = sorted(glob.glob(os.path.join(target_path, "**", "*.mtmod"), recursive=True) + glob.glob(os.path.join(target_path, "**", "*.wotmod"), recursive=True))
    else:
        archives = [target_path]

    if not archives:
        print(f"[!] No .mtmod, .wotmod, or .pyc files found in {target_path}")
        return

    print(f"[*] Found {len(archives)} mod archive(s) to process.\n")

    for arch in archives:
        mod_name = os.path.splitext(os.path.basename(arch))[0]
        mod_out = os.path.join(output_dir, mod_name)
        os.makedirs(mod_out, exist_ok=True)
        print(f"=== Decompiling: {mod_name} ===")

        with zipfile.ZipFile(arch, 'r') as z:
            names = [n for n in z.namelist() if not n.endswith('/')]
            pyc_count = 0
            res_count = 0

            for name in names:
                data = z.read(name)
                if name.endswith('.pyc'):
                    rel_py = name[:-1]
                    dest_path = os.path.join(mod_out, rel_py)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                    try:
                        src_code, is_pjo = decompile_bytecode(data, pycdc_bin=pycdc_bin)
                        status = "[PJOrion Deobfuscated]" if is_pjo else "[Clean]"
                        with open(dest_path, 'w', encoding='utf-8') as f:
                            f.write(src_code)
                        pyc_count += 1
                        print(f"  [+] {name} -> {rel_py} {status} ({len(src_code.splitlines())} lines)")
                    except Exception as e:
                        print(f"  [!] {name} failed: {e}")
                else:
                    dest_path = os.path.join(mod_out, name)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    res_count += 1

        print(f"[OK] Completed {mod_name}: {pyc_count} scripts, {res_count} resources.\n")

    print(f"All decompiled source files saved to: {output_dir}")


def build_command(args):
    print(f"[*] Building mod from: {args.source}")
    out = args.output or (args.source.rstrip("/\\") + ".mtmod")
    py27 = args.python27 or r"C:\Python27\python.exe"

    try:
        pycs, res, target = build_mod_archive(args.source, out, python27_path=py27)
        print(f"[+] Successfully built: {target}")
        print(f"    Compiled scripts: {pycs}")
        print(f"    Packaged resources: {res}")
    except Exception as e:
        print(f"[!] Build error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="PJOrion Smart Decompiler & Deobfuscator - Toolchain for Python 2.7 / BigWorld mods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python pjorion_decompiler.py decompile mod_StatsPRO_LE.pyc -o ./output_src
  python pjorion_decompiler.py decompile mod_safeShot.mtmod -o ./output_src
  python pjorion_decompiler.py decompile F:/Games/World_of_Tanks/mods/1.26.0.0 -o ./mods_src
  python pjorion_decompiler.py build ./mods_src/safeShot -o ./safeShot.mtmod
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    p_dec = subparsers.add_parser("decompile", help="Decompile .pyc file, .mtmod/.wotmod archive, or folder")
    p_dec.add_argument("target", help="Path to .pyc bytecode file, .mtmod/.wotmod archive, or directory")
    p_dec.add_argument("-o", "--output", default="./decompiled_src", help="Output directory for decompiled source code")
    p_dec.add_argument("--pycdc", default=None, help="Path to pycdc executable (optional)")

    p_bld = subparsers.add_parser("build", help="Compile and pack source folder back into .mtmod/.wotmod archive")
    p_bld.add_argument("source", help="Directory containing mod source code")
    p_bld.add_argument("-o", "--output", default=None, help="Output .mtmod/.wotmod file path")
    p_bld.add_argument("--python27", default=r"C:\Python27\python.exe", help="Path to Python 2.7 interpreter")

    args = parser.parse_args()

    if args.command == "decompile":
        decompile_file_or_dir(args.target, args.output, pycdc_bin=args.pycdc)
    elif args.command == "build":
        build_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
