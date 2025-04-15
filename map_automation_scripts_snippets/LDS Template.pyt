# ArcGIS Pro 3 Toolbox Template

#===========================================================================
# Script name: Arcgis Pro 3 Toolbox Template
# Author: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm

# Created on: 10/21/2024

#New sample changes
# 
#

# 
#
# 
#============================================================================

#import all necessary libraries 
import arcpy 
import traceback 
import sys 
import os 
import datetime
import openpyxl as xl






    
    
############################################################################################################################################################################
#
# Known Issues
#
############################################################################################################################################################################







############################################################################################################################################################################
#
# Define Global Variables to be used in the various versions of the Export Layout Tools
#
############################################################################################################################################################################
arcpy.AddMessage("         Setting up global variables")
# Set up variables for the various layers to be turned on and off in the site map
layers_for_site = ["Base Map Auto Scale (1:7,500,000-1:20,000)", "0-7.5K SITE MAP", "7.5-15K SITE MAP", "15-35K SITE MAP", "35-75K SITE MAP", "75-400K SITE MAP", "centroid", "baseDataText", "ALL Freshwater Atlas Labels GROUP"]
layers_for_imagery = ["Latest BC RGB Spot"]

# Set up variables for the various text elements to be turned on and off in the imagery site map
elements_for_inset = ["Inset Map Words", "Inset Map Dynamic Scale"]

# Get the current date to be used in naming of the pdf 
current_date = datetime.datetime.now()
formatted_date = current_date.strftime("%b%Y")

# Assign the layout names to variables
site_layout = "LDS Letter"
overview_layout = "REFERRAL"

#assign variables to identify aprx project, and map 
aprx = arcpy.mp.ArcGISProject("CURRENT")
site_map = aprx.listMaps('LDS Map')[0] 
inset_map = aprx.listMaps('LDS Inset')[0]
overview_map = aprx.listMaps('Referral Map')[0]
# overview_inset_map = aprx.listMaps('OverviewInsetMap')[0]
lands_file_path = r'\\spatialfiles.bcgov\srm\gss\authorizations\land\2025\cariboo'
site_map_frame = 'Map Frame'
site_map_inset_frame = 'Inset Map' # Could assign these strings to objects right here  
overview_map_frame = 'Referral Map Map Frame'
overview_map_inset_frame = 'Inset Data Frame Map Frame'

# Assign Application to Layer for the Export tool. This will be removed later if integrated with the Site and Overview tool
layer = site_map.listLayers("Interest Area - Crown Tenures")[0] #This could cause issues in other scripts if Application is not the key layer

# Duplicated Interest Area layer and renamed to layer below
crown_tenures_layer = site_map.listLayers("WHSE_TANTALIS.TA_CROWN_TENURES_SVW")[0]


############################################################################################################################################################################
#
# Set up global functions to be used in the various versions of the Export Layout Tools
#
############################################################################################################################################################################


arcpy.AddMessage("         Setting up global functions")
# Global exportToPdf function
def exportToPdf(layout, workSpace_path, pdf_file_name):
    out_pdf = f"{workSpace_path}\\{pdf_file_name}"
    layout.exportToPDF(
        out_pdf=out_pdf,
        resolution=300,  # DPI
        image_quality="BETTER",
        jpeg_compression_quality=80  # Quality (0 to 100)
    )

# This function will turn on the site map layers, turn on the inset map and turn off the imagery layers
# Currently not used
def turn_on_site_map_with_inset():
    global site_layout
    # Step 1 - LAYERS - Turn off the imagery layers and turn ON the site map layers
    for lyr in site_map.listLayers():
        if lyr.name in layers_for_imagery:
            lyr.visible = False
        elif lyr.name in layers_for_site:
            lyr.visible = True

    # Step 2 - TEXT ELEMENTS - Turn off the imagery related elements (Imagery Credits and ImageryNA)
    for lyt in aprx.listLayouts(site_layout):
        for elm in lyt.listElements("TEXT_ELEMENT"):
            if elm.name == "Imagery Credits":
                
                elm.visible = False
            
            if elm.name == "ImageryNA":
                elm.text = "Imagery: NA"
                
        if elm.name in elements_for_inset:
            elm.visible = True # Turn the inset map elements back on

    # Step 3 - MAPFRAME ELEMENTS - Turn on the inset map and extent indicator            
    for elm in lyt.listElements("MAPFRAME_ELEMENT"):
            if elm.name == "Inset Data Frame Map Frame":
                elm.visible = True # Turn the inset map back on
            elif elm.name == "ExtentIndicator":
                elm.visible = True # Turn the extent indicator back on
 
 
