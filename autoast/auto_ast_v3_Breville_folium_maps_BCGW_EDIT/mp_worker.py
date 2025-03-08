import sys

def process_job_mp(ast_instance, job, job_index, current_path, connection_path, return_dict):
    import os
    import arcpy
    import datetime
    import logging
    import multiprocessing as mp
    import traceback

    # Set up a log folder and unique log file path for this worker process
    log_folder = os.path.join(current_path, f'autoast_logs_{datetime.datetime.now().strftime("%Y%m%d")}')
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    log_file = os.path.join(
        log_folder,
        f'ast_worker_log_{datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")}_{mp.current_process().pid}_job_{job_index}.log'
    )
    
    # Configure logging for this worker process before any logging calls
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Now get a logger and start logging
    logger = logging.getLogger(f"Process Job Mp: worker_{job_index}")
    logger.info("##########################################################################################################################")
    logger.info("#")
    logger.info("Running Multiprocessing Worker Function.....")
    logger.info("#")
    logger.info("##########################################################################################################################")
    print(f"Process Job Mp: Processing job {job_index}: {job}")

    logger.info(f"Worker process {mp.current_process().pid} started for job {job_index}")
    
    # Set the arcpy workspace to the shared connection file so that no new connection is created
    arcpy.env.workspace = connection_path
    logger.info(f"arcpy.env.workspace set to connection path: {connection_path}")

    try:
        # Re-import the toolbox in each process
        ast_toolbox = os.getenv('TOOLBOX')
        ast_toolbox_alias = os.getenv('TOOLBOXALIAS')
        if ast_toolbox:
            arcpy.ImportToolbox(ast_toolbox, ast_toolbox_alias)
            print("Process Job Mp: AST Toolbox imported successfully in worker.")
            logger.info("AST Toolbox imported successfully in worker.")
        else:
            raise ImportError("AST Toolbox path not found. Ensure TOOLBOX path is set correctly in environment variables.")

        # Prepare parameters
        params = []
        for param in ast_instance.AST_PARAMETERS.values():
            value = job.get(param)
            if isinstance(value, str) and value.lower() in ['true', 'false']:
                value = True if value.lower() == 'true' else False
            params.append(value)
        
        output_directory = job.get('output_directory')
        if output_directory and not os.path.exists(output_directory):
            try:
                os.makedirs(output_directory)
                print(f"Output directory '{output_directory}' created.")
                logger.warning(f"Output directory didn't exist for job {job_index}. Created '{output_directory}'.")
            except OSError as e:
                raise RuntimeError(f"Failed to create the output directory '{output_directory}'. Check permissions: {e}")

        if not job.get('region'):
            raise ValueError("Region is required and was not provided. Job Failed")

        logger.debug(f"Job Parameters: {params}")

        logger.info("Running MakeAutomatedStatusSpreadsheet_ast...")
        arcpy.alphaast.MakeAutomatedStatusSpreadsheet(*params)
        logger.info("MakeAutomatedStatusSpreadsheet_ast completed successfully.")
        ast_instance.add_job_result(job_index, 'COMPLETE')

        logger.info("Capturing arcpy messages...")
        arcpy_messages = arcpy.GetMessages(0)
        arcpy_warnings = arcpy.GetMessages(1)
        arcpy_errors = arcpy.GetMessages(2)

        if arcpy_messages:
            logger.info(f'arcpy messages: {arcpy_messages}')
        if arcpy_warnings:
            logger.warning(f'arcpy warnings: {arcpy_warnings}')
        if arcpy_errors:
            logger.error(f'arcpy errors: {arcpy_errors}')
        
        return_dict[job_index] = 'Success'

    except Exception as e:
        return_dict[job_index] = 'Failed'
        logger.error(f"Job {job_index} failed with error: {e}")
        logger.debug(traceback.format_exc())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"Traceback:\n{traceback_str}")
