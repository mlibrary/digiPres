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

