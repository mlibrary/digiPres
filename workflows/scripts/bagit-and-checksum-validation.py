import bagit
import json
import csv
from pathlib import Path
import os
from unidecode import unidecode
import shutil

# digi pres globus uuid
globus_uuid = '5d8b0f1f-e5b1-4e8c-9310-22894a7d5f00'

def create_bag(metadata_file, barcode_dir, good_bags_dir, bad_bags_dir):

  # create metadata profile
  with open(metadata_file, 'r', encoding='utf-8') as f:
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
  bag = bagit.make_bag(bag_dir=barcode_dir, bag_info=metadata_prof, checksums=["md5"])

  if bag.is_valid():
      shutil.move(barcode_dir, good_bags_dir)
      return True
  else:
      shutil.move(barcode_dir, bad_bags_dir)
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

def convert_to_globus(path_to_bag):

    # create globus storage url
    globus_storage_url = f'https://app.globus.org/file-manager?origin_id={globus_uuid}&origin_path=%2Fgodata%2FDigiPresBags'

    # check for bag-info file
    if os.path.isfile(f'{path_to_bag}/bag-info.txt'):
        bag_info = Path(f'{path_to_bag}/bag-info.txt')
        # create dictionaries for each item and its metadata content
        item = {}
        content = {}
        # open bag info file
        with open(bag_info, 'r', encoding='utf-8') as f:
            lines = [line.rstrip() for line in f]
            for line in lines:
                # split by first instance of : delimiter
                parts = line.split(":", 1)

                # add to json dict
                content[parts[0].strip()] = parts[-1].strip()

                # set subject and url using barcode
                if 'Barcode' in parts[0].strip():
                    barcode = parts[-1].strip()
                    item['subject'] = barcode
                    content['url'] = globus_storage_url + f'%2F{barcode}%2F'

            # set visibility to all authenticated users
            item['visible_to'] = ['all_authenticated_users']
            # assign metadata to item
            item['content'] = content

            f.close()

        return item

    else:
        print(f'{path_to_bag} does not contain a valid bag info file')

def batch_globus(path_to_batch_directory):

    num_added = 0

    # can pass batch directory or good_bags subdirectory
    if 'good_bags' in str(path_to_batch_directory):
        p = Path(path_to_batch_directory)
    else:
        p = Path(path_to_batch_directory + "/good_bags")

    # create full json object
    full_dict = {}
    # set default values
    full_dict['ingest_type'] = 'GMetaList'
    ingest_data = {}
    gmeta = []

    try:
        # loop through batch of bags
        for f in p.iterdir():
            # skip irrelevant mac file
            if '.DS_Store' in str(f):
                next
            # skip globus ingest file if already created
            elif 'globus-ingest.json' in str(f):
                next
            # add items to full json object
            else:
                print(f'adding {f} to search ingest file')
                gmeta.append(convert_to_globus(str(f)))
                num_added += 1

        if num_added > 0:
            # assign values
            ingest_data['gmeta'] = gmeta
            full_dict['ingest_data'] = ingest_data

            # write to json file called globus-ingest.json and place it in batch directory
            with open(Path(f'{path_to_batch_directory}/globus-ingest.json'), 'w', encoding='utf-8') as f:
                    
                json.dump(full_dict, f, indent=4)

            print(f'{num_added} bags added to globus-ingest.json')
        else:
            print('no globus-ingest.json created')

    except:
        print('invalid batch bag directory')


def batch_bag(path_to_batch_directory):

    num_tried = 0
    num_successful = 0

    # create bags directory to plop newly created bags in
    good_bags = "good_bags"
    bad_bags = "bad_bags"
    try:
        good_bags = os.path.join(path_to_batch_directory, good_bags)
        bad_bags = os.path.join(path_to_batch_directory, bad_bags)
        os.mkdir(good_bags)
        os.mkdir(bad_bags)
        print(f"{good_bags} and {bad_bags} created successfully")
    except FileExistsError:
        print("bags directory already created. continuing on")
        # keep going
        pass
    except PermissionError:
        print("permission denied. unable to create bags directory")
    except Exception as e:
        print(f"an error occurred: {e}")

    p = Path(path_to_batch_directory)
    # count only the folders directly inside the path
    dir_count = sum(1 for item in p.iterdir() if item.is_dir())
    # subtract good_bags and bad_bags
    dir_count = dir_count - 2


    # loop through batch of bags
    for f in p.iterdir():
        # check if there is a metadata file
        if os.path.isfile(f'{f}/transfer_metadata/metadata.txt'):
            num_tried += 1
            print(f'bagging {num_tried} out of {dir_count} directories')
            metadata_file = f'{f}/transfer_metadata/metadata.txt'
            # create bag
            is_success = create_bag(metadata_file, f, good_bags, bad_bags)
            if is_success:
                num_successful += 1
        elif 'good_bags' in str(f) or 'bad_bags' in str(f) or '.DS_Store' in str(f):
            next
        else:
            print(f'{f} does not contain a valid metadata file')

    print(f'{num_successful} bags successfully created out of {dir_count}')

    # validate checksums
    print("Validating checksums...")
    batch_checksums(good_bags)


def batch_checksums(path_to_batch_directory):

    if 'good_bags' in str(path_to_batch_directory):

        p = Path(path_to_batch_directory)
    else:
        p = Path(path_to_batch_directory + "/good_bags")

    try:
        #loop through batch of bags
        for f in p.iterdir():
            # skip irrelevant mac file
            if '.DS_Store' in str(f):
                next
            # skip globus ingest file
            elif 'globus-ingest.json' in str(f):
                next
            #validate checksums
            else:
                call_checksum_validator(f'{f}')
    except:
        print('invalid bag directory')

bag_or_checksum = input("Would you like to bag ('b') or verify checksums ('c') or create globus ingest file ('g')?: ")
if bag_or_checksum == 'b':

    path_to_batch_directory = input("Enter path to batch directory: ")
    batch_bag(path_to_batch_directory.strip("'"))

    run_globus = input("Will you be ingesting to globus? Yes ('y') or no ('n'): ")
    if run_globus == 'y':
        # create globus file
        globus = path_to_batch_directory
        # mac click and drag strip quotations
        batch_globus(globus.strip("'"))

    else:
        print('thanks, all done!')

    
elif bag_or_checksum == 'c':
    
    # validation check
    path_to_bag = input("Enter path to batch directory: ")
    # mac click and drag strip quotations
    batch_checksums(path_to_bag.strip("'"))

elif bag_or_checksum == 'g':
    
    # create globus file
    globus = input("Enter path to batch directory: ")
    # mac click and drag strip quotations
    batch_globus(globus.strip("'"))

else:
    print("boo! invalid response :(")
