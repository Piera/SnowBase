Project
=======

Fall 2014 HB Project, the Snow Finder!
<p></p>
File notes:
<p></p>
<strong>Cron</strong>: Contains reference and scripts that are used to create files used for cron jobs, and the cron jobs.
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
    
<strong>Model</strong>: Contains reference and scripts needed to seed and add station and snow telemetry data to the database.</li></ul>
<p></p>
<ul><li>model.py:  Create data tables, or add to data tables</li>
<li>seed.py: Seed table using reference file and/or by calling station APIs</li>
<li>add.py: Add snow telemetry data to existing database. (Need to set up cron job for this).</li>
<li>requirements.txt: Requirements for virtual environment.</li>
<li>SnowDataParsed2014-11-08-0152Z.csv: Used to seed tables</li></ul>
  
