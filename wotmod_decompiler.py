#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WoTMod Smart Decompiler & Deobfuscator
All-in-one CLI utility for decompiling, deobfuscating, and building
World of Tanks / Mir Tankov (.wotmod / .mtmod) Python mods.
"""

import sys
import os
import argparse
import glob
import zipfile
import shutil

# Enable relative import from src if running as a package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.decompiler import decompile_bytecode
    from src.archive import build_mod_archive
    from src.postprocessor import sanitize_syntax
except ImportError:
    # If src is adjacent
    from decompiler import decompile_bytecode
    from archive import build_mod_archive
    from postprocessor import sanitize_syntax


def decompile_file_or_dir(target_path, output_dir, pycdc_bin=None):
    if not pycdc_bin:
        # Check adjacent scratch/misc or path
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "misc", "pycdc.exe")
        if os.path.exists(candidate):
            pycdc_bin = candidate
        else:
            pycdc_bin = shutil.which("pycdc") or "pycdc"

    if os.path.isdir(target_path):
        archives = sorted(glob.glob(os.path.join(target_path, "*.mtmod")) + glob.glob(os.path.join(target_path, "*.wotmod")))
        if not archives:
            archives = sorted(glob.glob(os.path.join(target_path, "**", "*.mtmod"), recursive=True))
    else:
        archives = [target_path]

    if not archives:
        print(f"[!] No .mtmod or .wotmod files found in {target_path}")
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
                    rel_py = name[:-1]  # .pyc -> .py
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
        description="WoTMod Smart Decompiler & Deobfuscator - Toolchain for World of Tanks / Mir Tankov mods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python wotmod_decompiler.py decompile mod_safeShot.mtmod -o ./output
  python wotmod_decompiler.py decompile F:/Tanki/mods/1.46.0.0/DMod -o ./DMod_src
  python wotmod_decompiler.py build ./DMod_src/safeShot -o ./safeShot.mtmod
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Decompile subcommand
    p_dec = subparsers.add_parser("decompile", help="Decompile .mtmod / .wotmod file or folder")
    p_dec.add_argument("target", help="Path to .mtmod/.wotmod file or directory containing mods")
    p_dec.add_argument("-o", "--output", default="./decompiled_src", help="Output directory for source code")
    p_dec.add_argument("--pycdc", default=None, help="Path to pycdc executable (optional)")

    # Build subcommand
    p_bld = subparsers.add_parser("build", help="Compile and pack source folder back into .mtmod")
    p_bld.add_argument("source", help="Directory containing mod source code (with res/ folder)")
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