#This function will turn on the inset map and associated supporting elements
def turn_on_inset(layout_to_turn_on):
   
    for lyt in aprx.listLayouts(layout_to_turn_on):         
        for elm in lyt.listElements("MAPFRAME_ELEMENT"):
                if elm.name == "Inset Data Frame Map Frame":
                    elm.visible = True # Turn the inset map back on
                elif elm.name == "ExtentIndicator":
                    elm.visible = True # Turn the extent indicator on 
        for elm in lyt.listElements("TEXT_ELEMENT"):
                if elm.name in elements_for_inset:
                    elm.visible = True # Turn the inset map elements on
        for elm in lyt.listElements("GRAPHIC_ELEMENT"):
                if elm.name == "Inset Map Scale Rectangle":
                    elm.visible = True # Turn the scale rectangle on

#This function will turn off the inset map and associated supporting elements
def turn_off_inset(layout_to_turn_off):
   
    for lyt in aprx.listLayouts(layout_to_turn_off):         
        for elm in lyt.listElements("MAPFRAME_ELEMENT"):
                if elm.name == "Inset Data Frame Map Frame":
                    elm.visible = False # Turn the inset map back off
                elif elm.name == "ExtentIndicator":
                    elm.visible = False # Turn the extent indicator off 
                elif elm.name == "Inset Map Scale Rectangle":
                    elm.visible = False # Turn the scale rectangle off
        for elm in lyt.listElements("TEXT_ELEMENT"):
                if elm.name in elements_for_inset:
                    elm.visible = False # Turn the inset map elements off
        for elm in lyt.listElements("GRAPHIC_ELEMENT"):
                if elm.name == "Inset Map Scale Rectangle":
                    elm.visible = False # Turn the scale rectangle on
                
# This function will turn on the site map layers and turn off the imagery layers
def turn_on_site_map():
    
    global site_layout, aprx
    # Step 1 - LAYERS - Turn off the imagery layers and turn ON the site map layers
    for lyr in site_map.listLayers():
        if lyr.name in layers_for_imagery:
            lyr.visible = False
        elif lyr.name in layers_for_site:
            lyr.visible = True

    # Step 2 - TEXT ELEMENTS - Turn off the imagery related elements (Imagery Credits and ImageryNA)
    for lyt in aprx.listLayouts(site_layout):
        
        
        for elm in lyt.listElements("TEXT_ELEMENT"):
            
            if elm.name == "Imagery Credits":
                
                elm.visible = False
            
            if elm.name == "ImageryNA":
                elm.text = "Imagery: NA"
                

# This function will turn on the imagery layers and turn off the site map layers and update the necessary text elements
def turn_on_imagery():
    global site_layout # IS IT BETTER TO DO IT THIS WAY OR TO PASS IN THE LAYOUT AS A PARAMETER?
    for lyr in site_map.listLayers():
        if lyr.name in layers_for_imagery: # If the any of the layers are in the list of layers defined in the layer for imagery variable, turn it on
            lyr.visible = True #Turn on the imagery layers
        
        elif lyr.name in layers_for_site: # If the layer name is in the list of layers defined in the layer for site variable, turn it off
            lyr.visible = False # Turn off the site map layers
        
    #Iterate through the list elements in the layout and find the text element named "Imagery Credits" and turn it on, find ImageryNA and replace NA with Spot 2021
    for lyt in aprx.listLayouts(site_layout):
        arcpy.AddMessage(f"Layout name is: {lyt.name}")
        for elm in lyt.listElements("TEXT_ELEMENT"):
            #arcpy.AddMessage(f"Text element name is: {elm.name}")
            if elm.name == "Imagery Credits":
                arcpy.AddMessage("Imagery Credits found")
                elm.visible = True
            elif elm.name == "ImageryNA":
                arcpy.AddMessage("IMAGERY: N/A found")
                elm.text = "Imagery: Spot 2021"
            

