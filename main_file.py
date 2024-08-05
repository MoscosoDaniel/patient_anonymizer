# %%
from Modules import anonymizer
from Modules import out_of_folder
import shutil
import os
import re
from tkinter import messagebox
# -------------------------------------------------------------------------
#                             DIRECTORY STRUCTURE
# -------------------------------------------------------------------------
# main_directory > name > dicom_directory
#
# main_directory: this is the parent (first) directory in the tree.
# name: this is the directory with the anonymized name of the patient.
# dicom_directory: this could be the directory holding all the smaller
#                  directories with the DICOM files inside, or a ZIP folder.
# -------------------------------------------------------------------------

# # Computer:
# main_directory = "patients"

# name: str = input("What is the patient's name: ")
# dicom_directory: str = input("What is the ZIP file's name: ")
# anonymized_tag: str = input("What is the anonymized tag: ")

# root_path: str = f"/home/person/Documents/DICOMS/PROJECT_NAME/{main_directory}/{name}"
# ----------------------------------
dir_name_pattern: str = r"new_patients/TAG_DATA_HOSPITAL-\d+\Z"

main_directory: str = "new_patients"

root_path: str = f"/home/person/Documents/DICOMS/PROJECT_NAME/{main_directory}"
# root_path: str = f"/media/person/My Passport/{main_directory}"  # In case you run it from an external hard-drive.

for root_paths, directories, files in os.walk(root_path):
    try:
        path_indexes: tuple[int, int] = re.search(dir_name_pattern, root_paths).span()
    except AttributeError:
        # Otherwise, when there are no directories, you will have a
        # "'NoneType' object", which cannot be used with ".span()"
        pass
    else:
        path_slice: str = root_paths[path_indexes[0]:path_indexes[1]]

        if bool(path_slice):
            name: str = path_slice[13:]
            anonymized_tag = name

            if len(directories) > 0:  # There are no ZIP files, only a directory.
                dicom_directory: str = directories[0]
            else:  # There is only a ZIP files and no directories.
                dicom_directory: str = os.path.splitext(files[0])[0]

            # ------------------------------------------------
            men_in_black: anonymizer.Eraser = anonymizer.Eraser(root_paths, anonymized_tag)

            wall_e: out_of_folder.Reorder = out_of_folder.Reorder(root_paths, dicom_directory, anonymized_tag)
            # ------------------------------------------------
            wall_e.unzip_file()

            men_in_black.anonymize()

            wall_e.make_directory()
            wall_e.check_files_order()
            wall_e.rename_files()

            shutil.rmtree(f"{root_paths}/{dicom_directory}")
            os.remove(f"{root_paths}/{dicom_directory}.zip")

messagebox.showinfo(title="Ready!",
                    message=f"All patients annonymized!")

# %%
