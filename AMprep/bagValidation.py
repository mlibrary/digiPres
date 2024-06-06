# https://github.com/LibraryOfCongress/bagit-python

import bagit
import glob, os

for bagDir in glob.iglob('/Volumes/ulib-darkblue-staging/CVGA/production/autoTransfer2/bagTest/**'):
    if os.path.isdir(bagDir): # filter dirs
        print(bagDir)
        bag = bagit.Bag(bagDir)

        '''
        try:
          bag.validate()

        except bagit.BagValidationError as e:
            print(e)
        '''
        bag.info['BIB-System-Number'] = bag.info['BIB/System Number']
        del bag.info['BIB/System Number']
        bag.info['BarcodeNumber-Identifier'] = bag.info['BarcodeNumber/Identifier']
        del bag.info['BarcodeNumber/Identifier']
        bag.info['ProfileName'] = bag.info['Profile Name']
        del bag.info['Profile Name']

        # persist changes
        bag.save(manifests=True)
         
        if bag.is_valid():
            print("yay :)")
        else:
            print("boo :(")
