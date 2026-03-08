import csv
import sys
import os
import json
import pickle

# ─────────────────────────────────────────
#  reader_JSON_Pickle.py - Extended File Editor
#  Supports CSV, JSON and Pickle files
#  Uses classes and inheritance
#
#  Usage:
#  python reader_JSON_Pickle.py <src> <dst> <change1> <change2> ...
#  Change format: "X,Y,value"  (X=column, Y=row, both start from 0)
#
#  Examples:
#  python reader_JSON_Pickle.py in.csv out.json 0,0,piano 1,1,mug
#  python reader_JSON_Pickle.py in.json out.pickle 0,0,hello
#  python reader_JSON_Pickle.py in.pickle out.csv 2,1,world
# ─────────────────────────────────────────


# ─────────────────────────────────────────
#  BASE CLASS
# ─────────────────────────────────────────

class FileEditor:
    """
    Base class for file editors.
    Handles:
      - Displaying the table in the terminal
      - Applying changes to rows
      - Listing files in a directory

    Child classes must implement:
      - load(filepath)  → returns list of lists
      - save(filepath, rows)
    """

    def load(self, filepath):
        """Load file and return content as a list of lists. Must be overridden."""
        raise NotImplementedError("Subclasses must implement load()")

    def save(self, filepath, rows):
        """Save list of lists to file. Must be overridden."""
        raise NotImplementedError("Subclasses must implement save()")

    def display(self, rows):
        """Print the content as a formatted table in the terminal."""
        if not rows:
            print("  (empty file)")
            return

        # Calculate column widths for neat alignment
        num_cols = max(len(row) for row in rows)
        col_widths = []
        for col in range(num_cols):
            width = max(len(str(row[col])) if col < len(row) else 0 for row in rows)
            col_widths.append(width)

        separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

        print(separator)
        for row in rows:
            cells = []
            for col in range(num_cols):
                value = str(row[col]) if col < len(row) else ""
                cells.append(value.ljust(col_widths[col]))
            print("| " + " | ".join(cells) + " |")
            print(separator)

    def apply_change(self, rows, change_str):
        """
        Apply a single change in 'X,Y,value' format to the rows.
        X = column index, Y = row index (both zero-based).
        Returns True if successful, False if skipped due to error.
        """
        parts = change_str.split(",", 2)

        # Validate format
        if len(parts) != 3:
            print(f"  ⚠ Skipping invalid change '{change_str}': format must be X,Y,value")
            return False

        col_str, row_str, value = parts

        # Validate X and Y are integers
        if not col_str.strip().isdigit() or not row_str.strip().isdigit():
            print(f"  ⚠ Skipping invalid change '{change_str}': X and Y must be integers")
            return False

        col = int(col_str.strip())
        row = int(row_str.strip())

        # Validate row exists
        if row >= len(rows):
            print(f"  ⚠ Skipping change '{change_str}': row {row} does not exist (max: {len(rows) - 1})")
            return False

        # Validate column exists
        if col >= len(rows[row]):
            print(f"  ⚠ Skipping change '{change_str}': column {col} does not exist in row {row} (max: {len(rows[row]) - 1})")
            return False

        # Apply the change
        rows[row][col] = value.strip()
        print(f"  ✔ Changed [{row}][{col}] → '{value.strip()}'")
        return True

    def list_files_in_directory(self, path):
        """List all files in the same directory as the given path."""
        directory = os.path.dirname(path) or "."
        try:
            files = os.listdir(directory)
            print(f"  Files in '{directory}':")
            for f in files:
                print(f"    - {f}")
        except Exception as e:
            print(f"  Could not list directory: {e}")


# ─────────────────────────────────────────
#  CSV EDITOR (inherits from FileEditor)
# ─────────────────────────────────────────

class CsvEditor(FileEditor):
    """Handles reading and writing CSV files."""

    def load(self, filepath):
        """Read a CSV file and return its content as a list of lists."""
        rows = []
        with open(filepath, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
        return rows

    def save(self, filepath, rows):
        """Save a list of lists to a CSV file."""
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)


