# x86db Schema

## Overview
This dataset provides a structured representation of x86 instructions in both JSON and SQL formats.  
It focuses on **semantic correctness and queryability**, rather than encoding/decoding tables.

The dataset is derived from multiple sources and normalized into a unified schema.

---

## Supported Fields

### Core Fields
- iclass: Instruction class (e.g., ADD, FISTP)
- extension: ISA extension (e.g., BASE, AVX, X87)
- category: Instruction category
- opcode:
  - Intel-style encoding string (e.g., `DF /3`, `REX.W + 01 /r`)
  - Not normalized
  - Not guaranteed to be machine-decodable
- mnemonic: Full mnemonic
- mode64: 64-bit validity (Valid / Invalid / etc.)
- compat: 32-bit compatibility mode validity
- cpl: Required privilege level
- op_en: Operand encoding type
- tuple: Tuple type (or N/A)
- description: Instruction description

---

### Operands
- Fixed-length (up to 4)
- Filled with `"N/A"` when unused
- May be `null` for implicit instructions
- Operand values are preserved as **semantic strings**
  (not strongly typed or normalized)

---

### Flags
- Dictionary mapping `flag -> status`
- Includes standard FLAGS (CF, ZF, etc.)
- FPU condition codes (C0–C3) may also appear

#### flags_text
- Human-readable description of flag behavior

---

### FPU (Optional)
- read: Stack registers read
- write: Stack registers written
- delta: Stack change
- constraint: Execution constraints
- notes: Behavioral notes

---

### Architecture Data (`arch`)
- Per-microarchitecture performance data
- Source: uops.info
- Key = architecture (e.g., ADL-P, RPL, etc.)

Values may include:
- throughput
- uops
- ports
- uops_mite
- uops_ms
- retire slots
- etc.

---

### Exceptions
- Grouped by execution mode:
  - Protected Mode
  - Real Mode
  - Virtual-8086 Mode
  - Compatibility Mode
  - 64-Bit Mode
  - Floating-Point Exceptions

Each group contains:
- exception code -> list of descriptions

---

## Value Types / What to Expect

### Extensions
The `extension` field is **NOT taken from Intel Volume 2**.

It is derived from **Intel XED datafiles**, and represents:
- ISA feature groups
- implementation-level classification

Examples:
- BASE, AVX, AVX2, AVX512EVEX, X87, SSE, BMI1, etc.

> **These values:**
> - may not appear in Intel manuals
> - may group instructions differently than Intel documentation
> - are intended for **programmatic classification**, not documentation fidelity

---

### Categories
The `category` field is also derived from **Intel XED datafiles**.

Examples:
- BINARY, LOGICAL, DATAXFER, X87_ALU, SHIFT, CALL, etc.

> **Note:**
> - Not part of Intel Volume 2
> - Designed for **categorization and querying**
> - May not exactly match Intel’s conceptual grouping

---

### op_en (Operand Encoding)
- A, B, C, RM, MR, ZO, I, etc.
- Based on Intel Volume 2 operand encoding notation

---

### Modes
- mode64: Valid / Invalid / V / N.E.
- compat: Valid / Invalid / V / N.E.

---

---

## Notes

- Missing or special values may appear as:

  - `null`  
    -> Field is intentionally empty (no data available or not applicable)

  - `"N/A"`  
    -> Field was parsed correctly, but does not apply to this instruction  
    (i.e., the absence of data is **expected and correct**)

  - `"???"`  
    -> Parser was unable to extract or determine the value  
    (this indicates a **parsing limitation or error**, not a source issue)

    If you encounter `"???"`, please consider opening an issue.

- Dataset is normalized from multiple sources:
  - Intel® Volume 2 (primary semantic source)
  - XED datafiles (extension, category, CPL)
  - uops.info (microarchitecture data)

- Some fields may be absent depending on instruction type

---

## Known Limitations

- FPU description field may be missing due to parsing limitations  
  (this is a parsing issue, not a source limitation)

---

## Notes on Intel® Volume 2 Semantics

This database represents instructions in a **semantic form**, closely aligned with:

Intel® 64 and IA-32 Architectures Software Developer’s Manual  
**Volume 2 (Instruction Set Reference)**  
Order Number: 325383-090US  
February 2026

Fields such as:
- `opcode`
- `mnemonic`
- `operands`
- `op_en`
- `tuple`
- `flags` / `flags_text`
- `description`
- `exceptions`

are derived from Intel Volume 2.

---

### Important

- This is **NOT an encoding table** (unlike XED internal tables or disassembler tables)
- Opcode strings (e.g., `DF /3`, `DE C0+i`) are:
  - human-readable
  - not directly machine-decodable
- Operand descriptions (e.g., `imm8/16/32`, `AL/AX/EAX/RAX`) are:
  - semantic groupings
  - not strict type definitions
- Some fields (e.g., `op_en`, `tuple`) require familiarity with Intel conventions

---

### Recommendation

To fully understand certain fields, refer to:

- Intel® 64 and IA-32 Architectures Software Developer’s Manual  
  Volume 2 (Instruction Set Reference)

---

## Design Goal

This database is designed for:
- analysis
- research
- tooling
- querying instruction semantics

It is **NOT intended for**:
- instruction encoding
- disassembly
- binary translation without additional processing