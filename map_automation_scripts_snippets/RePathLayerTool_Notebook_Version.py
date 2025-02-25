import arcpy
import os
import sys

def log(msg):
    """
    Helper function to print and also add a message
    so it appears in ArcGIS tool messages.
    """
    print(msg)
    arcpy.AddMessage(msg)

def fix_broken_layers(lyr, old_prefix, new_prefix):
    """
    Recursively fixes broken data sources in a layer.
    If the layer is a group layer, it fixes all sub-layers.
    Returns True if any broken data sources were fixed, False otherwise.
    """
    fixed_any = False

    # If it's a group layer, fix each sub-layer
    if lyr.isGroupLayer:
        for sub_lyr in lyr.listLayers():
            sub_fixed = fix_broken_layers(sub_lyr, old_prefix, new_prefix)
            if sub_fixed:
                fixed_any = True
    else:
        # If it's a single (non-group) layer
        if lyr.isBroken:
            if lyr.supports("DATASOURCE"):
                old_full_path = lyr.dataSource
                log(f"  Found broken data source: {old_full_path}")

                # Check if ".gdb" is in the path
                if ".gdb" in old_full_path:
                    # Extract the workspace up to ".gdb"
                    old_ws = old_full_path.split(".gdb")[0] + ".gdb"

                    # Check if old_prefix is in old_ws
                    if old_prefix in old_ws:
                        new_ws = old_ws.replace(old_prefix, new_prefix)
                        log(f"  Updating connection from:\n    {old_ws}\n  to:\n    {new_ws}")
                        try:
                            lyr.updateConnectionProperties(old_ws, new_ws)
                            log("  Data source successfully updated.")
                            fixed_any = True
                        except Exception as e:
                            log(f"  ERROR updating connection properties: {e}")
                            arcpy.AddError(e)
                    else:
                        log(f"  The old prefix '{old_prefix}' was not found in:\n    {old_ws}")
                else:
                    log("  Could not find '.gdb' in the path; skipping workspace-level update.")
            else:
                log(f"  Layer '{lyr.name}' does not support 'DATASOURCE' property.")
        else:
            log(f"  Layer '{lyr.name}' is not broken; no action needed.")

    return fixed_any

def main():
    # Define the old and new path segments
    oldPrefix = r"Q:\dsswhse\Data"
    newPrefix = r"\\giswhse.env.gov.bc.ca\whse_np\corp\cartographic_resources\data_whse"

    # Folder for saving the .lyrx files
    output_dir = r"C:\Users\CSOSTAD\Desktop\LayerFileExportTest"

    # Attempt to reference the current ArcGIS Pro project
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        log("Successfully referenced the current ArcGIS Pro project.")
    except Exception as e:
        log(f"ERROR: Could not reference the current ArcGIS Pro project.\n{e}")
        arcpy.AddError(e)
        sys.exit(1)

    # List the maps
    maps = aprx.listMaps()
    if not maps:
        log("No maps found in the current project.")
        return

    for m in maps:
        log(f"\n--- Checking map: {m.name} ---")

        # Instead of using 'recursive=False', we list all layers
        # then filter to find only those that are top-level.
        try:
            all_layers = m.listLayers()
        except Exception as e:
            log(f"ERROR: Could not list layers in map '{m.name}'.\n{e}")
            arcpy.AddError(e)
            continue

        if not all_layers:
            log(f"  Map '{m.name}' has no layers.")
            continue

        # Identify only top-level layers by checking the 'longName'
        top_level_layers = []
        for lyr in all_layers:
            # If a layer is truly top-level, then lyr.longName == lyr.name
            # Alternatively, we can check if "\\" is in lyr.longName
            # but direct equality is usually simpler in Pro
            if lyr.longName == lyr.name:
                top_level_layers.append(lyr)

        for lyr in top_level_layers:
            layer_name = lyr.name
            log(f"Layer: {layer_name}")

            # Fix broken data sources for this layer (and its sub-layers if it's a group)
            try:
                fix_broken_layers(lyr, oldPrefix, newPrefix)
            except Exception as e:
                log(f"  ERROR: Could not fix broken layers for '{layer_name}'.\n{e}")
                arcpy.AddError(e)

            # Now export THIS layer (which includes all sub-layers if it's a group)
            layer_filename = f"{layer_name}.lyrx"
            layer_file_path = os.path.join(output_dir, layer_filename)

            try:
                log(f"  Saving the layer (and any sub-layers) to:\n    {layer_file_path}")
                arcpy.management.SaveToLayerFile(lyr, layer_file_path, "RELATIVE")
            except Exception as e:
                log(f"  ERROR: Could not save layer file for '{layer_name}'.\n{e}")
                arcpy.AddError(e)



if __name__ == "__main__":
    main()
