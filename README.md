# PJOrion Smart Decompiler & Deobfuscator

All-in-one CLI toolchain for unpacking, deobfuscating, and decompiling protected Python 2.7 bytecode and game modifications across BigWorld Engine titles (World of Tanks, Mir Tankov, World of Warplanes, World of Warships).

---

## Technical Overview: The PJOrion Protection Model

PJOrion is the dominant commercial and private obfuscator used in Python 2.7 game modifications since 2014. Standard decompilers (`uncompyle6`, `decompyle++` / `pycdc`) fail or crash when processing PJOrion artifacts due to deliberate structural corruptions injected into the code object:

1. **Bogus Exception Dispatcher (Anti-Disassembly)**
   At bytecode offset 0, PJOrion injects a `SETUP_EXCEPT` instruction pointing to the end of the code segment, followed immediately by an invalid or truncated opcode at offset 3. Linear sweep disassemblers encounter the illegal instruction and abort execution. In runtime, the Python VM traps the exception and jumps to the handler, which executes three `POP_TOP` instructions to clean the exception stack and lands at the Original Entry Point (OEP).

2. **Control Flow Flattening (CFG Scrambling)**
   The linear execution order is completely fragmented into micro-blocks connected by unconditional relative and absolute jumps (`JUMP_FORWARD`, `JUMP_ABSOLUTE`). Dead instructions, invalid operands, and unreachable code segments are interleaved between valid blocks. Decompilers attempting AST reconstruction fail with recursion limit, stack underflow, or assertion errors.

3. **Bit-Reversed Compressed Container Layer**
   The primary code object is wrapped inside a synthetic `<pjorion_protected>` outer frame. The inner bytecode payload is compressed with zlib and bit-reversed (each byte inverted bitwise: bit 7 becomes bit 0, bit 6 becomes bit 1, etc.).

4. **Identifier Table Corruption**
   Identifiers in `co_varnames` and `co_names` are replaced with unprintable ASCII control characters (`\x00` through `\x1f`) or homoglyph sequences (`i`, `I`, `1`). Decompilers emit invalid syntax, and editors render missing glyph boxes (`□□□□`).

5. **Multi-Stage Runtime Virtual Machines**
   Advanced mods wrap logic inside dynamic loaders. Bytecode is evaluated in memory via `eval`, `chr`, and XOR decryption routines, generating dynamic code objects on the fly and binding them into game namespaces via reflection (`getattr`).

---

## Deobfuscation & Analysis Pipeline

The toolchain processes target files through a multi-stage recovery pipeline:

```
[ Input File (.pyc / .wotmod / .mtmod) ]
                   │
                   ▼
       [ 1. Container Unwrapper ]
   (Detects <pjorion_protected>, inverts bit order, decompresses zlib)
                   │
                   ▼
     [ 2. Multi-Stage VM / Recipe Check ]
   (Identifies runtime dynamic loaders and complex VM signatures)
                   │
                   ▼
     [ 3. CFG Analyzer & OEP Resolver ]
   (Traverses execution branches via NetworkX, eliminates dead blocks)
                   │
                   ▼
       [ 4. Identifier Sanitizer ]
   (Replaces unprintable control characters with valid symbol names)
                   │
                   ▼
    [ 5. Multi-Engine Decompilation ]
   (Primary: uncompyle6 / Fallback: pycdc with AST error handling)
                   │
                   ▼
    [ 6. Postprocessor & Syntax Fixer ]
   (Recovers function signatures, resolves loops, normalizes unicode)
                   │
                   ▼
      [ Output: Clean, Valid Python 2.7 Source ]
```

### Detailed Pipeline Components

- **Container Unwrapping (`src/unwrapper.py`)**: Identifies the 13-byte header signature of PJOrion containers, extracts the bit-reversed stream, maps it through an internal lookup table, decompresses the zlib payload, and synthesizes a valid Python 2.7 `.pyc` header (magic `03F30D0A` and timestamp).
- **CFG Reconstruction (`src/deobfuscator.py`)**: Disassembles instructions from the resolved OEP, constructs a directed control-flow graph with basic blocks, eliminates jump forwarders, purges unreachable nodes, and topologically orders blocks into contiguous linear bytecode.
- **Identifier Sanitization (`src/decompiler.py`)**: Validates every token against Python syntax identifier specifications (`^[a-zA-Z_][a-zA-Z0-9_]*$`). Corrupted or control tokens are replaced with stable prefixed names (`var_N`, `name_N`).
- **Multi-Engine Decompilation (`src/decompiler.py`)**: Runs `uncompyle6` with in-process output capture. If AST parsing fails, routes the bytecode to `pycdc` (Decompyle++).
- **Postprocessing & Signature Recovery (`src/postprocessor.py`)**: When an engine fails inside complex loop bodies, the postprocessor inspects bytecode symbol tables (`co_varnames`, `co_argcount`, `co_flags`) to rebuild correct parameter lists (`args`, `*args`, `**kwargs`) and produces syntactically valid code ready for compilation.
- **Recipe Engine (`src/pjorion_vm.py`)**: Resolves multi-stage dynamic runtime payloads that execute secondary VM interpreters in memory, linking verified deobfuscated reconstructions directly.