# ─────────────────────────────────────────
#  JSON EDITOR (inherits from FileEditor)
# ─────────────────────────────────────────

class JsonEditor(FileEditor):
    """Handles reading and writing JSON files.
    Format: list of lists, each inner list is a row of strings.
    Example: [["door","3","7"], ["sand","12","5"]]
    """

    def load(self, filepath):
        """Read a JSON file and return its content as a list of lists."""
        with open(filepath, "r") as f:
            data = json.load(f)
        # Ensure all values are strings (consistent with CSV behaviour)
        rows = [[str(cell) for cell in row] for row in data]
        return rows

    def save(self, filepath, rows):
        """Save a list of lists to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(rows, f, indent=2)


# ─────────────────────────────────────────
#  PICKLE EDITOR (inherits from FileEditor)
# ─────────────────────────────────────────

class PickleEditor(FileEditor):
    """Handles reading and writing Pickle files.
    Format: list of lists, each inner list is a row of strings.
    """

    def load(self, filepath):
        """Read a Pickle file and return its content as a list of lists."""
        with open(filepath, "rb") as f:      # "rb" = read binary
            data = pickle.load(f)
        # Ensure all values are strings
        rows = [[str(cell) for cell in row] for row in data]
        return rows

    def save(self, filepath, rows):
        """Save a list of lists to a Pickle file."""
        with open(filepath, "wb") as f:      # "wb" = write binary
            pickle.dump(rows, f)


# ─────────────────────────────────────────
#  FACTORY FUNCTION
#  Returns the correct editor based on file extension
# ─────────────────────────────────────────

def get_editor(filepath):
    """
    Detect file type from extension and return the correct editor object.
    Supported: .csv, .json, .pickle
    """
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext == ".csv":
        return CsvEditor()
    elif ext == ".json":
        return JsonEditor()
    elif ext == ".pickle":
        return PickleEditor()
    else:
        print(f"✖ Unsupported file type: '{ext}'. Supported: .csv, .json, .pickle")
        sys.exit(1)


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────

# Check minimum number of arguments
if len(sys.argv) < 3:
    print("Usage: python reader_JSON_Pickle.py <src> <dst> <change1> <change2> ...")
    print("  change format: X,Y,value  (e.g. 0,0,piano)")
    print("  supported formats: .csv  .json  .pickle")
    sys.exit(1)

src     = sys.argv[1]
dst     = sys.argv[2]
changes = sys.argv[3:]

# ── Validate source file ──
if not os.path.exists(src):
    print(f"✖ Error: File '{src}' does not exist.")
    # Use a base FileEditor just to call list_files_in_directory
    FileEditor().list_files_in_directory(src)
    sys.exit(1)

if not os.path.isfile(src):
    print(f"✖ Error: '{src}' is not a file.")
    FileEditor().list_files_in_directory(src)
    sys.exit(1)

# ── Get the correct editor for the source file ──
src_editor = get_editor(src)

# ── Load file ──
try:
    rows = src_editor.load(src)
    print(f"✔ Loaded '{src}' ({len(rows)} rows)\n")
except Exception as e:
    print(f"✖ Error reading file '{src}': {e}")
    sys.exit(1)

# ── Apply changes ──
if changes:
    print("Applying changes:")
    for change in changes:
        src_editor.apply_change(rows, change)
    print()
else:
    print("No changes specified.\n")

# ── Display result ──
print("Modified file content:")
src_editor.display(rows)
print()

# ── Get the correct editor for the destination file ──
dst_editor = get_editor(dst)

# ── Save to destination ──
try:
    dst_editor.save(dst, rows)
    print(f"✔ Saved to '{dst}'")
except Exception as e:
    print(f"✖ Error saving file '{dst}': {e}")
    sys.exit(1)
