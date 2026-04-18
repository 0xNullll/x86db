import json
import sqlite3
from collections import Counter
import os

# =========================
# LOADERS
# =========================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)["instructions"]

def load_sql(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM instructions")
    rows = cur.fetchall()

    instructions = []

    for ins in rows:
        ins_id = ins["id"]

        # operands
        cur.execute("""
            SELECT value FROM operands
            WHERE instruction_id = ?
            ORDER BY position
        """, (ins_id,))
        operands = [r["value"] for r in cur.fetchall()] or ["N/A"] * 4

        # flags
        cur.execute("""
            SELECT flag_name, status FROM flags
            WHERE instruction_id = ?
        """, (ins_id,))
        flags_rows = cur.fetchall()
        flags = {f["flag_name"]: f["status"] for f in flags_rows} if flags_rows else None

        instructions.append({
            "iclass"   : ins["iclass"],
            "extension": ins["extension"],
            "category" : ins["category"],
            "opcode"   : ins["opcode"],
            "mnemonic" : ins["mnemonic"],
            "mode64"   : ins["mode64"],
            "compat"   : ins["compat"],
            "cpl"      : ins["cpl"],
            "op_en"    : ins["op_en"],
            "tuple"    : ins["tuple_type"],
            "operands" : operands,
            "flags"    : flags
        })

    conn.close()
    return instructions

# =========================
# STATS
# =========================
def compute_stats(instructions):
    iclass_counter    = Counter(ins.get('iclass') or '???' for ins in instructions)
    extension_counter = Counter(ins.get('extension') for ins in instructions)
    mode64_counter    = Counter(ins.get('mode64') for ins in instructions)
    compat_counter    = Counter(ins.get('compat') for ins in instructions)
    cpl_counter       = Counter(ins.get('cpl') for ins in instructions if ins.get('cpl') is not None)
    category_counter  = Counter(ins.get('category') for ins in instructions)
    op_en_counter     = Counter(ins.get('op_en') or 'UNKNOWN' for ins in instructions)

    operand_arity_counter = Counter(
        sum(1 for v in (ins.get('operands') or []) if v != "N/A")
        for ins in instructions
    )

    def is_valid_64(mode):
        return str(mode).upper().startswith(('V', 'VALID'))

    def is_valid_32(compat):
        return str(compat).upper().startswith(('V', 'VALID'))

    count_32_only = 0
    count_64_only = 0
    count_both = 0
    count_unknown = 0

    for ins in instructions:
        valid64 = is_valid_64(ins.get('mode64'))
        valid32 = is_valid_32(ins.get('compat'))

        if valid32 and valid64:
            count_both += 1
        elif valid32:
            count_32_only += 1
        elif valid64:
            count_64_only += 1
        else:
            count_unknown += 1

    # FLAGS
    flags_counter = Counter()
    fpu_flags_counter = Counter()

    for ins in instructions:
        for flag, status in (ins.get('flags') or {}).items():
            if flag in ('C0', 'C1', 'C2', 'C3'):
                fpu_flags_counter[flag] += 1
            elif status:
                flags_counter[flag] += 1

    flag_status_counter = Counter()
    fpu_flag_status_counter = Counter()

    STATUS_MAP = {
        3: "modified",
        2: "tested",
        1: "undefined",
        0: "not_affected"
    }

    for ins in instructions:
        for flag, status in (ins.get('flags') or {}).items():

            status_name = STATUS_MAP.get(status, str(status))

            if flag in ('C0', 'C1', 'C2', 'C3'):
                fpu_flag_status_counter[(flag, status_name)] += 1
            else:
                flag_status_counter[(flag, status_name)] += 1

    # ================= PRINT =================

    print("\n" + "=" * 80)
    print(f"Number of instructions: {len(instructions)}")

    print("\nInstruction Classes:")
    for k in sorted(iclass_counter):
        print(f"  {k:17}: {iclass_counter[k]}")

    print("\nExtensions:")
    for k in sorted(extension_counter):
        print(f"  {k:15}: {extension_counter[k]}")

    print("\nCategories:")
    for k in sorted(category_counter):
        print(f"  {k:15}: {category_counter[k]}")

    print("\n64-bit Mode:")
    for k, v in mode64_counter.most_common():
        print(f"  {k:15}: {v}")

    print("\nCompatibility:")
    for k, v in compat_counter.most_common():
        print(f"  {k:15}: {v}")

    print("\nMode support summary:")
    print(f"  32-bit only : {count_32_only}")
    print(f"  64-bit only : {count_64_only}")
    print(f"  Both        : {count_both}")
    print(f"  Unknown     : {count_unknown}")

    print("\nCPL distribution:")
    for k, v in sorted(cpl_counter.items()):
        print(f"  CPL {k}: {v}")

    print("\nOp/En distribution:")
    for k, v in op_en_counter.most_common():
        k = "N/A" if k == "UNKNOWN" else k
        print(f"  {k:10}: {v}")

    print("\nOperand arity:")
    for k in sorted(operand_arity_counter):
        print(f"  {k} operands: {operand_arity_counter[k]}")

    print("\nFLAGS usage:")
    for k, v in flags_counter.most_common():
        print(f"  {k:5}: {v}")

    print("\nFLAGS behavior:")

    for (flag, status), count in sorted(flag_status_counter.items()):
        print(f"  {flag:5} {status:12}: {count}")

    print("\nFPU FLAGS usage:")
    for k, v in fpu_flags_counter.most_common():
        print(f"  {k:3}: {v}")

    print("\nFPU FLAGS behavior:")

    for (flag, status), count in sorted(fpu_flag_status_counter.items()):
        print(f"  {flag:3} {status:12}: {count}")

    print("=" * 80 + "\n")


# =========================
# MAIN
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(BASE_DIR, "..", "data", "isa_x86.json")
DB_PATH   = os.path.join(BASE_DIR, "..", "data", "isa_x86.db")

def main():
    mode = input("Mode (json/sql): ").strip().lower()

    if mode == "json":
        instructions = load_json(JSON_PATH)
        compute_stats(instructions)

    elif mode == "sql":
        instructions = load_sql(DB_PATH)
        compute_stats(instructions)

    else:
        print("Invalid mode")


if __name__ == "__main__":
    main()