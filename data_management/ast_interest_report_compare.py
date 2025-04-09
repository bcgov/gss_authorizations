import pandas as pd

# Load the Excel file
excel_path = r"\\spatialfiles.bcgov\srm\gss\projects\gr_2025_82_windfarms\documents\AGO\AGOL Layers Dictionary.xlsx"  # Replace with your file path
xl = pd.ExcelFile(excel_path)

# Read both sheets into DataFrames
df_marked = xl.parse('AST_Layers_In_InterestReport')
df_interest = xl.parse('Interest Report Layers')

# Get the unique values from Column C of Interest Report Layers
interest_layers = set(df_interest.iloc[:, 2].dropna().unique())

# Create a new column (or update column A) in df_marked based on the comparison
# Assuming 'Datasource' is the header for Column F
df_marked.insert(0, "Exists", df_marked['Datasource'].apply(lambda x: "Yes" if x in interest_layers else "No"))

# Save the updated DataFrame to a new Excel file (or overwrite the existing one)
with pd.ExcelWriter('updated_file.xlsx') as writer:
    df_marked.to_excel(writer, sheet_name='Marked_Layers', index=False)
    df_interest.to_excel(writer, sheet_name='Interest Report Layers', index=False)