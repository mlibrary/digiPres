# Process for backing up WARCs from Archive-it to MiDPN

Backup from Archive-It, partially based on this article: 

How to find and download your WARC files with WASAPI – Archive-It Help Center
https://support.archive-it.org/hc/en-us/articles/360015225051-How-to-find-and-download-your-WARC-files-with-WASAPI

 <img src="./IAtoMDPNflowchart.png" alt="Flowchart for process of backing up warc.gz files from Archive-it to MiDPN" width="200" align="left" />
 

Basic Process:
 
1. [Get crawl ID(s) for particular seed](#get-list-of-crawls)
2. [Use "curl" to get list of warc.gz files](#use-curl-to-get-a-list-of-warcgz-files)
3. [Use "wget" to download the warc.gz files](#then-actually-download-the-warcgz-files)
4. [Use "py-wacz" to Create single *.WACZ file from all warc.gz files](#use-pywacz-to-create-a-single-wacz-file-from-all-warcgz-files)
5. [Create metadata and use DART to move wacz file to MiPDN](#create-a-metadatatxt-file-containing-fields-using-information-from-archive-it)

- OPTIONAL  [Run site locally?](#run-site-locally)
- Other Considerations [Extract just the files](#other-considerations-extract-just-the-files)


<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>
<br/>

## Get list of Crawls:

Collection > Seed > List of Crawls:

From the Collection list, select Collection URL:

- https://partner.archive-it.org/1234/collections/22222

Click on Seeds

From the Seed list, select Seed:

- https://partner.archive-it.org/1234/collections/22222/seeds/1234567

Get Crawl IDs from Crawling History and use those in WASAPI:

- https://warcs.archive-it.org/wasapi/v1/webdata?crawl=1234567
- https://warcs.archive-it.org/wasapi/v1/webdata?crawl=2468901

## Use "curl" to get a list of warc.gz files:
Note: An Archive-It WARC is no bigger than 1GB, so a single crawl can generate multiple WARCs.

**** Using `sudo su` is key here****

**** You also need https://jqlang.org/ installed to parse the locations ****
```
sudo su 
curl -u username:password "https://warcs.archive-it.org/wasapi/v1/webdata?crawl=1234567" | jq -r .files[].locations[0] > url.list
```

## Then, actually download the warc.gz files:
`wget --http-user=username --http-password=password --accept txt,gz -i url.list`

**** If you have multiple crawls, you may want to use a batch process using a Bash script that pulls the crawls from the Seed Crawls list. 

1. Click on Crawling History
2. To download CSV of Seed Crawls click on Download Seed Crawls list
3. Open the CSV in spreadsheet
4. Select the entries from the Crawl ID column and save these as plain text in a file (RWAcrawls.txt).

This script needs to run after `sudo su`.
```
 #!/bin/bash
  while IFS= read -r crawl; do
      curl -u username:password "https://warcs.archive-it.org/wasapi/v1/webdata?crawl=${crawl}" | jq -r .files[].locations[0] >> url.list 
  done < "RWAcrawls.txt"
```

The '>>' appends each list of warcs to the same url.list file.

*** Need to check for crawls with count > 100, will need to use pagination option.***

## Use pywacz to create a single *.WACZ file from all warc.gz files 
(using https://github.com/webrecorder/py-wacz):

`wacz create -o example.wacz -f *.warc.gz -t --detect-pages`

*** Note this issue when running wacz: https://github.com/webrecorder/py-wacz/issues/50

## Create a metadata.txt file containing fields, using information from Archive-it:
```
Collection: (same collection name from Archive-it)
CollectionID: (same collection ID from Archive-it)
Seed: (seed ID from Archive-it)
URL: (original site URL)
Title: (Title of the website)
Creator: (creator of the website)
Description: (same description from Archive-it)
Language:
Country:
Created:
Updated:
```
## Use DART with MDPN configuration to transfer the wacz file and metadata.txt to MDPN for backup.
Save bag as:

UM_c[collectionID]_s[seedID]

For example: UM_c22222_s1234567

## Run Site Locally

Move newly created africanElections.wacz to webserver location and update index.html file accordingly (see https://replayweb.page/docs/embedding/#self-hosting):

HTML:
```
<!doctype html>
<html class="no-overflow">
  <head>
    <title>WebArchive</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="js/ui.js"></script>
    <link rel="stylesheet" href="css/style.css">
  </head>
  <body>
    <section class="web-archive">
    <replay-web-page replayBase="js/" url="https://examplesite.org/" source="wacz/example.wacz"></replay-web-page>
    </section>

  </body>
</html>
```
Start Apache webserver:

`sudo apachectl restart`

http://localhost/webarchive/exampleSite/

**** Using Apache webserver here because of ReplayWeb's HTTPS CORS requirement, mentioned here https://replayweb.page/docs/user-guide/locations/, simple HTTPS will not work.

## [Other Considerations] Extract just the files

If you do not need to capture the entire site but just the content, you can extract PDFs and/or other files such as images from WARC.gz files for easier access using warc-extractor from https://github.com/recrm/ArchiveTools.  

Usage examples:
```
python3 warc-extractor.py http:content-type:pdf
python3 warc_extractor.py -dump content http:error:200
```






