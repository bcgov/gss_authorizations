import arcpy, os

featureClass = 'WoodedAreas_50k'
oldFileGDB = r'Q:\dsswhse\Data\Base\Base50\Wooded Areas\BC_Wooded_Areas_50k.gdb'
newFileGDB = r'\\giswhse.env.gov.bc.ca\whse_np\corp\cartographic_resources\data_whse\Base\Base50\Wooded Areas\BC_Wooded_Areas_50k.gdb'
output_layer_file = r"C:/Users/CSOSTAD/Desktop/LayerFileExportTest/woodstest"

# Reference project
aprx = arcpy.mp.ArcGISProject("CURRENT")

# Search for specific broken layers
for map in aprx.listMaps():
    for lyr in map.listLayers():
        if lyr.isBroken:
            print("Found Broken layers")
            if lyr.supports("DATASOURCE"):
                if lyr.dataSource == os.path.join(oldFileGDB, featureClass):
                    print("Updating Connection Properties")
                    lyr.updateConnectionProperties(oldFileGDB, newFileGDB)
                    print("Saving layer to file")
                    arcpy.management.SaveToLayerFile(lyr, output_layer_file, "RELATIVE")