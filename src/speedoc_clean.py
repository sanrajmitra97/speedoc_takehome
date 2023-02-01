# This script will read in the raw bike data and output a cleaned dataset stored in the data folder.
#Import pandas 
import pandas as pd


# Read in Data
trips = pd.read_csv('../data/austin_bikeshare_trips.csv')
stations = pd.read_csv('../data/austin_bikeshare_stations.csv')


# Clean Data
# 1) No Duplicates - yay!
# 2) NA values
# It seems like there are not too many missing values compared to the number of rows. 
# - `bikeid`: we can't do much about the NAs as each bike id is unique, we can replace the missing bike id's with -1 to indicate that it is a missing bike id. 
# - `month` & `year`: Extract month and year from the start_time. 
# - `subscriber_type` - Replace missing subscriber types with mode. We may think of predicting this value in the future using the other columns. 
# - `start_station_id` & `end_station_id`: the station names are all there but the id is not given to them. After looking through the data, it seems as if the names have been recorded down incorrectly in the trips dataset. Let us use fuzzy matching to find these strings. 

# Clean Bike Id's - replace NaN values with -1. 
trips['bikeid'] = trips['bikeid'].fillna(-1)
trips['bikeid'] = trips['bikeid'].astype(int)

# Clean all the time columns - We use the start time to extract out year and month values. 
# We also add in new features such as day, dayofweek, isweekend to help us with visualizations later.
trips['checkout_time'] = pd.to_datetime(trips['checkout_time']).dt.time
trips['start_time'] = pd.to_datetime(trips['start_time'], format='%Y-%m-%d %H:%M:%S')
trips['year'] = trips['start_time'].dt.year
trips['month'] = trips['start_time'].dt.month
trips['day'] = trips['start_time'].dt.day
trips['dayofweek'] = trips['start_time'].dt.dayofweek
mapping = {0:'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4:'Friday', 5: 'Saturday', 6:'Sunday'}
trips['isweekend'] = trips['dayofweek'].apply(lambda x: x == 5 or x==6)
trips['dayofweek'] = trips['dayofweek'].apply(lambda x: mapping[x])

# Clean subscriber type - Take mode of the subscriber. 
trips['subscriber_type'] = trips['subscriber_type'].fillna('Walk Up')

# Clean stations 
# To identify the stations to drop, we use a fuzzy matching algorithm to determine similar station spellings.

# We are removing the following stations because they are idless and don't have a 1:1 definite mapping. Furthermore, there arent
# many rows as compared to the number of total rows we have. 
# Clean Start Station
stations_to_drop = ['Stolen', 'MapJam at Hops & Grain Brewery', 'Mobile Station @ Bike Fest', 'Mobile Station', 'MapJam at French Legation', 
                   'Mobile Station @ Unplugged', 'MapJam at Pan Am Park', 'Re-branding', 'Marketing Event', 'MapJam at Scoot Inn']
trips2 = trips[~trips.start_station_name.isin(stations_to_drop)]

start_station_mappings = {
    'Zilker Park at Barton Springs & William Barton Drive': ('Zilker Park', 2574), 
    'ACC - West & 12th': ('ACC - West & 12th Street', 2546), 
    'Convention Center/ 3rd & Trinity': ('Convention Center / 3rd & Trinity', 2539), 
    'Red River @ LBJ Library': ('Red River & LBJ Library', 1004), 
    'East 11th Street at Victory Grill': ('East 11th St. at Victory Grill', 2568), 
    'Main Office': ('OFFICE/Main/Shop/Repair', 1001), 
    'Shop': ('OFFICE/Main/Shop/Repair', 1001), 
    'Repair Shop': ('OFFICE/Main/Shop/Repair', 1001), 
    'Customer Service': ('OFFICE/Main/Shop/Repair', 1001), # Seems like this is a place where customer service would be located
    'Mobile Station @ Boardwalk Opening Ceremony': ('Boardwalk West', 3687)
}

def adjust_ids(idx, stn_name, station_mappings):
    if stn_name in station_mappings:
        true_id = station_mappings[stn_name][1]
        return true_id
    return idx


trips2['start_station_id'] = trips2.apply(lambda x: adjust_ids(x.start_station_id, x.start_station_name, start_station_mappings), axis=1)
trips2['start_station_name'] = trips2['start_station_name'].apply(lambda x: start_station_mappings[x][0] if x in start_station_mappings else x)

# Clean End Station
stations_to_drop = ['Stolen', 'Re-branding', 'Missing', 'Marketing Event', 'MapJam at Hops & Grain Brewery', 'Mobile Station @ Bike Fest', 'Mobile Station', 'MapJam at French Legation', 
                   'Mobile Station @ Unplugged', 'MapJam at Pan Am Park', 'MapJam at Scoot Inn']
end_station_mappings = {
    'Repair Shop': ('OFFICE/Main/Shop/Repair', 1001), 
    'Zilker Park at Barton Springs & William Barton Drive': ('Zilker Park', 2574), 
    'Convention Center/ 3rd & Trinity': ('Convention Center / 3rd & Trinity', 2539), 
    'ACC - West & 12th': ('ACC - West & 12th Street', 2546), 
    'Red River @ LBJ Library': ('Red River & LBJ Library', 1004), 
    'East 11th Street at Victory Grill': ('East 11th St. at Victory Grill', 2568), 
    'Main Office': ('OFFICE/Main/Shop/Repair', 1001), 
    'Shop': ('OFFICE/Main/Shop/Repair', 1001), 
    'Repair Shop': ('OFFICE/Main/Shop/Repair', 1001), 
    'Customer Service': ('OFFICE/Main/Shop/Repair', 1001), # Seems like this is a place where customer service would be located
    'Mobile Station @ Boardwalk Opening Ceremony': ('Boardwalk West', 3687),
    'Main Shop': ('OFFICE/Main/Shop/Repair', 1001)
}

trips3 = trips2[~trips2.end_station_name.isin(stations_to_drop)]
trips3['end_station_id'] = trips.apply(lambda x: adjust_ids(x.end_station_id, x.end_station_name, end_station_mappings), axis=1)
trips3['end_station_name'] = trips3['end_station_name'].apply(lambda x: end_station_mappings[x][0] if x in end_station_mappings else x)
final_trips = trips3.copy()
final_trips['end_station_id'] = final_trips['end_station_id'].astype(int)
final_trips['start_station_id'] = final_trips['start_station_id'].astype(int)

# Merge trips and stations dataset. 
trips_merge1 = final_trips.merge(stations, how='left', left_on=['end_station_id'], right_on=['station_id'])
trips_merge1 = trips_merge1.rename(columns={'latitude': 'end_lat', 'location': 'end_location', 'longitude': 'end_long', 'status': 'end_status'})
trips_merge1 = trips_merge1.drop(['station_id', 'name'], axis=1)
trips_merge1 = trips_merge1[['bikeid', 'checkout_time', 'duration_minutes', 'end_station_id',
                             'end_station_name', 'end_lat',
       'end_location', 'end_long', 'end_status', 
                            'month', 'start_station_id', 'start_station_name',
       'start_time', 'subscriber_type', 'trip_id', 'year', 'day', 'isweekend', 'dayofweek']]
trips_merge2 = trips_merge1.merge(stations, how='left', left_on=['start_station_id'], right_on=['station_id'])
trips_merge2 = trips_merge2.rename(columns={'latitude': 'start_lat', 'location': 'start_location', 'longitude': 'start_long', 
                                           'status': 'start_status'})

trips_merge2 = trips_merge2.drop(['station_id', 'name'], axis=1)
trips_merge2 = trips_merge2[['bikeid', 
                             'checkout_time', 'start_time', 'duration_minutes', 'day', 'month', 'year', 
                             'subscriber_type', 'trip_id', 
                            'end_station_id', 'end_station_name', 'end_lat', 'end_location', 'end_long', 'end_status', 
                            'start_station_id', 'start_station_name', 'start_lat','start_location', 'start_long', 'start_status', 'isweekend', 'dayofweek']]


# Clean outliers in duration_minutes
# The duration of a trip cannot be 0, neither can it be the max value of 10981. That's 180 hours! 
# Furthemore, the average bike trip in Austin, including these outliers is approximately 28 minutes. 
# To settle this, let's say on a given day, a person uses the bike to travel to work in the morning 
# for 1 hr + 8 hrs of work + 1 hr travel back = 10 hours. I will assume that it takes a maximum of 
# 10 hours for a cycle trip in Austin. Anything longer than that means the cycle was either not 
# returned or there was an error in recording. 

trips_merge2 = trips_merge2[trips_merge2.duration_minutes!=0]
# suspicious_trips =  trips_merge2[trips_merge2.duration_minutes > 10*60]
trips_merge3 = trips_merge2[trips_merge2.duration_minutes <= 10*60]


# final trips dataset
df = trips_merge3.copy()
df['hour'] = df['checkout_time'].apply(lambda x: x.hour) # Add in the hour as a feature for visualizations


# Prepare stations dataset
# We want to get the traffic density for each station
# traffic density of a station = total number of times people have parked and used bikes from station / number of days this station has been operational. 
# We want to do this because some stations see high number of rides just because they have been opened for a while, but this does not mean they are a high traffic station. 

station_names = stations.name.values
res = {}
for val in station_names:
    # Number of active day
    no_days = df[(df.start_station_name == val) | (df.end_station_name == val)]['start_time'].dt.date.value_counts().shape[0]
    
    #we count the number of trips as grpby start + grpby end
    start_trips = df.groupby(['start_station_name']).count()['bikeid']
    end_trips = df.groupby(['end_station_name']).count()['bikeid']
    start_trips_count = start_trips[start_trips.index==val].values[0]
    end_trips_count = end_trips[end_trips.index==val].values[0]
    total_trips =start_trips_count + end_trips_count
        
    mask = stations.name == val    
    stations.loc[mask, 'days_active'] = no_days
    stations.loc[mask, 'total_traffic'] = total_trips
    stations['traffic_density'] = stations['total_traffic']/stations['days_active']

df.to_csv('../data/prepared_trips.csv')
stations.to_csv('../data/prepared_stations.csv')