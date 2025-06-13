'''
This script will prep a folder of shapefiles to be run through the batch tool. 
Do to limitations with BCGW connections and multiprocessing, any excel file greater than 8 jobs MAY
cause an issue with the bcgw and too many connections. This script will break up your list of shapefiles
intro excel files with a maximum of 8 jobs per file.

# Its still early days but it can populate your excel file with the region. If you need a variety of regions,
just chooose a region and then you will have to edit it by hand. A pain in the ass for now but to be improved later


Opens a window asking the user to choose a main directory where the input data is stored.
Shows a dropdown menu asking the user to select a region (e.g., "Northeast", "Skeena", etc.).
The script goes through each subfolder inside the selected directory. 
If it finds a .shp (shapefile) inside a subfolder, it:
Notes the shapefiles path
Creates a matching output folder
Writes an entry to an Excel sheet with default settings
It adds up to 8 jobs per Excel workbook. If more than 8 shapefiles are found, it starts a new workbook.
Each Excel file is saved in a folder called outputs within the selected main directory.'''


import os
from openpyxl import Workbook
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu

def create_job_excel_files():
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
        root.quit()
        root.destroy()

    Button(root, text="Confirm", command=confirm_selection).pack(pady=10)
    root.mainloop()
    region = region_var.get()
    print("Selected region:", region)

    # Define paths for the output directory
    output_dir = os.path.join(main_dir, "outputs")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory created: {output_dir}")

    # Initialize counters and file list
    job_counter = 0
    workbook_counter = 1
    excel_files = []  #New list to store saved Excel file paths

    # Create the first workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "ast_config"

    # Add headers
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
            shapefile = next((f for f in os.listdir(subfolder_path) if f.endswith(".shp")), None)
            if shapefile:
                shapefile_path = os.path.join(subfolder_path, shapefile)
                print(f"Found shapefile: {shapefile_path}")

                output_subfolder = os.path.join(output_dir, subfolder)
                os.makedirs(output_subfolder, exist_ok=True)
                print(f"Output subfolder created: {output_subfolder}")

                ws.append([
                    region,
                    shapefile_path,
                    "",
                    "",
                    "",
                    output_subfolder,
                    "false",
                    "false",
                    "false",
                    "false",
                    "false",
                    "true",
                    "",
                    ""
                ])
                job_counter += 1
                print(f"Job added. Current job counter: {job_counter}")

                # Save workbook if it has 8 jobs
                if job_counter == 8:
                    batch_excel_path = os.path.join(output_dir, f"jobs_{workbook_counter}.xlsx")
                    wb.save(batch_excel_path)
                    excel_files.append(batch_excel_path)  # Track saved file
                    print(f"Batch jobs template saved to: {batch_excel_path}")
                    workbook_counter += 1
                    job_counter = 0

                    wb = Workbook()
                    ws = wb.active
                    ws.title = "ast_config"
                    ws.append(headers)
                    print("New workbook created.")

    # Save final workbook if needed
    if job_counter > 0:
        batch_excel_path = os.path.join(output_dir, f"jobs_{workbook_counter}.xlsx")
        wb.save(batch_excel_path)
        excel_files.append(batch_excel_path)  #Track final file
        print(f"Batch jobs template saved to: {batch_excel_path}")

    return excel_files  # Return the list of created Excel files

if __name__ == "__main__":
    excel_files = create_job_excel_files()
print(f"List of excel file paths is: {excel_files}")