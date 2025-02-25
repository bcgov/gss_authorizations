# -*- coding: utf-8 -*-
"""
This script performs the following workflow:
  1. Opens an existing ArcMap .lyr file.
  2. Saves it as an ArcGIS Pro .lyrx file to a specified output folder.
  3. Reopens the new .lyrx file and updates the connection properties for each layer,
     changing the FGDB path based on a new data location.
  4. Saves the updated .lyrx file.

Update these parameters before running:
    - in_layer_file: Path to the input .lyr file.
    - new_data_location: Folder where the new file geodatabase (with the same name as the old one) resides.
    - out_folder: Folder where the repathed .lyrx file should be saved.
"""

import arcpy
import os

def transform_gdb_path(source_path, new_data_location):
    source_path_norm = os.path.normpath(source_path)
    idx = source_path_norm.lower().find(".gdb")
    if idx == -1:
        return None

    old_gdb = source_path_norm[:idx+4]
    old_gdb_name = os.path.basename(old_gdb)
    rel_path = os.path.relpath(source_path_norm, old_gdb)
    
    new_gdb = os.path.join(new_data_location, old_gdb_name)
    new_path = os.path.join(new_gdb, rel_path)
    
    # Ensure final path uses Windows backslashes:
    new_path = os.path.normpath(new_path)
    
    return new_path


def update_layer_connections(lyr, new_data_location):
    """
    Recursively update the connection properties for each layer.
    For layers whose dataSource contains a .gdb, build a new path based on new_data_location,
    then update the connection properties.
    """
    try:
        if lyr.isGroupLayer:
            for sublyr in lyr.listLayers():
                update_layer_connections(sublyr, new_data_location)
        else:
            current_source = lyr.dataSource
            if current_source and ".gdb" in current_source.lower():
                new_path = transform_gdb_path(current_source, new_data_location)
                if new_path:
                    idx = new_path.lower().find(".gdb")
                    new_workspace = new_path[:idx+4]  # Includes the .gdb folder
                    dataset_name = new_path[idx+5:]     # The remainder is the dataset path
                    msg = (f"Updating layer '{lyr.name}':\n"
                           f"  Old source: {current_source}\n"
                           f"  New workspace: {new_workspace}\n"
                           f"  Dataset: {dataset_name}")
                    print(msg)
                    arcpy.AddMessage(msg)
                    
                    try:
                        if hasattr(lyr, "updateConnectionProperties"):
                            old_conn = lyr.connectionProperties
                            new_conn = old_conn.copy()
                            # For file geodatabases, update the database path.
                            if "connection_info" in new_conn and "database" in new_conn["connection_info"]:
                                new_conn["connection_info"]["database"] = new_workspace
                            # Optionally, update the dataset name.
                            if "dataset" in new_conn:
                                new_conn["dataset"] = dataset_name
                            
                            if lyr.updateConnectionProperties(old_conn, new_conn):
                                msg = f"Successfully updated connection for layer '{lyr.name}'."
                            else:
                                msg = f"Failed to update connection for layer '{lyr.name}'."
                            print(msg)
                            arcpy.AddMessage(msg)
                        else:
                            msg = f"Layer '{lyr.name}' does not support updateConnectionProperties."
                            print(msg)
                            arcpy.AddMessage(msg)
                    except Exception as e:
                        msg = f"Error updating connection for layer '{lyr.name}': {str(e)}"
                        print(msg)
                        arcpy.AddMessage(msg)
                else:
                    msg = f"Warning: Could not transform data source for layer '{lyr.name}'."
                    print(msg)
                    arcpy.AddMessage(msg)
            else:
                msg = f"Layer '{lyr.name}' does not reference a file geodatabase."
                print(msg)
                arcpy.AddMessage(msg)
    except Exception as e:
        msg = f"Error processing layer '{lyr.name}': {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)

