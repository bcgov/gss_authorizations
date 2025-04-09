import arcpy
import os
import sys

def log(msg):
    """
    Helper function: prints to console and also adds a message
    so it appears in ArcGIS tool messages.
    """
    print(msg)
    arcpy.AddMessage(msg)

def fix_broken_layers(lyr, old_prefixes, new_prefix):
    """
    Recursively fix broken layers. If a layer is a group layer, we
    fix each sub-layer by calling this function again.
    Returns True if any broken data sources were fixed, False otherwise.
    """
    fixed_any = False

    # If it's a group layer, go through all its sub-layers
    if lyr.isGroupLayer:
        sublayers = lyr.listLayers()
        for sub_lyr in sublayers:
            sub_fixed = fix_broken_layers(sub_lyr, old_prefixes, new_prefix)
            if sub_fixed:
                fixed_any = True
        # No direct 'datasource' fix for the group layer itself,
        # so just pass through here.
    else:
        # Check if the layer is broken
        if lyr.isBroken:
            if lyr.supports("DATASOURCE"):
                old_full_path = lyr.dataSource
                log(f"  Found broken data source: {old_full_path}")

                # Check if ".gdb" is present
                # e.g. Q:\dsswhse\Data\Base\Base20\Base20.gdb
                # or \\spatialfiles.bcgov\work\ilmb\dss\dsswhse\Data\Base
                if ".gdb" in old_full_path:
                    # Extract workspace up to ".gdb"
                    old_ws = old_full_path.split(".gdb")[0] + ".gdb"
                    
                    # Try each old prefix until we find a match
                    replaced = False
                    for prefix in old_prefixes:
                        if prefix in old_ws:
                            new_ws = old_ws.replace(prefix, new_prefix)
                            log(f"  Updating connection from:\n    {old_ws}\n  to:\n    {new_ws}")
                            try:
                                # Update at the workspace level
                                lyr.updateConnectionProperties(old_ws, new_ws)
                                log("  Data source successfully updated.")
                                fixed_any = True
                                replaced = True
                            except Exception as e:
                                log(f"  ERROR updating connection properties: {e}")
                                arcpy.AddError(e)
                            break  # Stop once we've done the first successful replacement

                    if not replaced:
                        log(f"  None of the old prefixes {old_prefixes} were found in:\n    {old_ws}")

                else:
                    log("  Could not find '.gdb' in the path; skipping workspace-level update.")
            else:
                log(f"  Layer '{lyr.name}' does not support DATASOURCE property.")
        else:
            log(f"  Layer '{lyr.name}' is not broken; no action needed.")

    return fixed_any

def main():
    # We have TWO old prefixes: Q: drive and an older UNC path
    oldPrefix_Q = r"Q:\dsswhse\Data\Base"
    oldPrefix_UNC = r"\\spatialfiles.bcgov\work\ilmb\dss\dsswhse\Data\Base"
    oldPrefix_workarea = r"\\spatialfiles.bcgov\work\srm\nel\Local\Geomatics\Workarea\Data\Base"
    

    # Put them in a list so we can check each one
    old_prefixes = [oldPrefix_Q, oldPrefix_UNC, oldPrefix_workarea]
    
    # This is your NEW prefix path
    newPrefix = r"\\giswhse.env.gov.bc.ca\whse_np\corp\cartographic_resources\data_whse\Base"
    
    # Folder where you want to save the .lyrx files
    output_dir = r"C:\Users\CSOSTAD\Desktop\LayerFileExportTest\Mar31"

    # Attempt to get the current ArcGIS Pro project
    try:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        log("Successfully referenced the current ArcGIS Pro project.")
    except Exception as e:
        log(f"ERROR: Could not reference the current ArcGIS Pro project.\n{e}")
        arcpy.AddError(e)
        sys.exit(1)

    # Iterate through each map in the project
    maps = aprx.listMaps()
    if not maps:
        log("No maps found in the current project.")
        return

    for m in maps:
        log(f"\n--- Checking map: {m.name} ---")

        layers = m.listLayers()
        if not layers:
            log(f"Map '{m.name}' has no layers.")
            continue

        # For each top-level layer, fix data sources (recursively if needed)
        # and then export the entire layer (group or single) as a .lyrx file.
        for lyr in layers:
            log(f"Layer: {lyr.name}")

            # Fix broken sub-layers (if it's a group) or the layer itself
            try:
                fix_broken_layers(lyr, old_prefixes, newPrefix)
            except Exception as e:
                log(f"  ERROR: Could not fix broken layers for '{lyr.name}'.\n{e}")
                arcpy.AddError(e)

            # After fixing, export the whole top-level layer as a single .lyrx
            layer_filename = f"{lyr.name}.lyrx"
            layer_file_path = os.path.join(output_dir, layer_filename)

            try:
                log(f"  Saving entire layer (with sub-layers) to:\n    {layer_file_path}")
                arcpy.management.SaveToLayerFile(lyr, layer_file_path, "RELATIVE")
            except Exception as e:
                log(f"  ERROR: Could not save layer file for '{lyr.name}'.\n{e}")
                arcpy.AddError(e)

    # Optionally, you can save the project to preserve changes in the .aprx
    # try:
    #     aprx.saveACopy(r"C:\Users\CSOSTAD\Desktop\LayerFileExportTest\UpdatedProject.aprx")
    #     log("Saved a copy of the project with updated layers.")
    # except Exception as e:
    #     log(f"ERROR: Could not save a copy of the project.\n{e}")
    #     arcpy.AddError(e)

if __name__ == "__main__":
    main()
