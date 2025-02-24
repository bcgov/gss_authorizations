# -*- coding: utf-8 -*-
import arcpy
import os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the file name)."""
        self.label = "Repath Layer Files Toolbox"
        self.alias = "RepathLayers"
        self.tools = [RepathLayer]

class RepathLayer(object):
    def __init__(self):
        """Define the tool (tool name is the class name)."""
        self.label = "Repath and Export Layer File"
        self.description = (
            "Repaths the data source of an ArcMap .lyr file so that it points to a "
            "new file geodatabase location and exports it as a .lyrx file. "
            "The tool extracts the geodatabase name from the original data source and "
            "rebuilds the path based on the new data location."
        )
    
    def getParameterInfo(self):
        # Parameter 0: Input Layer File (.lyr)
        param0 = arcpy.Parameter(
            displayName="Input Layer File (.lyr)",
            name="in_layer",
            datatype="DEFile",  # file selection
            parameterType="Required",
            direction="Input"
        )
        param0.filter.list = [".lyr"]

        # Parameter 1: New Data Location
        # This is where the new file geodatabase (with the same name as the old one) resides.
        param1 = arcpy.Parameter(
            displayName="New Data Location",
            name="new_data_location",
            datatype="DEFolder",  # folder selection
            parameterType="Required",
            direction="Input"
        )
        
        # Parameter 2: Output Folder for the repathed layer file (.lyrx)
        param2 = arcpy.Parameter(
            displayName="Output Folder for Repathed Layer",
            name="out_folder",
            datatype="DEFolder",
            parameterType="Required",
            direction="Output"
        )
        
        return [param0, param1, param2]
    
    def isLicensed(self):
        return True

    def updateParameters(self, parameters):
        return

    def updateMessages(self, parameters):
        return

    def execute(self, parameters, messages):
        # Retrieve parameter values.
        in_layer_file = parameters[0].valueAsText
        new_data_location = parameters[1].valueAsText
        out_folder = parameters[2].valueAsText
        
        messages.addMessage("Processing layer file: {}".format(in_layer_file))
        messages.addMessage("New data location: {}".format(new_data_location))
        messages.addMessage("Output folder: {}".format(out_folder))
        
        try:
            # Load the ArcMap .lyr file.
            lyrFile = arcpy.mp.LayerFile(in_layer_file)
        except Exception as e:
            messages.addErrorMessage("Error loading layer file: " + str(e))
            return
        
        # Loop through all top-level layers and update their data sources.
        for lyr in lyrFile.listLayers():
            self.updateLayerSource(lyr, new_data_location, messages)
        
        # Build the output file path: same base name, but with .lyrx extension.
        base_name = os.path.splitext(os.path.basename(in_layer_file))[0]
        out_layer_file = os.path.join(out_folder, base_name + ".lyrx")
        
        try:
            lyrFile.saveACopy(out_layer_file)
            messages.addMessage("Saved updated layer file to: " + out_layer_file)
        except Exception as e:
            messages.addErrorMessage("Error saving updated layer file: " + str(e))
    
    def updateLayerSource(self, lyr, new_data_location, messages):
        """
        Recursively update the data source of a layer.
        If the layer is a group layer, process its sublayers.
        """
        if lyr.isGroupLayer:
            for sublyr in lyr.listLayers():
                self.updateLayerSource(sublyr, new_data_location, messages)
        else:
            current_source = lyr.dataSource
            if current_source and ".gdb" in current_source.lower():
                new_path = self.transformGDBPath(current_source, new_data_location)
                if new_path:
                    # Determine the new workspace and dataset name.
                    idx = new_path.lower().find(".gdb")
                    if idx == -1:
                        messages.addWarningMessage("No .gdb found in transformed path: " + new_path)
                        return
                    new_workspace = new_path[:idx+4]  # include '.gdb'
                    dataset_name = new_path[idx+5:]     # path after the .gdb separator
                    messages.addMessage("Updating layer '{}'".format(lyr.name))
                    messages.addMessage("  Old source: {}".format(current_source))
                    messages.addMessage("  New workspace: {}".format(new_workspace))
                    messages.addMessage("  Dataset name: {}".format(dataset_name))
                    try:
                        # Use "FILEGDB_WORKSPACE" for file geodatabases.
                        lyr.replaceDataSource(new_workspace, "FILEGDB_WORKSPACE", dataset_name, False)
                    except Exception as e:
                        messages.addErrorMessage("Error updating layer '{}': {}".format(lyr.name, str(e)))
            else:
                messages.addMessage("Layer '{}' does not reference a file geodatabase.".format(lyr.name))
    
    def transformGDBPath(self, old_path, new_data_location):
        """
        Transforms an old data source path into a new one based on the new data location.
        
        Assumptions:
          - The original data source (old_path) contains a file geodatabase path (ending in ".gdb").
          - The new file geodatabase will have the same name as the old one.
        
        Example:
          If old_path is "Q:\Data\Project.gdb\FeatureDataset\FeatureClass" and
          new_data_location is "P:\NewData", then the new path becomes:
          "P:\NewData\Project.gdb\FeatureDataset\FeatureClass"
        """
        old_path_norm = os.path.normpath(old_path)
        idx = old_path_norm.lower().find(".gdb")
        if idx == -1:
            return None
        
        # Extract the full path to the old geodatabase.
        old_gdb = old_path_norm[:idx+4]
        # Get the geodatabase name (e.g., "Project.gdb").
        old_gdb_name = os.path.basename(old_gdb)
        # Calculate the relative path within the geodatabase.
        rel_path = os.path.relpath(old_path_norm, old_gdb)
        # Construct the new geodatabase path using the new data location.
        new_gdb = os.path.join(new_data_location, old_gdb_name)
        # Build the complete new data source path.
        new_path = os.path.join(new_gdb, rel_path)
        return new_path
