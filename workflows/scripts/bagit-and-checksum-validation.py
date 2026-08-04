import bagit
import json
import csv
from pathlib import Path
import re

globus_uuid = '5d8b0f1f-e5b1-4e8c-9310-22894a7d5f00'

def create_bag(metadata_file, barcode_dir):

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
      print("yay! bag is valid")
  else:
      print("boo! bag is not valid")

# create dictionary of original ftk checksums
def get_ftk_checksums(ftk_checksums):
    ftk_dict = {}

    with open (file=ftk_checksums, mode="r", encoding='utf-8') as ftk:
        ftk_content = csv.reader(ftk)
        next(ftk_content)
        for lines in ftk_content:
            # reformat ftk's backward slashes in the file path
            # MIGHT NEED TO REPLACE split delimiter
            file_path = (lines[2].split('[root]\\')[-1]).replace('\\', '/')
            file_path_replaced_spaces = file_path.replace(" ", "_")
            ftk_dict[file_path_replaced_spaces] = lines[0]

    return ftk_dict

def get_rclone_checksums(original_checksums):
    rclone_dict = {}

    with open (file=original_checksums, mode="r", encoding='utf-8') as rclone:
        
        for line in rclone:
            file_path = (line.strip().split('  ')[-1])
            checksum = line.strip().split('  ')[0]
            rclone_dict[file_path] = checksum

    return rclone_dict

def get_teracopy_checksums(original_checksums):
    teracopy_dict = {}

    with open (file=original_checksums, mode="r", encoding='utf-8') as teracopy:
        
        for line in teracopy:
            file_path = (line.strip().split(' *')[-1])
            # fix slashes
            file_path = (file_path.replace('/', '/'))                       
            checksum = line.strip().split(' *')[0]
    
            teracopy_dict[file_path] = checksum.lower()

    return teracopy_dict

def compare_with_bagit(bagit_checksums, failed_checksums, original_dict):
    # compare with bagit file
    num_validated = 0
    num_passed = 0

    with open(file=bagit_checksums, mode="r", encoding='utf-8') as bgt:
        for line in bgt:
                # to account for chinese character double-width quotation mark
                fixed_line = line.replace("＂", "\"")
                # only check against carved files
                if "carved_files" in fixed_line:
                    num_validated += 1
                    checksum = fixed_line.strip().split("  ")[0]
                    file_path = (fixed_line.strip().split("carved_files/")[-1])
                    if file_path in original_dict:
                        if checksum == original_dict[file_path]:
                            num_passed += 1
                        else:
                            # create or append failed_checksums file to documnent checksums that don't match
                            print("md5 checksums do not match for", file_path, "writing to", failed_checksums)
                            failed_info = file_path + ", " + original_dict[file_path] + ", " + checksum
                            with open(file=failed_checksums + "/failed_checksums.txt", mode="a", encoding='utf-8') as fc:
                                fc.write(failed_info + "\n")
                    else:
                        print('issue:', file_path)
                        next
        print("finished! validated", num_passed, "out of", num_validated, "files")
        
def call_checksum_validator(path_to_bag):
    
    search_directory = Path(f'{path_to_bag}/data/transfer_metadata')
    found_files = list(search_directory.glob(f'{"checksums"}.*'))
    original_checksums = str(found_files[0])
    
    if "txt" in original_checksums:
        original_dict = get_rclone_checksums(original_checksums)
    elif "csv" in original_checksums:
        original_dict = get_ftk_checksums(original_checksums)
    elif "md5" in original_checksums:
        original_dict = get_teracopy_checksums(original_checksums)
        
    bagit_checksums = f'{path_to_bag}/manifest-md5.txt'
    failed_checksums = f'{path_to_bag}/data/transfer_metadata'
    
    compare_with_bagit(bagit_checksums, failed_checksums, original_dict)

def convert_to_globus(path_to_bag):

    globus_storage_url = f'https://app.globus.org/file-manager?origin_id={globus_uuid}&origin_path=%2Fgodata%2FDigiPresBags'

    # REPLACE DOT
    bag_info = Path(f'{path_to_bag}/bag-info.txt')
    item = {}
    content = {}
    with open(bag_info, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f]
        for line in lines:
            # split by first instance of : delimiter
            parts = line.split(":", 1)

            # add to json dict
            content[parts[0].strip()] = parts[-1].strip()

            if 'Barcode' in parts[0].strip():
                barcode = parts[-1].strip()
                item['subject'] = barcode
                content['url'] = globus_storage_url + f'%2F{barcode}%2F'
                   
        item['visible_to'] = ['all_authenticated_users']
        item['content'] = content

        f.close()

    return item

def batch_globus(path_to_batch_directory):

    full_dict = {}
    full_dict['ingest_type'] = 'GMetaList'
    ingest_data = {}
    gmeta = []

    p = Path(path_to_batch_directory)
    for f in p.iterdir():
        # skip irrelevant mac file
        if '.DS_Store' in str(f):
            next
        elif 'globus-ingest.json' in str(f):
            next
        else:
            print(f)
            gmeta.append(convert_to_globus(str(f)))

    ingest_data['gmeta'] = gmeta
    full_dict['ingest_data'] = ingest_data

    with open(Path(f'{path_to_batch_directory}/globus-ingest.json'), 'w', encoding='utf-8') as f:
            
        json.dump(full_dict, f, indent=4)


def batch_bag(path_to_batch_directory):

    p = Path(path_to_batch_directory)
    for f in p.iterdir():
        # skip irrelevant mac file
        if '.DS_Store' in str(f):
            next
        else:
            metadata_file = f'{f}/transfer_metadata/metadata.txt'
            print(metadata_file)
            create_bag(metadata_file, f)
    
            print("Validating checksums...")
    
            call_checksum_validator(f'{f}')
        

bag_or_checksum = input("Would you like to bag ('b') or verify checksums ('c') or create globus ingest file ('g')?: ")
if bag_or_checksum == 'b':

    path_to_batch_directory = input("Enter path to batch directory: ")
    batch_bag(path_to_batch_directory.strip("'"))

    run_globus = input("Will you be ingesting to globus? Yes ('y') or no ('n'): ")
    if run_globus == 'y':
        # create globus file
        globus = path_to_batch_directory
        batch_globus(globus.strip("'"))

    else:
        print('thanks, all done!')

    
elif bag_or_checksum == 'c':
    
    # validation check
    path_to_bag = input("Enter path to bag: ")
    call_checksum_validator(path_to_bag.strip("'"))

elif bag_or_checksum == 'g':
    
    # create globus file
    globus = input("Enter path to batch directory: ")
    batch_globus(globus.strip("'"))