---

## Supported Formats & Engines

- **File Types**: Standalone `.pyc` bytecode, `.wotmod` and `.mtmod` zip packages.
- **Runtimes**: Python 2.7 (BigWorld Engine).
- **Target Games**:
  - World of Tanks / Мир Танков
  - World of Warplanes
  - World of Warships
  - Any standalone BigWorld client application using Python 2.7

---

## Installation

### Prerequisites

- **Python 3.8+** (64-bit) for the decompiler and deobfuscation toolchain.
- **Python 2.7** (optional, required only for the `build` command to compile `.py` back into `.pyc`).

### Setup

```bash
git clone https://github.com/imsudoer/pjorion-decompiler.git
cd pjorion-decompiler
pip install -r requirements.txt
```

To install Python 2.7 on Windows via winget (optional, for compiling mods):

```powershell
winget install --id Python.Python.2 -e
```

---

## Usage

### 1. Decompile a Single Bytecode File (`.pyc`)

```bash
python pjorion_decompiler.py decompile path/to/mod_StatsPRO_LE.pyc -o ./output_src
```

### 2. Decompile a Game Modification Package (`.wotmod` / `.mtmod`)

```bash
python pjorion_decompiler.py decompile path/to/mod_safeShot.mtmod -o ./output_src
```

The tool extracts all asset files (`.xml`, `.dds`, `.visual`, `.model`, etc.) and decompiles all `.pyc` scripts into their respective directory hierarchies.

### 3. Decompile an Entire Directory of Mods

```bash
python pjorion_decompiler.py decompile "C:/Games/World_of_Tanks/mods/1.26.0.0" -o ./all_mods_src
```

### 4. Build Modified Source Code Back into Mod Archive

```bash
python pjorion_decompiler.py build ./output_src/safeShot -o "C:/Games/World_of_Tanks/mods/1.26.0.0/safeShot.mtmod"
```

The build command:
1. Compiles every `.py` file to bytecode using Python 2.7.
2. Strips local file paths from code objects.
3. Packages compiled `.pyc` files along with resources into a valid zip archive.
4. Creates automatic `.bak` backups if a target file already exists.
5. Verifies that the target file is not locked by an active game process.

---

## Project Structure

```text
pjorion-decompiler/
├── pjorion_decompiler.py     # Primary CLI entrypoint
├── wotmod_decompiler.py      # Backward-compatible CLI alias
├── requirements.txt          # Python 3 dependencies
├── LICENSE                   # GNU General Public License v3.0
├── README.md                 # Technical documentation
├── src/
│   ├── unwrapper.py          # Container unwrapper (bit-reversal + zlib)
│   ├── deobfuscator.py       # CFG reconstructor and OEP resolver
│   ├── decompiler.py         # Multi-engine orchestrator (uncompyle6 / pycdc)
│   ├── postprocessor.py      # AST sanitizer and signature recovery
│   ├── pjorion_vm.py         # Multi-stage runtime VM handler
│   ├── archive.py            # Mod package builder (.wotmod / .mtmod)
│   └── recipes/              # Reconstructed multi-stage mod templates
└── misc/
    ├── BigWorld.py           # BigWorld Engine mock stubs for IDEs
    ├── Math.py               # Vector and Matrix mock stubs
    ├── Keys.py               # Game input key definitions
    ├── GUI.py                # BigWorld GUI component mock stubs
    ├── ResMgr.py             # BigWorld VFS resource manager stubs
    └── pycdc.exe             # Decompyle++ binary (Windows x86_64)
```

---

## IDE Setup (VS Code / PyCharm)

To eliminate false syntax warnings (`import BigWorld unresolved`, `print statements invalid in Python 3`) when editing decompiled Python 2.7 code in VS Code, add the following to your project's `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "C:\\Python27\\python.exe",
    "python.analysis.extraPaths": [
        "./misc"
    ]
}
```

---

## License

GNU General Public License v3.0 (GPL-3.0). See [LICENSE](LICENSE) for details.
