# x86db

High-fidelity x86 instruction database with normalized semantics, flag behavior, FPU modeling, and full exception coverage.

---

## Overview

**x86db** is a structured and queryable representation of the x86 instruction set architecture.

This project aggregates and normalizes instruction data from multiple sources into a unified format, available in both **JSON** and **SQLite**.

Unlike encoding/decoding-focused tables, this dataset preserves the **semantic behavior of instructions**, making it suitable for:

- Reverse engineering
- Static analysis
- Emulator development
- ISA research

---

## Goals

The primary goal of this project is to provide:

> A **structured, semantically rich, and queryable dataset** of x86 instructions — not a verbatim copy of any single source.

This project exists because existing resources are often:
- Optimized for encoding/decoding (not semantics)
- Difficult to query programmatically
- Missing consistent structure across instruction metadata

---

## Data Sources & Derivation

This dataset is derived from multiple sources, each contributing specific parts of the instruction model:

### Intel® Software Developer’s Manual (Volume 2)

- **Order Number:** 325383-090US  
- **Revision Date:** February 2026  

The following fields are primarily derived from Intel SDM Vol. 2:

- Instruction class (`iclass`)
- Mnemonic
- Operands
- Opcode
- Description
- Flags (per-flag behavior)
- Flags text
- FPU semantics (fully extracted and normalized):
  - Read / Write
  - Stack delta
  - Constraints
  - Notes
- Exceptions (across all CPU modes)
- Mode validity (64-bit / compatibility)
- Operand encoding (`op/en`)
- Tuple type

---

### Intel XED

Data derived from Intel XED datafiles.

- https://github.com/intelxed/xed

- **Snapshot Date:** 2026-02-03 (latest available at time of cloning)

Includes:
- CPL (privilege level metadata)
- Instruction extensions
- Instruction categories

---

### uops.info

Microarchitectural performance data derived from:

- https://uops.info/

- **Snapshot Date:** 2026-02-03

Includes:

- Throughput
- µops
- Port usage
- Architecture-specific characteristics

Note: Some entries may have missing microarchitectural data depending on source coverage.

---

### x86doc

Based on and extended from:

- https://github.com/fay59/x86doc

This project modifies and builds upon x86doc to:

- Improve parsing of Intel SDM Volume 2
- Extract structured instruction data
- Serve as a foundation for normalization

Significant transformations were applied to unify and enrich the dataset.

---

## Data Characteristics

This dataset includes:

- Semantic instruction behavior (not just encoding)
- Per-flag state tracking (modified, tested, undefined, not_affected)
- Unified flag model (EFLAGS + FPU condition codes C0–C3)
- Dual-layer flag representation:
  - structured (`flags`)
  - original textual (`flags_text`)
- Split instruction descriptions:
  - `description` (core semantics)
  - `description_notes` (clarifications / edge cases)
- FPU stack effects (read/write/delta) with full coverage
- Fully grouped exception handling:
  - Protected mode
  - Real mode
  - Virtual-8086 mode
  - Compatibility mode
  - 64-bit mode
- Architecture-specific performance data
- Consistent structure across all instructions

---

## Formats

The dataset is available in:

- `isa_x86.json` -> normalized, portable format
- `isa_x86.db` -> relational SQLite database

Both formats contain the same underlying data.

- `isa_x86.json` is the **canonical source of truth**
- `isa_x86.db` is a **derived relational representation**

---

## Project Structure

```
x86db/
│
├── data/
│   ├── isa_x86.json      # Canonical normalized dataset (portable format)
│   └── isa_x86.db        # SQLite database (relational form of same data)
│
├── docs/
│   └── schema.md         # Full schema documentation (fields, semantics, notes)
│
├── tools/
│   ├── isa_example.py    # Example usage / querying script
│   └── isa_stats.py      # Statistics & analysis tool (JSON + SQL modes)
│
├── LICENSE
├── README.md
├── .gitignore
└── .gitattributes
```

---

## Directory Breakdown

### `data/`

Contains the **actual dataset**.

* `isa_x86.json`

  * Primary format
  * Fully normalized
  * Best for:

    * scripting
    * portability
    * external tooling

* `isa_x86.db`

  * SQLite relational representation
  * Same data as JSON, but structured across tables
  * Best for:

    * complex queries
    * filtering / joins
    * analysis workflows

---

### `docs/`

Contains documentation about how to **understand and use the dataset**.

* `schema.md`

  * Field definitions
  * Data semantics
  * Notes about:

    * Intel Volume 2 alignment
    * XED-derived fields (`extension`, `category`, `CPL`)
    * meaning of `N/A`, `???`, `null`

This is the **authoritative reference** for interpreting the dataset.

---

### `tools/`

Utility scripts for interacting with the dataset.

* `isa_example.py`

  * Minimal usage example
  * Shows how to:

    * load data
    * access instruction fields
    * iterate/query

* `isa_stats.py`

  * Statistics tool
  * Supports:

    * JSON mode
    * SQL mode
  * Outputs:

    * distributions (extensions, categories, iclass, etc.)
    * operand stats
    * flag usage
    * SQL-only insights (arch, exceptions, FPU)

---

## Data Flow

```
Intel SDM (Vol.2)
        +
Intel XED
        +
uops.info
        ↓
   normalization
        ↓
   isa_x86.json
        ↓
   isa_x86.db (derived)
```

* JSON is the **source of truth**
* SQLite is a **derived, query-optimized representation**

---

## Important Notes

* The dataset is **semantic-first**, not encoding-first
* Fields like `extension` and `category` are derived from **Intel XED**
  and may not exactly match Intel Volume 2 naming
* Minor inconsistencies between sources are expected and intentional
  as part of normalization
* Flags are derived primarily from Intel SDM (Volume 2)
  - When SDM flag text is available, it is used as the authoritative source
  - When missing, flags are derived from Intel XED datafiles as a fallback

---

## Limitations

- Some fields may be missing if not present in source data
- Microarchitectural data coverage depends on uops.info availability
- This is not intended to replace official documentation

---

## Known Issues

- Minor parsing ambiguities may still occur in edge cases of Intel SDM text formatting
- Microarchitectural data coverage depends on uops.info availability

---

## License

This project is released under the **MIT license**. See [LICENSE](LICENSE) for full text.

---

## Attribution

This project aggregates, modifies, and restructures data derived from:

- Intel® 64 and IA-32 Architectures Software Developer’s Manual  
  https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html

- Intel XED (X86 Encoder Decoder)  
  https://github.com/intelxed/xed

- uops.info  
  https://uops.info/

- x86doc  
  https://github.com/mazegen/x86doc

All original content and rights belong to their respective owners.

This repository does not claim ownership of the original instruction specifications
or microarchitectural data.

---

## Motivation

This project was created to fill a gap:

> A ready-to-use x86 instruction database that preserves **semantic equivalence**
> rather than focusing purely on encoding/decoding tables.

---