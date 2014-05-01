### gets table from https://ucpi.sco.ca.gov/ucp/... 
### outputs csv

### There are two types (that I know of so far): Property and Notice
### - Property: https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyRecID=8162422
### - Notice: https://ucpi.sco.ca.gov/ucp/NoticeDetails.aspx?propertyRecID=2033380
 
# takes required arguments N/P, min, max. ex:
# - python scraping.py N 1 1000
# - python scraping.py P 500 2000
 
import sys
import csv 
import time 
import urllib2 
import datetime 
from bs4 import BeautifulSoup 
from geopy import geocoders
from random import randint
  
def main():
	print("Starting...")
	
	# only optional parameter is the max number of queries
	maxQueries = 2001
	if len(sys.argv) > 1:
		maxQueries = sys.argv[1]
	
	sleep = 0  # how much to wait in between calls
	getProperties(sleep, maxQueries)
	print("Done!")
    
def getProperties(sleep = 0, maxQueries = 2001):
	print("Getting Properties...")
	header = [["propID", "ownerName", "ownerAdd", "propType", "cashRep", "sharesRep", "nameSec", "repBy", "newAdd", "lat", "lng", "dateRetrieved", "URL"]]
	propertyList = list(header)
	errorCount = 0
	i = 1
	while (errorCount <= 100 and i <= maxQueries):
		randID = randint(1, 1000000) # right now it doesn't seem like it goes past 10m. maybe spottier after 1m?
		# https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyID=001331061
		# 9 digit numbers, needs to be padded with 0s
	
		dt = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
		url = "https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyID=" + str(randID).zfill(9)
		print(str(i) + ": " + url)
		try: 
			property = processProperty(url)
			errorCount = 0
		except Exception:
			print("Property ID " + str(randID) + " not found.")
			property = [randID, "", "", "", "", "", "", "", "", "", ""]
			errorCount = errorCount + 1
			pass
		propertyList.append(property + [dt] + [url])
		time.sleep(sleep)
		if i % 1000 == 0:
			print("Writing CSV.")
			outputCSV(propertyList,"properties_" + str(dt))
			propertyList = list(header) # reset propertyList - remember, lists are mutable.
		i = i + 1
	
def processProperty(requestURL):
	response = urllib2.urlopen(requestURL) 
	responseHTML = response.read()
	soup = BeautifulSoup(responseHTML)
	
	# get property ID number
	propID = soup.find('table', id="tbl_HeaderInformation").findAll('span')[2].contents[0].encode('ascii', 'ignore').strip()
	
	PropertyDetailsTable = soup.find('table', id="PropertyDetailsTable")
	PropertyDetailsList = getListFromTable(PropertyDetailsTable)

	# They add two fields (sharesRep and nameSec) if shares were reported
	if PropertyDetailsTable.find('tr', id="ctl00_ContentPlaceHolder1_trNumberOfShares") is None:
		PropertyDetailsList.insert(4, "")
		PropertyDetailsList.insert(4, "")
	
	# get latlon and better address from address
	geogList = getGeog(PropertyDetailsList[1])
		
	propertyRow = [propID] + PropertyDetailsList + geogList
	return(propertyRow)

def getListFromTable(table): 
	# processes a table where we want the second column of every row, returns list
	rows = table.findAll('tr')
	# get the second column of each row - that's our data
	outputList = []
	for row in rows:
		col = row.findAll('td')[1].contents
		if isinstance(col, list): # if it's a list, fix to string
			col = fixList(col)
		else:
			col = col[0].encode('ascii', 'ignore') # otherwise, just get string
		outputList.append(col.strip())
	return(outputList)
	
def fixList(tagstrList): 
	# take in a list that includes strings and tags, return property formatted string and ignore tags
	fixed = ""
	for part in tagstrList:
		if isinstance(part, unicode):
			fixed = fixed + part.strip().encode('ascii', 'ignore') + "\n"
	return(fixed.strip())

def getGeog(address):
	# take in an address, return the address, (lat, lon) in a list
	us = geocoders.GeocoderDotUS()
	try:
		place, (lat, lng) = us.geocode(address)
	except TypeError:
		print "Couldn't geocode address."
		place, (lat, lng) = "", (0,0)
	return list((place, lat, lng))
	
def outputCSV(mylist, name): 
	writer=csv.writer(file("data/" + name + '.csv','wb'),dialect='excel')
	writer.writerows(mylist)
	print("Wrote " + name + '.csv')
      
if __name__ == "__main__":
	main() 
