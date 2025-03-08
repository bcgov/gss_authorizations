###############################################################################################################################################################################
#
# Set up the database connection
#
###############################################################################################################################################################################
def setup_bcgw(logger):
    import os
    from dotenv import load_dotenv
    import arcpy

    SECRET_FILE = os.getenv('SECRET_FILE')
    if SECRET_FILE:
        load_dotenv(SECRET_FILE)
        logger.info(f"Secret file {SECRET_FILE} loaded.")
    else:
        logger.error("Secret file not found.")

    DB_USER = os.getenv('BCGW_USER')
    DB_PASS = os.getenv('BCGW_PASS')

    current_path = os.path.dirname(os.path.realpath(__file__))
    connection_folder = os.path.join(current_path, 'connection')

    if not os.path.exists(connection_folder):
        os.makedirs(connection_folder)

    connection_path = os.path.join(connection_folder, 'bcgw.sde')
    if os.path.exists(connection_path):
        os.remove(connection_path)

    arcpy.management.CreateDatabaseConnection(
        connection_folder=connection_folder,
        out_name='bcgw.sde',
        database_platform='ORACLE',
        instance='bcgw.bcgov/idwprod1.bcgov',
        account_authentication='DATABASE_AUTH',
        username=DB_USER,
        password=DB_PASS,
        save_user_pass='SAVE_USERNAME'  # or 'DO_NOT_SAVE_USERNAME' if you don't want credentials saved
    )

    logger.info(f"Database connection created at: {connection_path}")

    return connection_path

import arcpy

def get_sde_credentials(sde_file_path):
    """Extracts credentials from the provided .sde file."""
    try:
        conn_props = arcpy.Describe(sde_file_path).connectionProperties
        username = conn_props.userName
        password = conn_props.password
        return username, password
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve credentials from {sde_file_path}: {e}")

