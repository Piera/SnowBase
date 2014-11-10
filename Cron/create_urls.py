import csv

# This script creates a file of all of the URLs using the results of the create_station_json.py file
#  These URLs will be used for the chron job to collect json from each station.

f = csv.writer(open("APIurls.csv", "wb+"))
with open('stationsTriplets.csv', 'rb') as csvfile:
	triplet_reader = csv.reader(csvfile, delimiter=',')
	for row in triplet_reader:
		triplet = row[0]
		APIurl = ('http://api.powderlin.es/station/{}?days=0'.format(triplet))
		f.writerow([APIurl])