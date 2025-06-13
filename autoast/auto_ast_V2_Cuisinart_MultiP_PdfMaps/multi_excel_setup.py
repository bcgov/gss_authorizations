'''
Folder Selection:
Opens a window asking the user to choose a main directory where the input data is stored.

Region Selection:
Shows a dropdown menu asking the user to select a region (e.g., "Northeast", "Skeena", etc.).

Find Shapefiles:
The script goes through each subfolder inside the selected directory. If it finds a .shp (shapefile) inside a subfolder, it:

Notes the shapefiles path
Creates a matching output folder
Writes an entry to an Excel sheet with default settings
It adds up to 8 jobs per Excel workbook. If more than 8 shapefiles are found, it starts a new workbook.
Each Excel file is saved in a folder called outputs within the selected main directory.'''


import os
from openpyxl import Workbook
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu

# Initialize Tkinter root window
root = Tk()
root.withdraw()  # Hide the main window during file dialog

# Prompt user to select the main directory that contains the shapefiles
main_dir = filedialog.askdirectory(title="Select the main directory ")
if not main_dir:
    print("No directory selected. Exiting.")
    root.destroy()
    exit()
print(f"Selected directory: {main_dir}")

# Now show the root window again for the dropdown
root.deiconify()
print("Creating a dropdown menu for region selection...")
root.title("Select Region")
region_var = StringVar(root)
region_var.set("Northeast")  # Default region

Label(root, text="Select a region:").pack(pady=10)
regions = [
    "Northeast", "Cariboo", "Kootenay_Boundary", "Skeena",
    "South_Coast", "Thompson_Okanagan", "West_Coast", "Omineca"
]
OptionMenu(root, region_var, *regions).pack(pady=10)

def confirm_selection():
    root.quit()  # Exit the mainloop
    root.destroy()  # Close the window

Button(root, text="Confirm", command=confirm_selection).pack(pady=10)
root.mainloop()
region = region_var.get()
print("Selected region:", region)


# Define paths for the output directory
output_dir = os.path.join(main_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory created: {output_dir}")

# Initialize job counter and workbook counter
job_counter = 0 # a
workbook_counter = 1 #A workbook is an excel sheet of jobs

# Create the first workbook
wb = Workbook()
ws = wb.active
ws.title = "ast_config"

# Add the required headers
headers = [
    "region", "feature_layer", "crown_file_number", "disposition_number", 
    "parcel_number", "output_directory", "output_directory_same_as_input", 
    "dont_overwrite_outputs", "skip_conflicts_and_constraints", 
    "suppress_map_creation", "add_maps_to_current", "run_as_fcbc", 
    "ast_condition", "file_number"
]
ws.append(headers)
print("Headers added to the workbook.")

# Iterate through subfolders in the main directory
for subfolder in os.listdir(main_dir):
    subfolder_path = os.path.join(main_dir, subfolder)
    if os.path.isdir(subfolder_path):
        print(f"Processing subfolder: {subfolder_path}")
        # Look for a shapefile in the subfolder
        shapefile = next((f for f in os.listdir(subfolder_path) if f.endswith(".shp")), None)
        if shapefile:
            shapefile_path = os.path.join(subfolder_path, shapefile)
            print(f"Found shapefile: {shapefile_path}")

            # Create a corresponding output subfolder
            output_subfolder = os.path.join(output_dir, subfolder)
            os.makedirs(output_subfolder, exist_ok=True)
            print(f"Output subfolder created: {output_subfolder}")

            # Populate the Excel sheet with the shapefile path and default values
            ws.append([
                region,  # region
                shapefile_path,  # feature_layer
                "",  # crown_file_number
                "",  # disposition_number
                "",  # parcel_number
                output_subfolder,  # output_directory
                "false",  # output_directory_same_as_input
                "false",  # dont_overwrite_outputs
                "false",  # skip_conflicts_and_constraints
                "false",  # suppress_map_creation
                "false",  # add_maps_to_current
                "true",  # run_as_fcbc
                "",  # ast_condition
                ""  # file_number
            ])
            job_counter += 1
            print(f"Job added. Current job counter: {job_counter}")

            # If the job counter reaches 8, save the current workbook and start a new one
            if job_counter == 8:
                batch_excel_path = os.path.join(output_dir, f"jobs_{workbook_counter}.xlsx")
                wb.save(batch_excel_path)
                

                print(f"Batch jobs template saved to: {batch_excel_path}")
                workbook_counter += 1
                job_counter = 0
                

                
                

                # Create a new workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "ast_config"
                ws.append(headers)
                print("New workbook created.")

# Save the last workbook if it contains any jobs
if job_counter > 0:
    batch_excel_path = os.path.join(output_dir, f"jobs_{workbook_counter}.xlsx")
    wb.save(batch_excel_path)
    print(f"Batch jobs template saved to: {batch_excel_path}")