import openpyxl
import os
import tkinter as tk
from tkinter import filedialog

class ReplaceHyperlinks:
    def __init__(self, folder):
        self.folder = folder
        self.xl_files = []

        for root, dirs, files in os.walk(folder):
            for f in files:
                if f.endswith(('xls', 'xlsx')):
                    self.xl_files.append(os.path.join(root, f))

    def run_replacements(self):
        for xl in self.xl_files:
            print(f'Opening workbook: {xl}')
            wb = openpyxl.load_workbook(filename=xl)
            xl_head = os.path.dirname(xl)

            for sheet in wb.worksheets:
                for row in sheet.iter_rows():
                    for cell in row:
                        if cell.hyperlink:
                            target = cell.hyperlink.target.replace('file:///', '')

                            if target.startswith('https://') or not os.path.isabs(target):
                                continue

                            target_head = os.path.dirname(target)
                            target_file = os.path.basename(target)

                            try:
                                rel_head = os.path.relpath(target_head, xl_head)
                            except:
                                rel_head = target_head

                            new_target = os.path.join(rel_head, target_file)
                            cell.hyperlink.target = new_target
                            print(f'Replaced {target} with {new_target}')

            print('Saving workbook')
            wb.save(xl)
            wb.close()

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory(title="Select Folder Containing Excel Files")
    return folder_selected

if __name__ == '__main__':
    folder_path = select_folder()
    if folder_path:
        replace = ReplaceHyperlinks(folder=folder_path)
        replace.run_replacements()
    else:
        print("No folder selected.")
