# autoast is a script for batch processing the automated status tool
# author: csostad and wburt
# copyrite Governent of British Columbia
# Copyright 2019 Province of British Columbia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at 
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
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

## *** INPUT YOUR EXCEL FILE NAME HERE ***
excel_file = 'gr_2025_26_1_job.xlsx'

#################################################################################################################################################################################
# main.py
if __name__ == '__main__':
    current_path = os.path.dirname(os.path.realpath(__file__))
    logger = setup_logging()
    load_dotenv()

    # Set up the connection and retrieve connection_path and credentials
    connection_path, secrets = setup_bcgw(logger)
    print(f"Main: connection_path: {connection_path}")
    print(f"Main: secrets: {secrets}")

    # Create the path for the queuefile
    qf = os.path.join(current_path, excel_file)


    connection_path = setup_bcgw(logger)
    ast = AST_FACTORY(qf, logger, current_path, connection_path)

    # Proceed with your workflow
    if not os.path.exists(qf):
        print("Main: Queuefile not found, creating new queuefile")
        logger.info("Main: Queuefile not found, creating new queuefile")
        ast.create_new_queuefile()
        
    jobs = ast.load_jobs()
    ast.batch_ast()
    ast.re_load_failed_jobs_V2()
    ast.batch_ast()
    print("Main: AST Factory COMPLETE")
    logger.info("Main: AST Factory COMPLETE")