def main():
    # ==========================================================================
    # User-defined parameters: Update these paths before running.
    # ==========================================================================
    # Input .lyr file (ArcMap layer file)
    in_layer_file = r"//spatialfiles.bcgov/work/srm/nel/Local/Geomatics/Workarea/csostad/Cartographic Standards Group/Q Drive BaseMap Files/Base Map - BC Border Areas - 1,000,000.lyr"
    
    # New data location: the folder where the new file geodatabase resides
    new_data_location = r"//giswhse.env.gov.bc.ca/whse_np/corp/cartographic_resources/data_whse/Base/Base1000"
    
    # Output folder for the new .lyrx file
    out_folder = r"C:/Users/CSOSTAD/Desktop/LayerFileExportTest"
    
    # ==========================================================================
    # Step 1. Open the existing .lyr file.
    msg = f"Starting repathing process for layer file: {in_layer_file}"
    print(msg)
    arcpy.AddMessage(msg)
    
    if not os.path.exists(in_layer_file):
        msg = f"Input layer file does not exist: {in_layer_file}"
        print(msg)
        arcpy.AddMessage(msg)
        return
    
    if not os.path.exists(new_data_location):
        msg = f"New data location does not exist: {new_data_location}"
        print(msg)
        arcpy.AddMessage(msg)
        return
    
    if not os.path.exists(out_folder):
        try:
            os.makedirs(out_folder)
            msg = f"Created output folder: {out_folder}"
            print(msg)
            arcpy.AddMessage(msg)
        except Exception as e:
            msg = f"Could not create output folder {out_folder}: {str(e)}"
            print(msg)
            arcpy.AddMessage(msg)
            return

    try:
        lyrFile_old = arcpy.mp.LayerFile(in_layer_file)
        msg = f"Successfully loaded .lyr file: {in_layer_file}"
        print(msg)
        arcpy.AddMessage(msg)
    except Exception as e:
        msg = f"Error loading .lyr file {in_layer_file}: {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)
        return

    # ==========================================================================
    # Step 2. Save the .lyr file as a .lyrx file in the output folder.
    base_name = os.path.splitext(os.path.basename(in_layer_file))[0]
    out_layer_file = os.path.join(out_folder, base_name + ".lyrx")
    try:
        lyrFile_old.saveACopy(out_layer_file)
        msg = f"Saved .lyrx file to: {out_layer_file}"
        print(msg)
        arcpy.AddMessage(msg)
    except Exception as e:
        msg = f"Error saving .lyrx file to {out_layer_file}: {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)
        return

    # ==========================================================================
    # Step 3. Reopen the new .lyrx file and update its connection properties.
    try:
        lyrFile_new = arcpy.mp.LayerFile(out_layer_file)
        msg = f"Reopened .lyrx file for updating: {out_layer_file}"
        print(msg)
        arcpy.AddMessage(msg)
    except Exception as e:
        msg = f"Error reopening .lyrx file {out_layer_file}: {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)
        return

    try:
        layers = lyrFile_new.listLayers()
        if not layers:
            msg = "No layers found in the .lyrx file."
            print(msg)
            arcpy.AddMessage(msg)
        else:
            for lyr in layers:
                
                # Get the current connection properties
                current_conn_props = lyr.connectionProperties
                # Print out the current connection properties to see what they look like
                print("Current Connection Properties:\n", current_conn_props)
               
               # Repoint the layer to a different file geodatabase
                
                # Copy the current connection properties to a new variable
                new_conn_props = current_conn_props
                
                # Edit the connection properties dictionary
                new_conn_props['connection_info']['database'] = r"//giswhse.env.gov.bc.ca/whse_np/corp/cartographic_resources/data_whse/Base/Base1000"
                
                # Update the layer's connection properties
                lyr.updateConnectionProperties(current_conn_props, new_conn_props)
                
                
                # update_layer_connections(lyr, new_data_location)
    except Exception as e:
        msg = f"Error processing layers in {out_layer_file}: {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)
        return

    # ==========================================================================
    # Step 4. Save the updated .lyrx file.
    try:
        lyrFile_new.save()
        msg = f"Saved updated .lyrx file to: {out_layer_file}"
        print(msg)
        arcpy.AddMessage(msg)
    except Exception as e:
        msg = f"Error saving updated .lyrx file to {out_layer_file}: {str(e)}"
        print(msg)
        arcpy.AddMessage(msg)


    print("Connection properties updated and .lyrx file saved successfully.")

if __name__ == "__main__":
    main()
