# autoast is a script for batch processing the automated status tool
# author: csostad and wburt
# copyright Governent of British Columbia
# Copyright 2019 Province of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
from dotenv import load_dotenv
from logging_setup import setup_logging
from database_connection import setup_bcgw
from toolbox_import import import_ast
from ast_factory import AST_FACTORY

# snippet to run multiple terminal windows & "P:\corp\python_ast\python.exe" "W:\srm\nel\Local\Geomatics\Workarea\csostad\GitHubAutoAST\gss_authorizations\autoast\auto_ast_v3_Breville_folium_maps\main.py"


## *** INPUT YOUR EXCEL FILE NAME HERE ***
excel_file_1 = 'mat_excel_1.xlsx' # The name of the excel file containing the jobs to be processed
excel_file_2 = 'mat_excel_2.xlsx' # The name of the second excel file containing the jobs to be processed
excel_file_3 = 'mat_excel_3.xlsx' # The name of the third excel file containing the jobs to be processed
excel_file_4 = ''



#################################################################################################################################################################################
if __name__ == '__main__':
    

    # Call the setup_logging function to log the messages
    logger = setup_logging()

    # Load the default environment
    load_dotenv()

    # Call the import_ast function to import the AST toolbox
    template = import_ast(logger)

    # Call the setup_bcgw function to set up the database connection
    # secrets = setup_bcgw(logger)
    secrets, sde_connection, sde_path = setup_bcgw(logger)
    # username, password = secrets[0], secrets[1]
    
    # Set the SDE path environment variable for easy access by workers
    os.environ["SDE_FILE_PATH"] = sde_path
    logger.info(f"SDE Connection established at: {sde_path}")
    
    # START EXCEL FILE 1
    
    #NOTE if this test works, the following could be wrapped in a function
    # Create the path for the queuefile
    print("Main: Creating queuefile path for Excel File 1")
    logger.info("Main: Creating queuefile path for Excel File 1")   
    
    current_path = os.path.dirname(os.path.realpath(__file__))
    qf = os.path.join(current_path, excel_file_1)

    #qf_1 = os.path.join(current_path, excel_file_1)
    
    # Create an instance of the Ast Factory class, assign the queuefile path and the bcgw username and passwords to the instance
    ast = AST_FACTORY(qf, secrets[0], secrets[1], logger, current_path)
    
    #ast_1 = AST_FACTORY(qf_1, secrets[0], secrets[1], logger, current_path)

    if not os.path.exists(qf):
        print("Main: Queuefile not found, creating new queuefile")
        logger.info("Main: Queuefile not found, creating new queuefile")
        ast.create_new_queuefile()
    
    # if not os.path.exists(qf_1):
    #     print("Main: Queuefile_1 not found, creating new queuefile")
    #     logger.info("Main: Queuefile_1 not found, creating new queuefile")
    #     ast.create_new_queuefile()
        
    # Load the jobs using the load_jobs method. This will scan the excel sheet and assign to "jobs" 
    print("Main: Loading jobs from Excel File 1")
    logger.info("Main: Loading jobs from Excel File 1")   
    jobs = ast.load_jobs()
    
    #jobs = ast_1.load_jobs()
    
    print("Main: Batching jobs for Excel File 1")
    logger.info("Main: Batching jobs for Excel File 1")
    ast.batch_ast()
    
    #ast_1.batch_ast()
    
    print("Main: Reloading failed jobs for Excel File 1")
    logger.info("Main: Reloading failed jobs for Excel File 1")
    ast.re_load_failed_jobs_V2()
    
    #ast_1.re_load_failed_jobs_V2()
    
    print("Main: Re-batching failed jobs for Excel File 1")
    logger.info("Main: Re-batching failed jobs for Excel File 1")
    ast.batch_ast()
    
    #ast_1.batch_ast()
    
    print("Main: AST Factory Excel File 1 COMPLETE")
    logger.info("Main: AST Factory Excel File 1 COMPLETE")
    
    
    ## Start Excel File 2
    
    print("Main: Creating queuefile path for Excel File 2")
    logger.info("Main: Creating queuefile path for Excel File 2")   
    
    current_path = os.path.dirname(os.path.realpath(__file__))
    qf = os.path.join(current_path, excel_file_2)

    # Create an instance of the Ast Factory class, assign the queuefile path and the bcgw username and passwords to the instance
    ast = AST_FACTORY(qf, secrets[0], secrets[1], logger, current_path)

    if not os.path.exists(qf):
        print("Main: Queuefile not found, creating new queuefile")
        logger.info("Main: Queuefile not found, creating new queuefile")
        ast.create_new_queuefile()
        
    # Load the jobs using the load_jobs method. This will scan the excel sheet and assign to "jobs" 
    print("Main: Loading jobs from Excel File 2")
    logger.info("Main: Loading jobs from Excel File 2")   
    jobs = ast.load_jobs()
    
    print("Main: Batching jobs for Excel File 2")
    logger.info("Main: Batching jobs for Excel File 2")
    ast.batch_ast()
    
    print("Main: Reloading failed jobs for Excel File 2")
    logger.info("Main: Reloading failed jobs for Excel File 2")
    ast.re_load_failed_jobs_V2()
    
    print("Main: Re-batching failed jobs for Excel File 2")
    logger.info("Main: Re-batching failed jobs for Excel File 2")
    ast.batch_ast()
    
    print("Main: AST Factory Excel File 2 COMPLETE")
    logger.info("Main: AST Factory Excel File 2 COMPLETE")


## Start Excel File 3
    
    print("Main: Creating queuefile path for Excel File 3")
    logger.info("Main: Creating queuefile path for Excel File 3")   
    
    current_path = os.path.dirname(os.path.realpath(__file__))
    qf = os.path.join(current_path, excel_file_3)

    # Create an instance of the Ast Factory class, assign the queuefile path and the bcgw username and passwords to the instance
    ast = AST_FACTORY(qf, secrets[0], secrets[1], logger, current_path)

    if not os.path.exists(qf):
        print("Main: Queuefile not found, creating new queuefile")
        logger.info("Main: Queuefile not found, creating new queuefile")
        ast.create_new_queuefile()
        
    # Load the jobs using the load_jobs method. This will scan the excel sheet and assign to "jobs" 
    print("Main: Loading jobs from Excel File 3")
    logger.info("Main: Loading jobs from Excel File 3")   
    jobs = ast.load_jobs()
    
    print("Main: Batching jobs for Excel File 3")
    logger.info("Main: Batching jobs for Excel File 3")
    ast.batch_ast()
    
    print("Main: Reloading failed jobs for Excel File 3")
    logger.info("Main: Reloading failed jobs for Excel File 3")
    ast.re_load_failed_jobs_V2()
    
    print("Main: Re-batching failed jobs for Excel File 3")
    logger.info("Main: Re-batching failed jobs for Excel File 3")
    ast.batch_ast()
    
    print("Main: AST Factory Excel File 3 COMPLETE")
    logger.info("Main: AST Factory Excel File 3 COMPLETE")
