###############################################################################################################################################################################
#
# Set up the database connection
#
###############################################################################################################################################################################
# database_connection.py
import os
from dotenv import load_dotenv
import arcpy

def setup_bcgw(logger):
    SECRET_FILE = os.getenv('SECRET_FILE')
    if SECRET_FILE:
        load_dotenv(SECRET_FILE)
        logger.info(f"Secret file {SECRET_FILE} found")
    else:
        logger.error("Secret file not found")

    DB_USER = os.getenv('BCGW_USER')
    DB_PASS = os.getenv('BCGW_PASS')
    if DB_USER and DB_PASS:
        logger.info(f"Database user {DB_USER} and password found")
    else:
        logger.error("Database user and password not found")

    current_path = os.path.dirname(os.path.realpath(__file__))
    connection_folder = os.path.join(current_path, 'connection')

    if not os.path.exists(connection_folder):
        logger.info("Connection folder not found, creating new connection folder")
        os.mkdir(connection_folder)

    connection_path = os.path.join(connection_folder, 'bcgw.sde')
    if os.path.exists(connection_path):
        os.remove(connection_path)

    bcgw_con = arcpy.management.CreateDatabaseConnection(
        connection_folder,
        'bcgw.sde',
        'ORACLE',
        'bcgw.bcgov/idwprod1.bcgov',
        'DATABASE_AUTH',
        DB_USER,
        DB_PASS,
        'DO_NOT_SAVE_USERNAME'
    )

    logger.info("New DB connection created")
    arcpy.env.workspace = bcgw_con.getOutput(0)
    logger.info("Workspace set to bcgw connection")

    # Return the connection file path (and credentials if needed)
    return connection_path, [DB_USER, DB_PASS]

###############################################################################################################################################################################
