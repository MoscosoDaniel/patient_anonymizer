# %%
import os
import pydicom
import zipfile


class Reorder:
    """
    This program takes a parent directory, checks if there are any children directories inside, and sorts their
    contents.
    \nIf the child directory has a ZIP file, it unzips it, removes all the directories that might have been created, and saves all the files in a newly created directory, sorting them according to their `SeriesTime` DICOM tag.
    \nIf there is no ZIP file, then the program checks for an already unziped directory.\n\n
    This is the structure for the directory/ZIP file:\n
     -------------------------------------------------------------------------\n
                            DIRECTORY STRUCTURE
     -------------------------------------------------------------------------\n
     main_directory > name > dicom_directory

     `main_directory`: this is the parent (first) directory in the tree.\n
     `name`: this is the directory with the anonymized name of the patient.\n
     `dicom_directory`: this is the directory holding all the smaller directories with the DICOM files inside, or a ZIP file.\n
     -------------------------------------------------------------------------
    """

    def __init__(self, root_path, dicom_directory, anonymized_tag="EMPTY_ANONYMIZED_TAG"):
        self.dicom_directory: str = dicom_directory
        self.root_path: str = root_path
        self.root_dir_path: str = f"{self.root_path}/{self.dicom_directory}"
        self.anonymized_tag: str = anonymized_tag
        self.time_stamp_dict: dict[str, str] = {}

    def __dir__(self):
        return ["unzip_file", "make_directory", "sort_files", "check_files_order", "rename_files"]

    def unzip_file(self) -> None:
        """
        This function creates a new directory in the root, with the same name as the ZIP file
        containing all the DICOM files. Then unzips the ZIP file into this newly created
        directory

        Parameters:
        -----------

        Returns:
        --------

        """
        self.make_directory(self.dicom_directory)

        try:
            with zipfile.ZipFile(f"{self.root_path}/{self.dicom_directory}.zip", "r") as zip_ref:
                zip_ref.extractall(self.root_dir_path)
        except FileNotFoundError:
            pass
        except OSError:
            raise OSError("You are running Linux paths on Windows native devices.\nTry copying the files to your computer first.")

        print("\nfiles unzziped!\n")

    def make_directory(self, new_dir: str = "default") -> None:
        """
        This function takes the root of the directory (given when the class is
        instanciated) and the anonymized tag. Then, creates a new directory in
        the same root, with the name of the anonymized tag. \n
        This is just if the function is used without any parameters. If a
        parameter is given, then it creates a new directory with this name, in
        the root directory.

        Parameters:
        -----------
            new_dir (path): If this parameter receives a value, then it becomes
                            the name of the new directory that needs to be created,
                            in the root directory.

        Returns:
        --------

        """
        if new_dir == "default":
            try:
                os.mkdir(f"{self.root_path}/{self.anonymized_tag}")
            except FileExistsError:
                pass
        else:
            try:
                os.mkdir(f"{self.root_path}/{new_dir}")
            except FileExistsError:
                pass

    def sort_files(self) -> dict[str, str]:
        """
        This function takes the root of the directory (given when the class is
        instanciated) looks for all the DICOM files in it, saves it in a
        dictionary, then sorts the files according to the 'SeriesTime' DICOM
        tag. \n
            - If there are multiple directories in the main directory, it uses
              'os.walk()' to naviate the entire tree. \n
            - The keys of the created dictionary are the series time of each
              individual DICOM file. \n
            - The values of the created dictionary are the full path for every
              DICOM tag.

        Parameters:
        -----------

        Returns:
        --------
            sorted_time_stamp_dict: |dictionary| This dictionary contains all
            the DICOM files in a specific directory, even if it has multiple
            sub-directories inside. The files are sorted according to the
            'SeriesTime', which are stored as keys in the dictionary. The
            values correspond to the full path of each given key (DICOM file).
        """
        # Create a dictionary with the sorted dicom files:
        #   key   --> 'SeriesTime' tag of the DICOM file.
        #   value --> path of the DICOM file.
        for root, dirs, files in sorted(os.walk(self.root_dir_path)):
            for item in files:
                dcm_file: str = f"{root}/{item}"
                dataset: pydicom.Dataset = pydicom.dcmread(dcm_file)
                self.time_stamp_dict[dataset.data_element("SeriesTime").value] = dcm_file

        sorted_time_stamp_dict = {key: value for key, value in sorted(self.time_stamp_dict.items(), key=lambda tuple_item: tuple_item[0])}
        # -------------------------------
        # Reasoning behind this last line
        # -------------------------------

        # # Although you might trust that when you use 'sorted()' the first time,
        # # it sets everything up for the rest of the code. But it actually is not
        # # completely sorted the way you need it. If the folders have weird naming,
        # # then the output might not be the one you are looking for.
        # # Ex: 'token10' goes before 'token2' --> the #2 needs a leading #0 to
        # # behave the way you want it. 'token02' goes before 'token10'

        # a = {'d': 6, 'a': 3, 'b': 2, 'e': 4, "2": 1, 't': 5}

        # # Create a new list with all items sorted according to
        # # the 2nd item in the tuple --> values:
        # sorted(a.items(), key=lambda x: x[1])  # Remember, this is how you define 'lambdas'. It is not a 'dict()' anymore.

        # # Create a new list with all items sorted according to
        # # the 1st item in the tuple --> keys:
        # sorted(a.items(), key=lambda x: x[0])  # Remember, this is how you define 'lambdas'. It is not a 'dict()' anymore.

        # # Same as previous one, since it is the default value:
        # sorted(a.items())

        # # What is left is to use dictionary comprehension:
        # {key: value for key,value in sorted(a.items(), key=lambda x: x[1])}

        # # Now, no matter how scrambled you data is, or if you do not use 'sorted'
        # # initially, everything will be sorted correctly ALWAYS.
        # ---------------------------------------------------------------------
        return sorted_time_stamp_dict

    def check_files_order(self) -> None:
        """
        This function first calls the `sort_files()` function, saves the sorted
        dictionary into a variable, to finally output all the sorted files in
        a more readable way:
            1.- The index of the current DICOM file inside the dictionary. \n
            2.- The `SeriesTime` time stamp of the given DICOM file. \n
            3.- The full path of the given DICOM file. \n

        Parameters:
        -----------

        Returns:
        --------

        """
        sorted_time_stamp_dict: dict[str, str] = self.sort_files()
        # ---------------------- This is for sanity check: ----------------------
        for counter, item in enumerate(sorted_time_stamp_dict.items()):
            print(f"index: {counter} | time_stamp: {item[0]} | root: {item[1]}")

    def rename_files(self) -> None:
        """
        This function first calls the `sort_files()` function, saves the sorted
        dictionary into a variable, and then uses the values for as a starting
        point for renaming each file. \n
            - The original name of the file comes from the original path of the file. \n
            - The new name comes from \n
                > The root of the outer most directory, plus \n
                > The name or anonymyzed tag given when instantiating the class, which
                  is also the name given to the newly created directory by the
                  `make_directory()` function, plus \n
                > An integer series starting at '000', which are the names of all the
                  sorted DICOM files.

        Parameters:
        -----------

        Returns:
        --------

        """
        def make_number_tag(counter: int) -> str:
            if len(str(counter)) == 1:
                tag: str = f"00{counter}"
            elif len(str(counter)) == 2:
                tag: str = f"0{counter}"
            else:
                tag: str = f"{counter}"

            return tag

        def make_special_renames(dicom_data: tuple[str, str], tag: str) -> None:
            if "TEST1" in dicom_data[1]:
                os.rename(f"{dicom_data[1]}", f"{self.root_path}/{self.anonymized_tag}/{tag}_t1.dcm")
            elif "TEST2" in dicom_data[1]:
                os.rename(f"{dicom_data[1]}", f"{self.root_path}/{self.anonymized_tag}/{tag}_t2.dcm")
            else:
                os.rename(f"{dicom_data[1]}", f"{self.root_path}/{self.anonymized_tag}/{tag}.dcm")

        sorted_time_stamp_dict: dict[str, str] = self.sort_files()

        # -----------------------------------------------------------------------------------------------
        # Get the files out of the original directories, and add them to the newly created directory:
        for counter, dicom in enumerate(sorted_time_stamp_dict.items()):
            tag = make_number_tag(counter)

            make_special_renames(dicom, tag)


# %%
if __name__ == "__main__":
    # # ------- Check how the directories and files are seen by the code: -------
    # name = "PATIENT_NAME"
    # root = f"sample_dir/patients/{name}"

    # counter = 0
    # for root, dirs, files in sorted(os.walk(root)):
    #     print(root)
    #     print(dirs)
    #     for item in files:
    #         counter += 1
    #         print(item)
    #     print(f" --------- {counter} --------- ")
    # # -------------------------------------------------------------------------

    # name = input("What is the patient's name: ")
    name = "NEW_PATIENTS"  # This is where all the raw dicom dirs/ZIP files are held.

    grand_parent_directory = "sample_dir"  # This is the name of the upper-most directory. It could be the name of the project.
    dicom_directory = "PATIENT1"  # This is the name that comes with the directory/ZIP file by default.

    root_path = f"documents/first_dir/second_dir/etc/{grand_parent_directory}/{name}"

    anonymized_tag = "NEW_NAME_TAG"

    wall_e = Reorder(root_path, dicom_directory, anonymized_tag)

    wall_e.unzip_file()

    wall_e.make_directory()
    wall_e.check_files_order()
    wall_e.rename_files()
# %%
