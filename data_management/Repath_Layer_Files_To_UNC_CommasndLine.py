import arcpy
import os
import sys

def log(msg):
    """
    Helper function to print to console and also add a message
    so it appears in ArcGIS tool messages (if running inside an ArcGIS Tool).
    """
    print(msg)
    try:
        arcpy.AddMessage(msg)
    except:
        # If ArcPy environment isn't fully active, this may fail gracefully
        pass

def fix_broken_layers(lyr, old_prefixes, new_prefix):
    """
    Recursively fix broken data sources in a layer.
    If the layer is a group layer, it fixes all sub-layers.
    Returns True if any broken data sources were fixed, False otherwise.
    """
    fixed_any = False

    # If it's a group layer, go through all its sub-layers
    if lyr.isGroupLayer:
        for sub_lyr in lyr.listLayers():
            sub_fixed = fix_broken_layers(sub_lyr, old_prefixes, new_prefix)
            if sub_fixed:
                fixed_any = True
    else:
        # If it's a single (non-group) layer
        if lyr.isBroken:
            if lyr.supports("DATASOURCE"):
                old_full_path = lyr.dataSource
                log(f"  Found broken data source: {old_full_path}")

                if ".gdb" in old_full_path:
                    # Extract workspace up to ".gdb"
                    old_ws = old_full_path.split(".gdb")[0] + ".gdb"

                    replaced = False
                    # Try each old prefix in the list
                    for prefix in old_prefixes:
                        if prefix in old_ws:
                            new_ws = old_ws.replace(prefix, new_prefix)
                            log(f"  Updating connection from:\n    {old_ws}\n  to:\n    {new_ws}")
                            try:
                                lyr.updateConnectionProperties(old_ws, new_ws)
                                log("  Data source successfully updated.")
                                replaced = True
                                fixed_any = True
                            except Exception as e:
                                log(f"  ERROR updating connection properties: {e}")
                            break

                    if not replaced:
                        log(f"  None of the old prefixes {old_prefixes} were found in:\n    {old_ws}")
                else:
                    log("  Could not find '.gdb' in the path; skipping workspace-level update.")
            else:
                log(f"  Layer '{lyr.name}' does not support 'DATASOURCE' property.")
        else:
            log(f"  Layer '{lyr.name}' is not broken; no action needed.")

    return fixed_any

def main():
    # ----------------------------------------------------------------------
    # 1) Parse input arguments or prompt the user
    # ----------------------------------------------------------------------
    if len(sys.argv) < 3:
        log("Usage: python repath_script.py <path_to_aprx> <output_directory>")
        log("Example: python repath_script.py C:\\Projects\\MyMap.aprx C:\\Temp\\OutputLayers")
        sys.exit(1)
    
    aprx_path = sys.argv[1]
    output_dir = sys.argv[2]

    # Optionally, define your old/new prefixes here OR prompt for more arguments
    old_prefixes = [
        r"Q:\dsswhse\Data\Base",
        r"\\spatialfiles.bcgov\work\ilmb\dss\dsswhse\Data\Base",
        r"\\spatialfiles.bcgov\work\srm\nel\Local\Geomatics\Workarea\Data\Base"
    ]
    new_prefix = r"\\giswhse.env.gov.bc.ca\whse_np\corp\cartographic_resources\data_whse\Base"

    # ----------------------------------------------------------------------
    # 2) Validate inputs
    # ----------------------------------------------------------------------
    if not os.path.isfile(aprx_path):
        log(f"ERROR: Project file not found: {aprx_path}")
        sys.exit(1)

    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir)
            log(f"Created output directory: {output_dir}")
        except Exception as e:
            log(f"ERROR: Could not create output directory: {output_dir}\n{e}")
            sys.exit(1)

    # ----------------------------------------------------------------------
    # 3) Open the APRX outside of ArcGIS Pro
    # ----------------------------------------------------------------------
    try:
        aprx = arcpy.mp.ArcGISProject(aprx_path)
        log(f"Opened ArcGIS Pro project: {aprx_path}")
    except Exception as e:
        log(f"ERROR: Could not open APRX file.\n{e}")
        sys.exit(1)

    # ----------------------------------------------------------------------
    # 4) Fix broken data sources in each map
    # ----------------------------------------------------------------------
    for m in aprx.listMaps():
        log(f"\n--- Checking map: {m.name} ---")
        all_layers = m.listLayers()
        if not all_layers:
            log(f"  Map '{m.name}' has no layers.")
            continue

        # First, fix all layers recursively
        for lyr in all_layers:
            try:
                fix_broken_layers(lyr, old_prefixes, new_prefix)
            except Exception as e:
                log(f"  ERROR: Could not fix broken layers for '{lyr.name}'.\n{e}")

        # Then identify only top-level layers
        top_level_layers = [lyr for lyr in all_layers if lyr.longName == lyr.name]

        # Export each top-level layer to a .lyrx
        for lyr in top_level_layers:
            layer_filename = f"{lyr.name}.lyrx"
            layer_file_path = os.path.join(output_dir, layer_filename)
            log(f"\n  Saving TOP-LEVEL layer '{lyr.name}' to:\n    {layer_file_path}")

            try:
                arcpy.management.SaveToLayerFile(lyr, layer_file_path, "RELATIVE")
            except Exception as e:
                log(f"  ERROR: Could not save layer file for '{lyr.name}'.\n{e}")

    # ----------------------------------------------------------------------
    # 5) Optionally save a copy of the .aprx
    # ----------------------------------------------------------------------
    # out_aprx_copy = os.path.join(output_dir, "UpdatedProject.aprx")
    # try:
    #     aprx.saveACopy(out_aprx_copy)
    #     log(f"Saved a copy of the project to: {out_aprx_copy}")
    # except Exception as e:
    #     log(f"ERROR: Could not save a copy of the project.\n{e}")

    log("\nDone. All broken layers processed and top-level layers exported.")

if __name__ == "__main__":
    main()
