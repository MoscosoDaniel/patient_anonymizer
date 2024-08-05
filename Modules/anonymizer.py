# %%
import os
import pydicom
import copy


class Eraser:
    """
    This is a simple program for anonymizing all DICOM files stored in
    a specific directory.
    """

    def __init__(self, root_path: str, anonymized_name: str) -> None:
        self.root_path: str = root_path
        self.anonymized_name: str = anonymized_name
        self.dataset: pydicom.FileDataset = pydicom.FileDataset
        self.data_elements: dict = {"PerformingPhysicianName": "Doctor",
                                    "ScheduledPerformingPhysicianName": "Doctor2",
                                    "InstitutionName": "Hospital",
                                    "InstitutionalDepartmentName": "Department",
                                    "PatientName": "Patient",
                                    "PatientID": "000000000000",
                                    "PatientBirthDate": "00000000",
                                    "PatientSex": "X"}
        self.missing_tags: list = []

    def __dir__(self) -> None:
        return ["get_existing_tags", "test", "anonymize"]

    def get_existing_tags(self, dataset: pydicom.FileDataset) -> dict[str, str]:
        """
        This function opens the DICOM file, and extracts all the available,
        DICOM tags that contain personal data from the user.

        Parameters:
        -----------
            dataset: |pydicom.FileDataset| This is the dataset read
                     from the DICOM file. Here is where all the tags and
                     data is stored.


        Returns:
        --------
            all_tags: |dict| It returns a dictionary consisting of the tags
                             present in the DICOM file available for
                             modification:\n
                             `"key"` --> tags.\n
                             `"value"` --> the modified names.
        """
        self.dataset = dataset
        all_tags: dict[str, str] = copy.deepcopy(self.data_elements)
        self.missing_tags: list[str] = []  # This is just in case you want to also run 'test()' without crashing.

        # Get the missing tags:
        for item in all_tags:
            if bool(dataset.get(item)) is True:
                pass
            else:
                print(f"Missing '{item}' tag. It will still be anonymized though.\n")
                self.missing_tags.append(item)

        # Delete the missing tags:
        # otherwise the dictionary will change size during iteration (if used in previous loop).
        for item in self.missing_tags:
            del all_tags[item]

        return all_tags

    def test(self, dataset: pydicom.FileDataset) -> None:
        """
        This function takes the DICOM file `dataset`, and prints how the output
        of the final anonymization will look like. Showing how the tags and
        their values are in the current state, and how they will be after the
        anonymization process.

        Parameters:
        -----------
            dataset: |pydicom.FileDataset| This is the dataset read
                     from the DICOM file. Here is where all the tags and
                     data is stored.


        Returns:
        --------

        """

        def print_tags(tags: dict[str, pydicom.FileDataset]) -> None:
            for tag in tags:
                print(dataset.data_element(tag))

        self.dataset = dataset

        # --------------- CHECK THE MODIFICATION OF TAGS ---------------
        # Get all the existing tags from the DICOM file:
        existing_tags: dict[str, str] = self.get_existing_tags(self.dataset)

        # Print original tags and values:
        print_tags(existing_tags)

        print()

        # Change tags values:
        for tag in existing_tags:
            dataset.data_element(tag).value = existing_tags[tag]

        # Print new tags and values:
        print_tags(existing_tags)
        # --------------- CHECK THE MODIFICATION OF TAGS ---------------

    def anonymize(self) -> None:
        """
        This function anonymizes All the DICOM files inside a directory
        taking the `root_directory` path and the `anonymized_name` given
        when first instantiating the class.

        Parameters:
        -----------


        Returns:
        --------

        """
        # ------------ ANONYMIZE ALL DICOM FILES IN THE DIRECTORY ------------
        counter: int = 0

        for root, dirs, files in os.walk(self.root_path):
            for item in files:
                if os.path.splitext(item)[1] != ".dcm":  # If it is not a DICOM file extension.
                    print(f"This will not be included '{item}'")
                else:
                    print("Current file: ", item)
                    counter += 1
                    self.dataset = pydicom.dcmread(os.path.join(root, item))

                    all_tags: dict[str, str] = self.get_existing_tags(self.dataset)

                    all_tags["PatientName"] = self.anonymized_name

                    for tag in all_tags:
                        self.dataset.data_element(tag).value = all_tags[tag]

                    self.dataset.save_as(os.path.join(root, item), write_like_original=False)

                    print(f"\nFile(s) anonymized: {counter}\n")
        # ------------ ANONYMIZE ALL DICOM FILES IN THE DIRECTORY ------------


# %%
# Debugging:
if __name__ == "__main__":
    anonymized_name: str = input("What is the anonymized tag? ")
    root_path: str = input("What is the root of the directory? ")

    bleach = Eraser(root_path, anonymized_name)

    bleach.anonymize()

    bleach.dataset.data_element("PatientSex")
    # # -------------------------------- TEST --------------------------------
    # # root_path = f"/home/person/Documents/DICOMS/1.dcm"

    # dataset = pydicom.dcmread(root_path)
    # anonymized_name = "Test"

    # bleach = Eraser(root_path, anonymized_name)

    # # Tip: This is a 'dict', so you can use the 'get()' method instead of 'data_element()'.
    # bleach.dataset.data_element("InstitutionName")

    # anonymized_tags = bleach.get_existing_tags(dataset)
    # bleach.dataset.data_element("PerformingPhysicianName").value
    # bleach.dataset.data_element("PerformingPhysicianName")
    # print(anonymized_tags)
    # print()
    # print()
    # bleach.test(dataset)

    # # Check 1 by 1:
    # # dataset.data_element("PerformingPhysicianName")
    # # dataset.data_element("ScheduledPerformingPhysicianName")
    # # dataset.data_element("InstitutionName")
    # # dataset.data_element("PatientName")
    # # dataset.data_element("PatientID")
    # # dataset.data_element("PatientBirthDate")
    # # dataset.data_element("PatientSex")
    # # dataset.data_element("InstitutionalDepartmentName")
    # # -------------------------------- TEST --------------------------------
# %%
