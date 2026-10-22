# -*- coding: utf-8 -*-
"""
Post-processor and syntax sanitizer for decompiled Python 2.7 source files.
Recovers broken function signatures from bytecode symbol tables and fixes decompiler artifacts.
"""

import re


def extract_bytecode_signatures(code_obj, sigs=None):
    """
    Recursively extracts exact argument signatures from a code object.
    """
    if sigs is None:
        sigs = {}
    name = code_obj.co_name
    args = list(code_obj.co_varnames[:code_obj.co_argcount])
    idx = code_obj.co_argcount
    if code_obj.co_flags & 0x04:
        args.append('*' + code_obj.co_varnames[idx])
        idx += 1
    if code_obj.co_flags & 0x08:
        args.append('**' + code_obj.co_varnames[idx])
        idx += 1
    sigs[name] = ', '.join(args)

    for c in code_obj.co_consts:
        if hasattr(c, 'co_code'):
            extract_bytecode_signatures(c, sigs)
    return sigs


def fix_broken_function_definitions(text, signatures):
    """
    Repairs 'def funcNameParse error at or near...' lines inserted by uncompyle6 on AST failure.
    Replaces with valid signature 'def funcName(args): pass'.
    """
    pattern = re.compile(r'^(\s*)def\s+([a-zA-Z0-9_]+)Parse error.*', re.MULTILINE)
    lines = text.splitlines(True)
    new_lines = []

    for i, line in enumerate(lines):
        m = pattern.match(line)
        if m:
            indent = m.group(1)
            fname = m.group(2)
            args = signatures.get(fname, '')
            new_lines.append(f'{indent}def {fname}({args}):\n')

            next_line = lines[i + 1] if i + 1 < len(lines) else ''
            next_indent = len(next_line) - len(next_line.lstrip()) if next_line.strip() else 0
            curr_indent = len(indent)

            if not next_line.strip() or next_indent <= curr_indent:
                new_lines.append(f'{indent}    pass  # Decompilation failed for this method\n')
        else:
            new_lines.append(line)

    return ''.join(new_lines)


def sanitize_syntax(text):
    """
    Cleans up all common decompiler formatting glitches.
    """
    # Fix uncompyle6 unicode escape bug: \u0x43b -> \u043b, \u0x043b -> \U0000043b
    text = re.sub(r'\\u0x([0-9a-fA-F]{3})', r'\\u0\1', text)
    text = re.sub(r'\\u0x([0-9a-fA-F]{4})', r'\\U0000\1', text)

    # Fix u'b'...' string prefixes
    text = re.sub(r"u'b'([^']*)'", r"'\1'", text)
    text = re.sub(r'u"b"([^"]*)"', r'"\1"', text)

    # Fix pycdc type placeholder
    text = re.sub(r'<TYPE:\s*\d+>', '2147483647', text)

    # Fix pycdc invalid comprehension lambda syntax: lambda .0: pass
    text = re.sub(r'lambda\s+\.0:\s*(?:pass|None)', 'lambda *args: None', text)
    text = re.sub(r'lambda\s+\.0:', 'lambda *args:', text)

    # Fix lambda : pass -> lambda : None
    text = re.sub(r'lambda\s*:\s*pass', 'lambda: None', text)

    # Strip appended decompiler notes/snippets
    if '# --- DECOMPILATION NOTE ---' in text:
        idx = text.find('# --- DECOMPILATION NOTE ---')
        text = text[:idx]

    # Strip trailing module-level returns
    lines = text.splitlines()
    while lines and (not lines[-1].strip() or lines[-1].strip() == 'return'):
        lines.pop()

    return '\n'.join(lines) + '\n'


def postprocess_source(source_text, code_obj=None):
    """
    Complete pipeline: signature restoration + syntax sanitization.
    """
    sigs = {}
    if code_obj:
        extract_bytecode_signatures(code_obj, sigs)

    text = fix_broken_function_definitions(source_text, sigs)
    text = sanitize_syntax(text)
    return text
