import pandas as pd
import openpyxl

# Load the Excel file
file_path = "Monthly Portfolio-31 12 25.xlsx"
excel_file = pd.ExcelFile(file_path)

# Get all sheet names
print("=" * 80)
print("SHEET NAMES IN THE EXCEL FILE:")
print("=" * 80)
for i, sheet in enumerate(excel_file.sheet_names, 1):
    print(f"{i}. {sheet}")

print(f"\nTotal Sheets: {len(excel_file.sheet_names)}")

# Analyze Index sheet
print("\n" + "=" * 80)
print("ANALYZING INDEX SHEET:")
print("=" * 80)
try:
    index_df = pd.read_excel(file_path, sheet_name="Index", header=None)
    print(f"Rows: {len(index_df)}, Columns: {len(index_df.columns)}")
    print("\nFirst 15 rows:")
    print(index_df.head(15))
except Exception as e:
    print(f"Error reading Index sheet: {e}")

# Analyze first few scheme sheets
print("\n" + "=" * 80)
print("ANALYZING SAMPLE SCHEME SHEETS:")
print("=" * 80)

# Get non-index sheets
scheme_sheets = [s for s in excel_file.sheet_names if s.lower() != "index"][:3]

for sheet in scheme_sheets:
    print(f"\n--- Sheet: {sheet} ---")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet, header=None)
        print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
        print("\nFirst 20 rows:")
        print(df.head(20))
    except Exception as e:
        print(f"Error reading sheet: {e}")
