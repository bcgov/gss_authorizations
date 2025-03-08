import sys

def process_job_mp(ast_instance, job, job_index, current_path, connection_path, return_dict):
    import os, arcpy, datetime, logging, traceback, multiprocessing as mp

    # configure logging first (as previously done)
    log_folder = os.path.join(current_path, f'autoast_logs_{datetime.datetime.now().strftime("%Y%m%d")}')
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)

    log_file = os.path.join(
        log_folder,
        f'ast_worker_log_{datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")}_{mp.current_process().pid}_job_{job_index}.log'
    )

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(f"worker_{job_index}")
    logger.info("##########################################################################################################################")
    logger.info("#")
    logger.info("Running Multiprocessing Worker Function.....")
    logger.info("#")
    logger.info("##########################################################################################################################")
    print(f"Process Job Mp: Processing job {job_index}: {job}")

    logger.info(f"Worker process {mp.current_process().pid} started for job {job_index}")
    
      # set workspace to shared connection
    arcpy.env.workspace = connection_path
    logger.info(f"Workspace set to: {connection_path}")

    try:
        # import toolbox and run your tool using job parameters
        ast_toolbox = os.getenv('TOOLBOX')
        ast_toolbox_alias = os.getenv('TOOLBOXALIAS')

        if ast_toolbox:
            arcpy.ImportToolbox(ast_toolbox, ast_toolbox_alias)
            logger.info("AST Toolbox imported successfully.")
        else:
            raise ImportError("TOOLBOX path missing.")

        params = [job.get(param, '') for param in ast_instance.AST_PARAMETERS.values()]

        arcpy.alphaast.MakeAutomatedStatusSpreadsheet(*params)
        logger.info("MakeAutomatedStatusSpreadsheet executed successfully.")

        ast_instance.add_job_result(job_index, 'COMPLETE')
        return_dict[job_index] = 'Success'

    except Exception as e:
        return_dict[job_index] = 'Failed'
        logger.error(f"Job {job_index} failed with error: {e}")
        logger.debug(traceback.format_exc())
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"Traceback:\n{traceback_str}")
