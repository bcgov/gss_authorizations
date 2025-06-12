import os
from openpyxl import Workbook
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu

# Prompt user to select the main directory
Tk().withdraw()  # Hide the root Tkinter window
main_dir = filedialog.askdirectory(title="Select the main directory provided by the client")
if not main_dir:
    print("No directory selected. Exiting.")
    exit()
print(f"Selected directory: {main_dir}")

# Prompt user to select a region from a dropdown menu
root = Tk()
print("Creating a dropdown menu for region selection...")
root.title("Select Region")
region_var = StringVar(root)
print
region_var.set("Northeast")  # Default region

Label(root, text="Select a region:").pack(pady=10)
regions = [
    "Northeast", "Cariboo", "Kootenay_Boundary", "Skeena",
    "South_Coast", "Thompson_Okanagan", "West_Coast", "Omineca"
]
OptionMenu(root, region_var, *regions).pack(pady=10)
print("confirming selection...")
def confirm_selection():
    root.destroy()

Button(root, text="Confirm", command=confirm_selection).pack(pady=10)
root.mainloop()
region = region_var.get()
print("assigning region to var")
print(f"Selected region: {region}")

# Define paths for the output directory
output_dir = os.path.join(main_dir, "outputs")
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory created: {output_dir}")

# Initialize job counter and workbook counter
job_counter = 0
workbook_counter = 1

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