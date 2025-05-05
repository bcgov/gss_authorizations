#description: 
# this script updates a path in an excel document with enhanced error checking
import openpyxl 
import os
import sys
import ctypes
import arcpy
import logging
from datetime import datetime as dt
from ctypes import wintypes
from argparse import ArgumentParser
from util.environment import Environment

def run_app() -> None:
    try:
        fld, logger = get_input_parameters()
        replace = ReplaceHyperlinks(folders=fld, logger=logger)
        replace.run_replacements()
        del replace
    except Exception as e:
        logging.error(f'Error running the application: {e}')
        sys.exit(1)

def get_input_parameters() -> tuple:
    try:
        parser = ArgumentParser(description='Replace hyperlinks within excel documents with relative paths.')
        parser.add_argument('fld', type=str, help='Semi colon separated list of folders to run')
        parser.add_argument('--log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                            help='Log level for message output')
        parser.add_argument('--log_dir', help='Path to the log file directory')

        args = parser.parse_args()
        logger = Environment.setup_logger(args)

        if not args.fld:
            raise ValueError("Folder path must not be empty.")

        return args.fld, logger

    except Exception as e:
        logging.error(f'Unexpected exception, program terminating: {str(e)}')
        raise Exception('Errors exist')


class ReplaceHyperlinks:
    """
    ------------------------------------------------------------------------------------------------------------
        CLASS: Used to contain the methods for replacing hyperlinks with added error handling
    ------------------------------------------------------------------------------------------------------------
    """
    def __init__(self, folders: str, logger: logging.Logger) -> None:
        self.folders = folders.split(';')
        self.xl_files = []
        self.logger = logger

        self.logger.info('Gathering excel files')
        for fld in self.folders:
            if not os.path.exists(fld):
                self.logger.warning(f'Folder does not exist: {fld}')
                continue

            for root, dirs, files in os.walk(fld):
                for f in files:
                    if f.endswith(('xls', 'xlsx')):
                        file_path = os.path.join(root, f)
                        self.xl_files.append(file_path)
                        self.logger.debug(f'Excel file added: {file_path}')
    
    def run_replacements(self) -> None:
        for xl in self.xl_files:
            try:
                xl = Environment.get_full_path(str_file=xl)
                xl_head = os.path.dirname(xl)

                self.logger.info(f'Opening workbook: {xl}')
                wb = openpyxl.load_workbook(filename=xl)

                for sheet in wb.worksheets:
                    for row in sheet.iter_rows():
                        for cell in row:
                            if cell.hyperlink:
                                target = cell.hyperlink.target.replace('file:///','')

                                if target.startswith('https://') or not os.path.isabs(target):
                                    continue

                                try:
                                    target = Environment.get_full_path(str_file=target)
                                    target_head = os.path.dirname(target)
                                    target_file = os.path.basename(target)
                                    rel_head = os.path.relpath(target_head, xl_head)
                                    new_target = os.path.join(rel_head, target_file)

                                    cell.hyperlink.target = new_target
                                    self.logger.info(f'Replaced {target} with {new_target}')

                                except Exception as inner_e:
                                    self.logger.error(f'Error processing hyperlink {target}: {str(inner_e)}')

                self.logger.info('Saving workbook')
                wb.save(xl)
                wb.close()

            except openpyxl.utils.exceptions.InvalidFileException:
                self.logger.error(f'Invalid Excel file: {xl}')
            except Exception as e:
                self.logger.error(f'Unexpected error processing workbook {xl}: {str(e)}')

if __name__ == '__main__':
    run_app()
