import csv
import sys
import os

# ─────────────────────────────────────────
#  reader.py - CSV File Editor
#  Usage: python reader.py <src> <dst> <change1> <change2> ...
#  Change format: "X,Y,value"  (X=column, Y=row, both start from 0)
# ─────────────────────────────────────────


def list_files_in_directory(path):
    """List all files in the same directory as the given path."""
    directory = os.path.dirname(path) or "."
    try:
        files = os.listdir(directory)
        print(f"  Files in '{directory}':")
        for f in files:
            print(f"    - {f}")
    except Exception as e:
        print(f"  Could not list directory: {e}")


def load_csv(filepath):
    """Read a CSV file and return its content as a list of lists."""
    rows = []
    with open(filepath, "r", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_csv(filepath, rows):
    """Save a list of lists to a CSV file."""
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def display_csv(rows):
    """Print the CSV content as a formatted table in the terminal."""
    if not rows:
        print("  (empty file)")
        return

    # Calculate column widths for neat alignment
    col_widths = []
    num_cols = max(len(row) for row in rows)
    for col in range(num_cols):
        width = max(len(row[col]) if col < len(row) else 0 for row in rows)
        col_widths.append(width)

    # Print separator line
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    print(separator)
    for row in rows:
        # Pad each cell to the column width
        cells = []
        for col in range(num_cols):
            value = row[col] if col < len(row) else ""
            cells.append(value.ljust(col_widths[col]))
        print("| " + " | ".join(cells) + " |")
        print(separator)


def apply_change(rows, change_str):
    """Apply a single change in 'X,Y,value' format to the rows.
    X = column index, Y = row index (both zero-based).
    Returns True if successful, False if skipped due to error."""

    parts = change_str.split(",", 2)  # split into max 3 parts

    # Validate format: must have exactly 3 parts
    if len(parts) != 3:
        print(f"  ⚠ Skipping invalid change '{change_str}': format must be X,Y,value")
        return False

    col_str, row_str, value = parts

    # Validate X and Y are integers
    if not col_str.isdigit() or not row_str.isdigit():
        print(f"  ⚠ Skipping invalid change '{change_str}': X and Y must be integers")
        return False

    col = int(col_str)
    row = int(row_str)

    # Validate row exists
    if row >= len(rows):
        print(f"  ⚠ Skipping change '{change_str}': row {row} does not exist (max: {len(rows) - 1})")
        return False

    # Validate column exists
    if col >= len(rows[row]):
        print(f"  ⚠ Skipping change '{change_str}': column {col} does not exist in row {row} (max: {len(rows[row]) - 1})")
        return False

    # Apply the change
    rows[row][col] = value
    print(f"  ✔ Changed [{row}][{col}] → '{value}'")
    return True


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

# Check minimum number of arguments (script + src + dst = 3)
if len(sys.argv) < 3:
    print("Usage: python reader.py <src> <dst> <change1> <change2> ...")
    print("  change format: X,Y,value  (e.g. 0,0,piano)")
    sys.exit(1)

src = sys.argv[1]
dst = sys.argv[2]
changes = sys.argv[3:]  # all remaining arguments are changes

# ── Validate source file ──
if not os.path.exists(src):
    print(f"✖ Error: File '{src}' does not exist.")
    list_files_in_directory(src)
    sys.exit(1)

if not os.path.isfile(src):
    print(f"✖ Error: '{src}' is not a file.")
    list_files_in_directory(src)
    sys.exit(1)

# ── Load CSV ──
try:
    rows = load_csv(src)
    print(f"✔ Loaded '{src}' ({len(rows)} rows)\n")
except Exception as e:
    print(f"✖ Error reading file '{src}': {e}")
    sys.exit(1)

# ── Apply changes ──
if changes:
    print("Applying changes:")
    for change in changes:
        apply_change(rows, change)
    print()
else:
    print("No changes specified.\n")

# ── Display result ──
print("Modified CSV content:")
display_csv(rows)
print()

# ── Save to destination ──
try:
    save_csv(dst, rows)
    print(f"✔ Saved to '{dst}'")
except Exception as e:
    print(f"✖ Error saving file '{dst}': {e}")
    sys.exit(1)
