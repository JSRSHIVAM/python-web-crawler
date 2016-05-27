# python-web-crawler
A simple web crawler developed in python3.4 and MySQL


Libraries:
BeautifulSoup
urllib
pymysql

Usage:
 Create MySql Database "crawler"
 Import the sql file.


 Demo site is provided to test the crawler. Extract the zip file in web root directory.
 Set the base and crawl at the last line in crawl.py to target url
- base = "http://localhost/"
- crawl("http://localhost/","href")

Run the python Script
The crawl data will be updated in database.
AFTER EACH RUN TRUNCATE THE ENTIRE TABLE.
