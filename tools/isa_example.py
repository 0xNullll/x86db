import json
import sqlite3
import os

# =========================
# Backend: JSON
# =========================
def dump_instruction_json(data, mnemonic):
    mnemonic = mnemonic.strip().upper()

    def base_mnemonic(m):
        return m.split()[0].upper()

    instructions = [
        ins for ins in data["instructions"]
        if base_mnemonic(ins["mnemonic"]) == mnemonic
    ]

    return instructions


# =========================
# Backend: SQL
# =========================
def dump_instruction_sql(conn, mnemonic):
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    mnemonic = mnemonic.strip().upper()

    cur.execute("""
        SELECT * FROM instructions
        WHERE UPPER(
            SUBSTR(mnemonic, 1, INSTR(mnemonic || ' ', ' ') - 1)
        ) = ?
    """, (mnemonic,))

    rows = cur.fetchall()
    instructions = []

    for ins in rows:
        ins_id = ins["id"]

        # --- operands ---
        cur.execute("""
            SELECT value FROM operands
            WHERE instruction_id = ?
            ORDER BY position
        """, (ins_id,))
        operands = [r["value"] for r in cur.fetchall()]

        # --- flags ---
        cur.execute("""
            SELECT flag_name, status FROM flags
            WHERE instruction_id = ?
        """, (ins_id,))
        flags_rows = cur.fetchall()
        flags = {f["flag_name"]: f["status"] for f in flags_rows} if flags_rows else None

        # --- FPU ---
        cur.execute("SELECT * FROM fpu WHERE instruction_id = ?", (ins_id,))
        fpu_row = cur.fetchone()
        fpu = None
        if fpu_row:
            fpu_row = dict(fpu_row)
            fpu = {
                "read": fpu_row.get("st_read"),
                "write": fpu_row.get("st_write"),
                "delta": fpu_row.get("st_delta"),
                "constraint": fpu_row.get("constraint_type"),
                "notes": fpu_row.get("notes"),
            }

        # --- arch ---
        cur.execute("""
            SELECT arch_name, key, value FROM arch
            WHERE instruction_id = ?
        """, (ins_id,))
        arch_rows = cur.fetchall()
        arch = {}
        for r in arch_rows:
            arch.setdefault(r["arch_name"], {})[r["key"]] = r["value"]
        if not arch:
            arch = None

        # --- exceptions ---
        cur.execute("""
            SELECT id, group_name FROM exception_groups
            WHERE instruction_id = ?
        """, (ins_id,))
        groups = cur.fetchall()

        exceptions = {}
        for g in groups:
            cur.execute("""
                SELECT exception_code, description
                FROM exceptions
                WHERE group_id = ?
            """, (g["id"],))
            ex_rows = cur.fetchall()

            exceptions[g["group_name"]] = {
                ex["exception_code"]: [ex["description"]]
                for ex in ex_rows
            } if ex_rows else None

        if not exceptions:
            exceptions = None

        # --- normalize into JSON shape ---
        instructions.append({
            "mnemonic": ins["mnemonic"],
            "opcode": ins["opcode"],
            "description": ins["description"],
            "description_notes": ins["description_notes"],
            "mode64": ins["mode64"],
            "compat": ins["compat"],
            "extension": ins["extension"],
            "category": ins["category"],
            "operands": operands if operands else None,
            "flags": flags,
            "flags_text": ins["flags_text"],
            "fpu": fpu,
            "arch": arch,
            "exceptions": exceptions
        })

    return instructions


# =========================
# Shared printer
# =========================
def print_instructions(instructions, mnemonic):
    if not instructions:
        print("[!] No instruction found.")
        return

    print(f"\n=== {mnemonic} ({len(instructions)} variants) ===\n")

    for i, ins in enumerate(instructions, 1):
        print(f"[Variant {i}] {ins['mnemonic']}")
        print("-" * 50)

        print(f"Opcode      : {ins['opcode']}")
        print(f"Description : {ins['description']}")
        print(f"Notes       : {ins['description_notes']}")
        print(f"Mode        : 64bit={ins['mode64']} | Compat={ins['compat']}")
        print(f"Extension   : {ins['extension']}")
        print(f"Category    : {ins['category']}")

        ops = ins.get("operands")
        print(f"Operands    : [{', '.join(ops) if ops else 'None'}]")

        print("\nFlags (Detailed):")
        if ins.get("flags"):
            for k, v in ins["flags"].items():
                print(f"  {k:<4} -> {v}")
        else:
            print("  None")

        if ins.get("flags_text"):
            print(f"\nFlags Text  : {ins['flags_text']}")

        print("\nFPU:")
        if ins.get("fpu"):
            f = ins["fpu"]
            print(f"  Read       : {f.get('read')}")
            print(f"  Write      : {f.get('write')}")
            print(f"  Delta      : {f.get('delta')}")
            print(f"  Constraint : {f.get('constraint')}")
            print(f"  Notes      : {f.get('notes')}")
        else:
            print("  None")

        print("\nArchitecture:")
        if ins.get("arch"):
            for arch, vals in ins["arch"].items():
                print(f"  {arch}")
                for k, v in vals.items():
                    print(f"    {k:<12}: {v}")
        else:
            print("  None")

        print("\nExceptions:")
        if ins.get("exceptions"):
            for group, excs in ins["exceptions"].items():
                print(f"  {group}")
                if excs:
                    for code, descs in excs.items():
                        for d in descs:
                            print(f"    {code}: {d}")
                else:
                    print("    None")
        else:
            print("  None")

        print("\n" + "=" * 60 + "\n")


# =========================
# Main
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "..", "data", "isa_x86.json")
DB_PATH   = os.path.join(BASE_DIR, "..", "data", "isa_x86.db")

def main():
    mode = input("Select mode (json/sql): ").strip().lower()

    if mode == "json":
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            backend = json.load(f)
    elif mode == "sql":
        backend = sqlite3.connect(DB_PATH)

    else:
        print("Invalid mode.")
        return

    print("=== x86 ISA Viewer ===")

    while True:
        mnemonic = input("\nEnter instruction (or 'exit'): ").strip()

        if mnemonic.lower() == "exit":
            break

        if not mnemonic:
            continue

        if mode == "json":
            instructions = dump_instruction_json(backend, mnemonic)
        else:
            instructions = dump_instruction_sql(backend, mnemonic)

        print_instructions(instructions, mnemonic.upper())

    if mode == "sql":
        backend.close()


if __name__ == "__main__":
    main()