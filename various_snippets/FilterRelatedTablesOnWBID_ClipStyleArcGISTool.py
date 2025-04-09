# Author: Chris Sostad
# WLRS
# Created Date: January 14th, 2025
# Updated Date: 
# Description:
# ArcGIS Pro Script Tool to filter Excel tables based on Waterbody ID from a Join Table.

# Script Summary:
# This Python script filters multiple Excel tables based on waterbody IDs for lakes managed as small lake fisheries in the Omineca Region. It performs the following tasks:

# Inputs & Setup:

# Loads a list of related Excel tables containing fishery data and a separate "Omineca_Lakes Join Table" containing the waterbody IDs of interest.
# Defines a list of possible column names for waterbody IDs since the column naming varies across tables.
# Identify Waterbody IDs:

# Reads the "Omineca_Lakes Join Table" and extracts unique waterbody IDs from the column that matches the predefined list of possible column names.
# Create Output Folder:

# Creates a new folder named filtered_records in the same directory as the input tables for storing filtered results.
# Filtering Process:

# Iterates through each related Excel table and each sheet within the tables.
# For each sheet:
# Identifies the column containing waterbody IDs.
# Filters rows where the waterbody ID matches the list extracted from the "Omineca_Lakes Join Table."
# Saves the filtered data to a new Excel file within the filtered_records folder, maintaining the same sheet names.
# Output:

# Outputs the path of each filtered table for reference in the console.
# Key Functionalities:
# Filters multiple Excel tables based on waterbody IDs.
# Handles varying column names for waterbody IDs.
# Creates a dedicated output directory for filtered results.
# Preserves the original sheet structure of the Excel files.



import arcpy
import os
import pandas as pd

# Set input parameters for ArcGIS Pro ModelBuilder tool
omineca_join_table = arcpy.GetParameterAsText(0)  # Path to the Omineca Join Table
related_tables_folder = arcpy.GetParameterAsText(1)  # Folder containing related Excel tables
output_folder = arcpy.GetParameterAsText(2)  # Output folder for filtered tables


# Set input parameters for ArcGIS Pro ModelBuilder tool

# Possible field names for Waterbody ID
waterbody_id_fields = [
    "WBID", "Waterbody_Key_Group", "Waterbody Key Group Code 50K", 
    "WATERBODY_IDENTIFIER", "WBODY_ID", "WATERBODY_"
]

# Prepare a list to hold output tables for ModelBuilder compatibility
output_tables = []

# Function to find the matching waterbody ID column in a DataFrame
def find_waterbody_id_field(columns):
    for field in waterbody_id_fields:
        for col in columns:
            if col.strip().lower() == field.strip().lower():
                return col
    return None

# Validate and load the Omineca Join Table
if not os.path.exists(omineca_join_table):
    arcpy.AddError(f"Omineca Join Table not found: {omineca_join_table}")
    raise FileNotFoundError(f"Omineca Join Table not found: {omineca_join_table}")

# Load the Omineca Join Table
try:
    df_lakes = pd.read_excel(omineca_join_table)
except Exception as e:
    arcpy.AddError(f"Error reading the Omineca Join Table: {e}")
    raise

# Identify the Waterbody ID field
lakes_id_field = find_waterbody_id_field(df_lakes.columns)
if not lakes_id_field:
    arcpy.AddError("No matching Waterbody ID field found in Omineca Join Table.")
    raise ValueError("No matching Waterbody ID field found.")

# Extract unique Waterbody IDs
lake_ids = df_lakes[lakes_id_field].unique().tolist()

# Create output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# List all Excel files in the related tables folder, excluding the join table
related_tables = [
    os.path.join(related_tables_folder, f) 
    for f in os.listdir(related_tables_folder) 
    if f.endswith('.xlsx') and "join_table" not in f.lower()
]

# Iterate through related tables and filter them
for table_path in related_tables:
    try:
        excel_file = pd.ExcelFile(table_path)
        sheet_names = excel_file.sheet_names
    except Exception as e:
        arcpy.AddWarning(f"Error reading file {table_path}: {e}")
        continue

    for sheet_name in sheet_names:
        try:
            # Load sheet data into a DataFrame
            df_table = excel_file.parse(sheet_name)
            table_id_field = find_waterbody_id_field(df_table.columns)
            if not table_id_field:
                arcpy.AddWarning(f"No Waterbody ID field in sheet '{sheet_name}' of {table_path}. Skipping.")
                continue

            # Filter the data
            filtered_table = df_table[df_table[table_id_field].isin(lake_ids)]

            # Generate output file path with "_Filtered" appended to the name
            file_name = os.path.basename(table_path).replace(".xlsx", "_Filtered.xlsx")
            output_table_path = os.path.join(output_folder, file_name)

            # Save only the filtered version, not duplicating the original file
            with pd.ExcelWriter(output_table_path, engine='openpyxl', mode='w') as writer:
                filtered_table.to_excel(writer, index=False, sheet_name=sheet_name)

            # Add the output table path to the list
            output_tables.append(output_table_path)

            # Send feedback to the ArcGIS Pro tool
            arcpy.AddMessage(f"Filtered data from '{sheet_name}' saved to: {output_table_path}")

        except Exception as e:
            arcpy.AddWarning(f"Error processing sheet '{sheet_name}' in '{table_path}': {e}")

# Set up to 10 output tables for ModelBuilder (Fixed Number)
for index in range(9):
    try:
        arcpy.SetParameter(index + 3, output_tables[index])  # Setting up to 10 outputs
    except IndexError:
        # If fewer than 10 tables exist, output will be empty for those slots
        arcpy.SetParameter(index + 3, None)

# Final message after all processing
arcpy.AddMessage("Processing complete!")
