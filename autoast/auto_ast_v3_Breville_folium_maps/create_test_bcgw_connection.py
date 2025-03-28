###############################################################################################################################################################################
#
# Set up the database connection
#
###############################################################################################################################################################################
import os
from dotenv import load_dotenv
import arcpy

def setup_bcgw():
    # Get the secret file containing the database credentials
    SECRET_FILE = os.getenv('SECRET_FILE')

    # If secret file found, load the secret file and display a print message, if not found display an error message
    if SECRET_FILE:
        load_dotenv(SECRET_FILE)
        print(f"Secret file {SECRET_FILE} found")
        #logger.info(f"Secret file {SECRET_FILE} found")
    else:
        print("Secret file not found")
        #logger.error("Secret file not found")

    # Assign secret file data to variables    
    DB_USER = os.getenv('BCGW_USER')
    DB_PASS = os.getenv('BCGW_PASS')
    

    # If DB_USER and DB_PASS found display a print message, if not found display an error message
    if DB_USER and DB_PASS:
        print(f"Database user {DB_USER} and password found")
        
    else:
        print("Database user and password not found")
        

    # Define current path of the executing script
    current_path = os.path.dirname(os.path.realpath(__file__))

    # Create the connection folder
    connection_folder = 'connection'
    connection_folder = os.path.join(current_path, connection_folder)

    # Check for the existance of the connection folder and if it doesn't exist, print an error and create a new connection folder
    if not os.path.exists(connection_folder):
        print("Connection folder not found, creating new connection folder")
        #logger.info("Connection folder not found, creating new connection folder")
        os.mkdir(connection_folder)

    # Check for an existing bcgw connection, if there is one, remove it
    if os.path.exists(os.path.join(connection_folder, 'bcgw.sde')):
        os.remove(os.path.join(connection_folder, 'bcgw.sde'))

    # Create a bcgw connection
    bcgw_con = arcpy.management.CreateDatabaseConnection(connection_folder,
                                                        'bcgw.sde',
                                                        'ORACLE',
                                                        'bcgw.bcgov/idwprod1.bcgov',
                                                        'DATABASE_AUTH',
                                                        DB_USER,
                                                        DB_PASS,
                                                        'SAVE_USERNAME')
    
    #NOTE - Changed from dont not save username to save username

    print("new db connection created")
    #ogger.info("new db connection created")


    arcpy.env.workspace = bcgw_con.getOutput(0)
    
    sde_path = os.path.join(connection_folder, 'bcgw.sde')

    print("workspace set to bcgw connection")
    #logger.info("workspace set to bcgw connection")
    
    secrets = [DB_USER, DB_PASS]
    sde_connection = arcpy.env.workspace
    
    return secrets, sde_connection, sde_path

###############################################################################################################################################################################
