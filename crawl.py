import bs4
from bs4 import BeautifulSoup
import urllib
import urllib.request
import pymysql.cursors
import traceback
import re

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             db='crawler',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
master = []
unvisited = []
visited = []
depth = 0
extract = ["html","js","php","aspx","jpg","png"]

def cleanUrl(base,link):
    clean = ""
    if  not base in link:
        return base+link   
    return clean+link

def insertSatisfy(link):
    if link == "#" or link=="." or link =="./" or link == "../":
        return False


    #folder = [-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)
    for formats in extract:
     #if formats in link:
     # return True
     if formats.endswith("/"):
        return True     
    return True
    
def formatLink(link):
    #remove fragments
    clean = link.split('#')[0]
    #build url
    if clean.find('http') == 0:
        # It's an absolute URL, do nothing.
        pass
    elif clean.find('/') == 0:
        # If it's a root URL, append it to the base URL:
        clean = 'http://' + url_base + "/"
    else:
        # If it's a relative URL, ?
        pass
    return clean    

def isExist(link):
    with connection.cursor() as cursor:
        checkExists = "SELECT count(`id`) FROM `crawl_data` WHERE `link` = %s"
        cursor.execute(checkExists,link)
        isIt = cursor.fetchone()
         
        #print("Count "+ str(isIt['count(`id`)']))         
        if isIt['count(`id`)'] == 0:
            connection.commit()
            return False
        connection.commit()
    return True

def updateVisited(link):
    #print("Updating Visit")
    with connection.cursor() as cursor:
        getVisit = "SELECT `visited` FROM `crawl_data` WHERE `link` = %s"
        cursor.execute(getVisit,(link))
        count = cursor.fetchone()
        if count:
         newVal =count['visited'] + 1 
         updateMe = "UPDATE `crawl_data` SET `visited`="+str(newVal)+" WHERE `link` = %s"
         cursor.execute(updateMe,(link))
         print("Visit Updated: " + link +" count: "+ str(newVal)) 
        connection.commit()
       
    return
    
    
def isVisitingLeft(depth):
    with connection.cursor() as cursor:
        checkIsUnvisitPresent = "SELECT count(`id`)  FROM `crawl_data` WHERE `visited` = 0 AND depth = %s"
        cursor.execute(checkIsUnvisitPresent, str(depth))
        count = cursor.fetchone()

        if count['count(`id`)'] > 0:
            connection.commit()
            return True
        connection.commit()
    return False


def getLink(url, type):   
        links = []
        try:
            with urllib.request.urlopen(url) as link:
              response = link.read()
              soup = BeautifulSoup(response, "lxml")
              
              if type == "href":
                  for link in soup.find_all('a'):
                   href = str(link.get("href"))
                   links.append(href)
                  for link in soup.find_all('form'): 
                   action = str(link.get("action"))
                   links.append(action)
        except:
            return []
        links = list(set(links)) 
        #print("URL:  %s" % url +" Links:  "+ str(len(unvisited)))
        return links   
        
def insert(link, type, depth):
    insertquery = "INSERT INTO `crawl_data` (`link`, `type`,`depth`) VALUES (%s, %s, %s)"
    
    try:
        if not isExist(link):
            with connection.cursor() as cursor:
                param = [link, type, int(depth)]
                cursor.execute(insertquery, param)
                connection.commit()
            print("Inserted " + link)    
        else :
            updateVisited(link)
    finally:
       pass 

def getAllFromDB(depth):
    with connection.cursor() as cursor:
        getAll = "SELECT link  FROM `crawl_data` WHERE `depth` = %s"
        cursor.execute(getAll, str(depth))
        links = cursor.fetchall()
        
        ret = []
        for linkURL in links:
            ret.append(linkURL['link'])
        connection.commit()
    return ret

def getUnvisitedFromDB(depth):
    with connection.cursor() as cursor:
        getAll = "SELECT link  FROM `crawl_data` WHERE `depth` = %s and visited = 0"
        cursor.execute(getAll, str(depth))
        links = cursor.fetchall()
        
        ret = []
        for linkURL in links:
            ret.append(linkURL['link'])
        connection.commit()
    return ret
    
    
depthCounter = 0        
def crawl(url, type):
    global depthCounter
    global base
    insert(url, type, depthCounter)
    depthCounter += 1
    try:
            unvisited = getLink(url, type)
            updateVisited(url)
            
            for l in unvisited:
                insert(cleanUrl(base,l), type, depthCounter)
            
            while isVisitingLeft(depthCounter):
                print("Going to depth "+ str(depthCounter), )
                getFromDB = getUnvisitedFromDB(depthCounter)
                for each in getFromDB:
                    print("Visiting "+ each)
                    unvisited = getLink(each, type)
                    print(unvisited)
                    for everyOne in unvisited:
                        insert(cleanUrl(base,everyOne), type, depthCounter+1)
                    updateVisited(each)
                if not isVisitingLeft(depthCounter): 
                    depthCounter += 1
            #for each in getFromDB

            
    finally:
        connection.commit()


base = "http://localhost/"
crawl("http://localhost/","href")

