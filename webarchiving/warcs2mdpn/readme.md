Process for backing up WARCs from Archive-it to MiDPN

Backup from Archive-It, partially based on this article: 
How to find and download your WARC files with WASAPI – Archive-It Help Center
https://support.archive-it.org/hc/en-us/articles/360015225051-How-to-find-and-download-your-WARC-files-with-WASAPI

 <img src="./IAtoMDPNflowchart.png" alt="Flowchart for process of backing up warc.gz files from Archive-it to MiDPN" width="200" align="left" />

Get list of Crawls:

Collection > Seed > List of Crawls:

From the Collection list, select Collection URL:

https://partner.archive-it.org/1234/collections/22222

Click on Seeds

From the Seed list, select Seed:

https://partner.archive-it.org/1234/collections/22222/seeds/1234567

Get Crawl IDs from Crawling History and use those in WASAPI:

https://warcs.archive-it.org/wasapi/v1/webdata?crawl=1234567

https://warcs.archive-it.org/wasapi/v1/webdata?crawl=2468901













##Use "curl" to get a list of warc.gz files:
Note: An Archive-It WARC is no bigger than 1GB, so a single crawl can generate multiple WARCs.

**** Using sudo su is key here****
**** You also need https://jqlang.org/ installed to parse the locations ****

sudo su 
curl -u username:password "https://warcs.archive-it.org/wasapi/v1/webdata?crawl=1234567" | jq -r .files[].locations[0] > url.list


##Then, actually download the warc.gz files:
wget --http-user=username --http-password=password --accept txt,gz -i url.list

**** If you have multiple crawls, you may want to use a batch process using a Bash script that pulls the crawls from the Seed Crawls list. 
Click on Crawling History
To download CSV of Seed Crawls click on Download Seed Crawls list
Open the CSV in spreadsheet
Select the entries from the Crawl ID column and save these as plain text in a file (RWAcrawls.txt).

This script needs to run after sudo su.

 #!/bin/bash
  while IFS= read -r crawl; do
      curl -u username:password "https://warcs.archive-it.org/wasapi/v1/webdata?crawl=${crawl}" | jq -r .files[].locations[0] >> url.list 
  done < "RWAcrawls.txt"


The '>>' appends each list of warcs to the same url.list file.

*** Need to check for crawls with count > 100, will need to use pagination option.***

##Use pywacz to create a single *.WACZ file from all warc.gz files (using https://github.com/webrecorder/py-wacz):
wacz create -o africanElections.wacz -f *.warc.gz -t --detect-pages
*** Note this issue when running wacz: https://github.com/webrecorder/py-wacz/issues/50

Create a metadata.txt file containing fields, using information from Archive-it:

- Collection: (same collection name from Archive-it)
- CollectionID: (same collection ID from Archive-it)
- Seed: (seed ID from Archive-it)
- URL: (original site URL)
- Title: (Title of the website)
- Creator: (creator of the website)
- Description: (same description from Archive-it)
- Language:
- Country:
- Created:
- Updated:

Use DART with MDPN configuration to transfer the wacz file and metadata.txt to MDPN for backup.
Save bag as:
UM_c[collectionID]_s[seedID]
Elections in Africa example: UM_c13472_s3316427




