import requests
import pandas as pd
import io
from time import process_time as timer

#Create empty list to get weather station data.

ghcnd_stations_data = []

#from https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily under stations link (metadata)

#Retrieve data from text file and change each line into a list of data items. Needed for getting climate data for all stations of interest.

with open('ghcnd_stations.txt', 'r') as in_file:
   lines = [line.strip() for line in in_file]
   for i in lines:
       ghcnd_stations_data.append(i.split())

#Create a csv file for the stations by seperating the data items with commas for each line. 
#Make sure to add "Station,Lat,Long,Measurement,Province" to the first line of the ghcnd_stations.csv once created to use the tableau file.

with open('ghcnd_stations.csv', 'w') as out_file:
    for i in ghcnd_stations_data:
        out_file.write(str(",".join(i)))
        out_file.write('\n')

#Move data into a Pandas dataframe

station_data = pd.DataFrame(ghcnd_stations_data)

#Remove all columns except station ID column used to get climate data for all stations of interest.

station_data = station_data.iloc[:,0].values.tolist()

#Create class for NCEI API. Used to retrieve climate data for individual stations

class c_ncei_data_service_api:

    def __init__(self, dataset, data_types,  stations, start_date_time, end_date_time):

        # Set the base API URL
        self._base_api_url = 'https://www.ncei.noaa.gov/access/services/data/v1/?'

        # Retrieve data
        self._dataset = self.call_api(dataset, data_types, stations, start_date_time, end_date_time)

    def call_api(self, dataset, data_types, stations, start_date_time, end_date_time):
    
        # Create the full API request URL and submit it to the server. See https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation.

        full_url = self._base_api_url + 'dataset=' + dataset + '&dataTypes=' + data_types + '&stations=' + stations + '&startDate=' + start_date_time + '&endDate=' + end_date_time + '&format=csv' + '&units=standard'
        
        response = requests.get(full_url)

        return response.text
    
    def get_data(self):

        # Return the data retrieved with the API call.

        return self._dataset

#Create empty Pandas dataframe to store climate data

climate_data = pd.DataFrame()

#Sends requests climate data for all stations of interest. Uses to NCEI data service API. If you don't want to wait for more than 3 hours, replace "len(station_data)" with a smaller number like 30.

data = []

start = timer()
for i in range(0,len(station_data)):
    api_result = c_ncei_data_service_api('daily-summaries','TAVG,TMAX,TMIN,WDFG,WSFG,PRCP,SNOW,SNWD', station_data[i] ,'2013-01-01','2023-12-31') #Send Request
    data.append(pd.read_csv(io.StringIO(api_result.get_data()),on_bad_lines='skip')) #Retrieve data as Pandas Dataframe and append it to a list of dataframes
    
climate_data = pd.concat(data) #Combine list of dataframes into the climate_data dataframe
end = timer()

print(climate_data)
print(end-start, "minutes  for completion")
climate_data.to_csv('WeatherData.csv', index = False) #Create csv containing the climate data.
