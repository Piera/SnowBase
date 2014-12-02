Hackbright Final Project: SnowBase
============================================

<h2>Overview:</h2>

<p></p>
<ul><li>SnowBase connects winter backcountry enthusiasts to up-to-date snow pack conditions with one click.</li>
<li>For those who are eagerly awaiting new snow, easy-to-use text alerts are available for over 860 SNOTEL mountain stations.</li>
<li>Data generated by the USDA's SNOTEL network is brought to life on a daily basis through the Powderlin.es API, database, mapping, texting and data visualization technologies.</li></ul>

![ScreenShot](https://raw.githubusercontent.com/Piera/Project/master/MVC/ScreenShot.png)

<p></p>
<h2>About SNOTEL:</h2>
The SNOTEL system is a system of backcountry snow telemetry stations maintained by the USDA for the purposes of monitoring water resources.  There are 867 reporting stations located in the western United States, including Alaska.  

<p></p>
<h2>Technologies:</h2>
<p></p>
<ul><li>SQLite</li>
<li>Python</li>
<li>Flask</li>
<li>SQLAlchemy</li>
<li>JavaScript</li>
<li>jQuery</li>
<li>d3</li>
<li>Bootstrap</li>
<li>HTML/CSS</li>
<li>Powderlin.es SNOTEL API</li>
<li>Google Maps API</li>
<li>Twilio API</li></ul>

<h2>Key Challenges:</h2>

<strong>Data:</strong> 

While the Powderlin.es API provides a robust service, the underlying mechanical system of SNOTEL stations can misfire, with stations serving missing data points, and the API experiencing the occasional delay from the USDA server.  Using an SQLite database to store data points ensures that users will not be exposed to delays, and will always find data for their desired locations.  Filtering the data sets for minimally viable data points, and handling cases of non or partially reporting stations was another important consideration.  Determining the minimally viable data point / data set is yet another - this is a judgement that will evolve with further familiarity with the SNOTEL system, and with user feedback.  QA on data points is currently conducted by comparing data on the SNOTEL site to chart and graph values on SnowBase.

![ Missing data ](https://raw.githubusercontent.com/Piera/Project/master/MVC/Missing_data.png) 

<strong>Search Performance:</strong> 

SnowBase takes user input and uses Google Maps geocoding, and the haversine formula to calculate the 10 closest stations in the database, returning the latest snow telemetry data for each.  This query is a classic example of a "Nearest Neighbor Search" problem.  The approach I took was to use geographical partitions to bucket the stations; so that only a subset of data is queried with each input.  I used a benchmark location input to keep track of algorithm performance, and improved the search speed by approximately 2 seconds from the original brute-force linear algorithm.  I am interested in furthering the geo partitioning algorithm and/or exploring other algorithmic solutions before upgrading the database.

![ Benchmark search ](https://raw.githubusercontent.com/Piera/Project/master/MVC/Benchmark_search.png)  

<strong>Usability:</strong> 

Existing SnoTel representations require users to zoom, scroll, and click excessivly to find the data for a given SNOTEL station.  Currently, there is no way to compare data from any two SnoTel stations.  For this project, I made a "one click" commitment to the end user. Data is easily accessed and compared; I used jQuery and d3 to effortlessly render trending data on when the user hovers on the data chart.  I also included a heatmap layer, gradient key, and marker indicators on the map, so that users can quickly identify where the deepest snow is. 

![ Comparison chart ](https://raw.githubusercontent.com/Piera/Project/master/MVC/Comparison_chart.png)  

The simplicity of the text alert system also reflects the "one click" commitment; having users log in to set or manage text messages felt too heavy handed for the simple task of setting up an alert.  Instead, users text a code to the SnowBase phone number and the alert is set via the Twilio API. After the initial text receipt, the user receives a single text alert when there is new snow at the station same text are instructions for how to reset the alert.  Users can effectively manage their alerts from their phone without visiting SnowBase.  This light solution employs a simple data table and Boolean toggle system.

![ Text Alert ](https://raw.githubusercontent.com/Piera/Project/master/MVC/Text_alert.jpg)  

<p><p>
<h2>Instructions:</h2>

To run SnowBase:
<ul><li>Clone repository</li>
<li>From within MVC directory:</li>
<li>```pip install -r requirements.txt```</li>
<li>```source env/bin/activate```</li>
<li>```python finder.py```</li></ul>

To update or add data points at any time:
<ul><li>Update add.py with current file location of the url file, then:</li>
<li> `python add.py` </li></ul>

To enable the Twilio text alert functionality:
<ol><li> Sign up for a Twilio account</li>
<li>Save account keys</li>
<li>In MVC directory, download and unzip ngrok</li>
<li>```source env/bin/activate```</li>
<li>```python finder.py```</li>
<li>```./ngrok 5000```</li>
<li>Update Twilio with the ngrok URL/alerts</li>
<li>Text codes to your new Twilio number</li>
<li>Alerts are distributed with each run of Add.py</li>
<li>Or, run scan.py to trigger alerts separately</li></ol>

<p></p>
<h2>File Directory:</h2>

<p></p> 
<strong>MVC</strong>: Contains flask app files, and reference/scripts needed to create the database of stations and snow telemetry data points.
<p></p>
<ul><li>requirements.txt: Requirements for virtual environment.</li>
<li>finder.py: Flask app for simple capture of lat/long, returns closest stations with data.</li>
<li>haversine.py: Computation for distance between two points given lat/long for each.</li>
<li>static and template folders: contain files for view rendering</li>
<li>model.py:  Create data tables, or add to data tables</li>
<li>seed.py: Seed table using reference file and/or by calling station APIs</li>
<li>add.py: Add snow telemetry data to existing database.</li>
<li>alerts.py: Adds and updates alert data to alerts database
<li>scan.py: Scans database for alerts, sends alerts
<li>SnowDataParsed2014-11-08-0152Z.csv: Used to seed tables</li>
<li>Snow.db: Including db, for running finder.py</li></ul>

<p></p>
<strong>Cron</strong>: Contains reference and scripts that are used to create files used for cron jobs, and the cron job scripts.
<p></p>
<ul><li>create_station_json.py: Creates a csv file of all of the stations, including the station triplet needed for the API url.</li>
<li>create_urls.py: Creates a file of all API urls needed to call in a complete set of telemetry data.</li>
<li>json_cron.py: Calls all station APIs and saves a file of json objects. Runs daily.</li>
<li>parsed_cron.py: Calls all station APIs and saves a csv file of parsed data from each station. Runs daily.</li>
<li>StationJSON: File of json objects from each station.</li>
<li>stationsTriplets.csv: File of station triplets used to create API urls.</li>
<li>APIurls.csv: csv file of API urls for all stations.</li>
<li>APIurls_short.csv:  short csv file of API urls for testing purposes.</li>
<li>KEY: Key for parsing the output from the parsed_cron.py file.</li>
<li>Various csv files are included as sample output</li></ul>


