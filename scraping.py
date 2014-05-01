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
  
def main():
	if len(sys.argv) < 4: 
		print("Insufficient arguments. Proper example: \"python scraping.py P 500 2000\"")
		sys.exit()
	print("Starting...")
	
	# get required parameters from call
	NParg = sys.argv[1]
	start = int(sys.argv[2])
	end = int(sys.argv[3])
	
	sleep = 0  # how much to wait in between calls
	
	if NParg == "N":
		getNotices(start, end, sleep)
	if NParg == "P":
		getProperties(start, end, sleep)
	print("Done!")
    
def getProperties(start, end, sleep = 0):
	print("Getting Properties...")
	header = [["propID", "ownerName", "ownerAdd", "propType", "cashRep", "sharesRep", "nameSec", "repBy", "newAdd", "lat", "lng", "dateRetrieved", "URL"]]
	propertyList = list(header)
	todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
	lastGood = start
	csvFirst = start # for printing the CSV
	for num in range(start,end+1):
		# 4/28/2014 - search on propertyID, not propertyRecID. Not dynamic. 
		# https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyID=001331061
		# 9 digit numbers, needs to be padded with 0s
	
		url = "https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyID=" + str(num).zfill(9)
		print(str(num - start + 1) + "/" + str(end - start + 1) + ": Querying " + url)
		try: 
			property = processProperty(url) + [todaysdate] + [url]
			propertyList.append(property)
			lastGood = num # if this worked, save it as the last Good
		except Exception:
			print("Error processing " + str(url) + "!")
			pass
		if num > lastGood + 100: # if there were 100 straight errors
			print("100 straight errors. Quitting now.")
			break			
		time.sleep(sleep)
		if num % 1000 == 0:
			print("Writing CSV, moving to next CSV.")
			outputCSV(propertyList,"properties_" + str(csvFirst) + "_" + str(num))
			propertyList = list(header) # reset propertyList - remember, lists are mutable.
			csvFirst = num
	print("Writing last CSV.")
	outputCSV(propertyList,"properties_" + str(csvFirst) + "_" + str(end))
	
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
	
def getNotices(start, end, sleep = 0): # processes Notices from start to end, saves CSV
	print("Getting Notices...")
	noticeList = [["bizContact", "propType", "cashRep", "sharesRep", "nameSec", "dateRep", "dateCont", "ownerName", "ownerAdd", "dateRetrieved", "URL"]]
	todaysdate = datetime.datetime.now().strftime("%Y-%m-%d")
	for num in range(start,end+1):
		url = "https://ucpi.sco.ca.gov/ucp/NoticeDetails.aspx?propertyRecID=" + str(num)
		print(str(num - start + 1) + "/" + str(end - start + 1) + ": Querying " + url)
		try: 
			notice = processNotice(url) + [todaysdate] + [url]
			noticeList.append(notice)
			lastGood = num # if this worked, save it as the last Good pull
		except AttributeError:
			print("Error processing " + str(url) + "!")
			pass
		if num > lastGood + 1000: # if there were 1000 straight errors
			print("1000 straight errors. Quitting now.")
			break
		time.sleep(sleep)
	outputCSV(noticeList,"notices_" + str(start) + "_" + str(lastGood))
	
def processNotice(requestURL): # given a URL, retrieves a single webpage and returns a list 
	response = urllib2.urlopen(requestURL) 
	responseHTML = response.read()
	soup = BeautifulSoup(responseHTML)
	
	# process the holder name
	Holder = fixList(soup.find('td', id="HolderNameData").contents)
	
	# process the property details table
	PropertyDetailsTable = soup.find('table', id="PropertyDetailsTable")
	PropertyDetailsRows = PropertyDetailsTable.findAll('tr')
	
	# get the second column of each row - that's our data
	PropertyDetailsList = []
	for row in PropertyDetailsRows:
		col = row.findAll('td')[1].contents
		if isinstance(col, list): # if it's a list, fix to string
			col = fixList(col)
		else:
			col = col[0].encode('ascii', 'ignore') # otherwise, just get string
		PropertyDetailsList.append(col.strip())
	noticeRow = [Holder] + PropertyDetailsList
	return(noticeRow)
	
def getGeog(address):
	# take in an address, return the address, (lat, lon) in a list
	us = geocoders.GeocoderDotUS()
	try:
		place, (lat, lng) = us.geocode(address)
	except TypeError:
		print "Couldn't geocode address."
		place, (lat, lng) = "", (0,0)
	return list((place, lat, lng))
	
def fixList(tagstrList): 
	# take in a list that includes strings and tags, return property formatted string and ignore tags
	fixed = ""
	for part in tagstrList:
		if isinstance(part, unicode):
			fixed = fixed + part.strip().encode('ascii', 'ignore') + "\n"
	return(fixed.strip())
	
def outputCSV(mylist, name): 
	writer=csv.writer(file("data/" + name + '.csv','wb'),dialect='excel')
	writer.writerows(mylist)
	print("Wrote " + name + '.csv')
      
if __name__ == "__main__":
	main() 