# Function to zoom to feature extent
def zoom_to_feature_extent(map_name, map_frame, layer_name, zoom_factor, layout_name):


    ''' This function will focus the layout on the selected feature and then pan out x% (depending on zoom factor) 
    to show the surrounding area. If you use an 0.8 (80%) Zoom Factor, to calculate the zoom percentage: Original zoom 
    is 100% (the initial extent of the splitline layer).The new extent is 160% larger than the original. This is because 
    you are adding 80% of the width to both sides (left and right) and 80% of the height to both top and bottom.'''\
        
    arcpy.AddMessage("         Running zoom_to_feature_extent function")
    # Verify layout existence
    layouts = aprx.listLayouts(layout_name)
    if not layouts:
        arcpy.AddError(f"No layout found with the name: {layout_name}")
        return
    lyt_name = layouts[0]

    # Verify map frame existence
    map_frames = lyt_name.listElements("MAPFRAME_ELEMENT", map_frame)
    if not map_frames:
        arcpy.AddError(f"No map frame found with the name: {map_frame} in layout: {layout_name}")
        return
    mf = map_frames[0]

    # Verify layer existence
    maps = aprx.listMaps(map_name)
    if not maps:
        arcpy.AddError(f"No map found with the name: {map_name}")
        return
    map_obj = maps[0]
    layers = map_obj.listLayers(layer_name)
    if not layers:
        arcpy.AddError(f"No layer found with the name: {layer_name} in map: {map_name}")
        return
    lyr_name = layers[0]

    # Get and adjust the extent
    try:
        current_extent = mf.getLayerExtent(lyr_name, False, True)
        x_min = current_extent.XMin - (current_extent.width * zoom_factor)
        y_min = current_extent.YMin - (current_extent.height * zoom_factor)
        x_max = current_extent.XMax + (current_extent.width * zoom_factor)
        y_max = current_extent.YMax + (current_extent.height * zoom_factor)
        new_extent = arcpy.Extent(x_min, y_min, x_max, y_max)
        mf.camera.setExtent(new_extent)
        arcpy.AddMessage(f"         Zoomed to {layer_name} with zoom factor {zoom_factor}")
        # # Get the current scale of the map frame
        # current_scale = mf.camera.getScale()
        # arcpy.AddMessage(f"Current scale is: {current_scale}")
        # # Round the scale to the nearest 10,000
        # rounded_scale = round(current_scale / 10000) * 10000
        # arcpy.AddMessage(f"Rounded scale is: {rounded_scale}")
        # # Set the map frame to the new rounded scale
        # mf.camera.setScale(rounded_scale)
        # arcpy.AddMessage(f'Zooming the map to the new scale of {rounded_scale}')
        
    except Exception as e:
        arcpy.AddError(f"Error in zooming to extent: {str(e)}")

def format_dms(dms_str):
    '''
    The purpose of the format_dms function is to format coordinates (DMS) 
    format and round the seconds to two decimals.
    '''
    parts = dms_str.split()
    
    # Check if the dms_str has the expected format
    if len(parts) != 3:
        raise ValueError("Invalid DMS format in the centroid layer. It should have three parts separated by whitespace.")
    
    # The split() method splits the string at whitespace characters. The result of the split() method is assigned to the parts variable, 
    # which becomes a list containing the individual parts of the dms_str string.The code then extracts specific parts from the parts list using indexing.
    parts = dms_str.split()
    degrees, minutes, seconds_with_dir = parts[0], parts[1], parts[2]
    arcpy.AddMessage("         Function to truncate seconds to two decimal places is running.....")


    
    # Split seconds and direction into two parts. The seconds and the direction. Seconds is obtained by slicing the seconds with dir string 
    # from the beginning to the second last character. The direction is obtained by slicing the seconds with dir string from the last character.
    seconds, direction = seconds_with_dir[:-1], seconds_with_dir[-1]

    # The code then truncates the seconds to two decimal places using the float function and string formatting.
    truncated_seconds = f"{float(seconds):.2f}"

    # The code then constructs the formatted DMS by combining the degrees, minutes, truncated seconds, and direction.
    formatted_dms = f"{degrees} {minutes} {truncated_seconds}\"{direction}"
    
    # The code then returns the formatted DMS.
    return formatted_dms


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Descriptive Name of your Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [NameOfYourTool, MySecondTool]  
        # Insert the name of each tool in your toolbox if you have more than one. 
        # i.e. self.tools = [FullSiteOverviewMaps, ExportSiteAndImageryLayout, Amendment]


class NameOfYourTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""

    def getParameterInfo(self):
        """This function assigns parameter information for tool""" 
        
        
    def getParameterInfo(self):
        """This function assigns parameter information for tool""" 
        #This parameter is the file number of the application
        file_num = arcpy.Parameter(
            displayName = "Crown Land File Number",
            name="file_num",
            datatype="String",
            parameterType="Required",
            direction="Input")

        parameters = [file_num]

        return parameters
       


    
    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True
    

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    
    #NOTE This is where you cut a past your code
    def execute(self, parameters, messages):
        
        arcpy.AddMessage("         Setting up global variables")
        """The source code of the tool."""
        
        
        # Bring in parameters to the function to be used as variables 
        file_num = parameters[0].valueAsText
        arcpy.AddMessage(f"File number is: {file_num}")
        
        # Now write your script
        arcpy.AddMessage(f"Hello World, the file number is {file_num}")
        
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
    
#NOTE add another tool to the toolbox if you want
class MySecondTool(object):
    def __init__(self):
        
        """This tool will prep all required data for an individual crown tenure - to be used to add/subtract amendment - it will create the 
        amendment polygon, centroid, and splitline, and calculate geometries for centroid and splitline"""
        
        self.label = "Descriptive Name of your Second Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """This function assigns parameter information for tool""" 
        
        
        #This parameter is the file number of the application
        amend_file_num = arcpy.Parameter(
            displayName = "Lands Amendment File Number",
            name="file_num",
            datatype="String",
            parameterType="Required",
            direction="Input")
        
        parameters = [amend_file_num] #Each parameter name needs to be in here, separated by a comma

        return parameters

    
