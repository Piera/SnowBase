import json
import csv

# This script was used to open the StationJSON, and create a CSV file of all of 
#  the stations, including the triplets that will be used create_urls.py.

json_data=open('StationJSON')
data = json.load(json_data)
f = csv.writer(open("stationsTriplets.csv", "wb+"))
f.writerow(["triplet", "station", "elevation", "latitude", "longitude"])
for i in range(len(data)):
	f.writerow([data[i]['triplet'],
			   data[i]['name'], 
               data[i]['elevation'], 
               data[i]['location']['lat'],
               data[i]['location']['lng']])
json_data.close()