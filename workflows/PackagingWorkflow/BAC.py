import bagit
import json
import csv
from pathlib import Path
import os
from unidecode import unidecode
import shutil

# digi pres globus uuid
globus_uuid = '5d8b0f1f-e5b1-4e8c-9310-22894a7d5f00'

def create_bag(path_to_barcode_directory, path_to_metadata_file):

  # create metadata profile
  with open(path_to_metadata_file, 'r', encoding='utf-8') as f:
    metadata_prof = {}
    full_metadata_prof = json.load(f)

    # pull from already created metadata text file
    metadata_prof['BarcodeNumberIdentifier'] = full_metadata_prof['BarcodeNumberIdentifier']
    metadata_prof['RecordsLabel'] = full_metadata_prof['RecordsLabel']
    metadata_prof['AlternateTitle'] = full_metadata_prof['AlternateTitle']
    metadata_prof['OriginatingUnitDepartment'] = full_metadata_prof['OriginatingUnitDepartment']
    metadata_prof['AccessionNumberCollection'] = full_metadata_prof['AccessionNumberCollection']
    metadata_prof['BagCreator'] = full_metadata_prof['BagCreator']

  # create bag
  # REPLACE path with the directory you want to bag
  bag = bagit.make_bag(path_to_barcode_directory, bag_info=metadata_prof, checksums=["md5"])

  if bag.is_valid():
      print("yay! bag is valid")
      return True
  else:
      print("boo :( bag is not valid")
      return False

# create dictionary of original ftk checksums
def get_ftk_checksums(ftk_checksums):
    ftk_dict = {}

    with open (file=ftk_checksums, mode="r", encoding='utf-8') as ftk:

        # read checksums in csv format
        ftk_content = csv.reader(ftk)
        next(ftk_content)
        for lines in ftk_content:
            # reformat ftk's backward slashes in the file path
            # MIGHT NEED TO REPLACE split delimiter
            file_path = (lines[2].split('[root]\\')[-1]).replace('\\', '/')
            # isolate and reformat file name
            file_path_replaced_spaces = file_path.replace(" ", "_")
            # add to file and checksum to dictionary
            ftk_dict[unidecode(file_path_replaced_spaces)] = lines[0]

    return ftk_dict

def get_rclone_checksums(original_checksums):

    rclone_dict = {}

    with open (file=original_checksums, mode="r", encoding='utf-8') as rclone:

        # loop through checksums
        for line in rclone:
            file_path = (line.strip().split('  ')[-1])
            # replace punctuation with underscore to account for bagit file renaming
            file_path = file_path.replace(',', '_')
            # isolate checksum value
            checksum = line.strip().split('  ')[0]

            # add to file and checksum to dictionary
            rclone_dict[unidecode(file_path)] = checksum

    return rclone_dict

def get_teracopy_checksums(original_checksums):

    teracopy_dict = {}

    with open (file=original_checksums, mode="r", encoding='utf-8') as teracopy:

        # loop through checksums
        for line in teracopy:
            file_path = (line.strip().split(' *')[-1])
            # fix slashes, this changes whether you're running it on mac or windows
            file_path = (file_path.replace('/', '/'))    
            # isolate checksum value                   
            checksum = line.strip().split(' *')[0]

            # add to file and checksum to dictionary
            teracopy_dict[unidecode(file_path)] = checksum.lower()

    return teracopy_dict

def compare_with_bagit(bagit_checksums, failed_checksums, original_dict):
    # compare with bagit file
    num_validated = 0
    num_passed = 0

    with open(file=bagit_checksums, mode="r", encoding='utf-8') as bgt:
        for line in bgt:
                # to account for chinese character double-width quotation mark
                fixed_line = line.replace("＂", "\"")
                fixed_line = unidecode(fixed_line)
                # only check against carved files
                if "carved_files" in fixed_line:
                    num_validated += 1
                    checksum = fixed_line.strip().split("  ")[0]
                    file_path = (fixed_line.strip().split("carved_files/")[-1])
                    if file_path in original_dict:
                        # make comparison
                        if checksum == original_dict[file_path]:
                            # update counter for number of files that have been checked
                            num_passed += 1
                        else:
                            # create or append failed_checksums file to documnent checksums that don't match
                            print("md5 checksums do not match for", file_path, "writing to", failed_checksums)
                            failed_info = file_path + ", " + original_dict[file_path] + ", " + checksum
                            with open(file=failed_checksums + "/failed_checksums.txt", mode="a", encoding='utf-8') as fc:
                                fc.write(failed_info + "\n")
                    else:
                        # error feedback
                        print(f'{file_path} does not match a file path in the original checksums dictionary')
                        next
        # feedback
        print("finished! validated", num_passed, "out of", num_validated, "files")
        
def call_checksum_validator(path_to_bag):

    print(f'validating checksums for {path_to_bag}')
    # check if metadata file exists
    if os.path.isfile(f'{path_to_bag}/data/transfer_metadata/metadata.txt'):

        # find the checksum file
        search_directory = Path(f'{path_to_bag}/data/transfer_metadata')
        found_files = list(search_directory.glob(f'{"checksums"}.*'))
        original_checksums = str(found_files[0])

        # get rclone checksums
        if "txt" in original_checksums:
            original_dict = get_rclone_checksums(original_checksums)
        # get ftk checksums
        elif "csv" in original_checksums:
            original_dict = get_ftk_checksums(original_checksums)
        # get teracopy checksums
        elif "md5" in original_checksums:
            original_dict = get_teracopy_checksums(original_checksums)

        # find bagit checksum file
        bagit_checksums = f'{path_to_bag}/manifest-md5.txt'
        # write failed checksums to transfer_metadata folder
        failed_checksums = f'{path_to_bag}/data/transfer_metadata'

        # compare bagit checksums with original checksums
        compare_with_bagit(bagit_checksums, failed_checksums, original_dict)
    else:
        # error handling
        print(f'{path_to_bag} does not contain a valid metadata file')


def single_bag(path_to_barcode_directory, path_to_metadata_file):

    is_valid = create_bag(path_to_barcode_directory, path_to_metadata_file)

    if is_valid:
        call_checksum_validator(path_to_barcode_directory)