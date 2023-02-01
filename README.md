# Speedoc Take-Home

### Summary of repository
1) To see all visualizations and explanations, please refer to the notebook named `speedoc_viz.ipynb` under the src folder or feel free to view the pdf version of this notebook. 
2) To run the data cleaning script and visualization notebook, please install the required packages under the `requirements.txt` file in a virtual environment to avoid any version clashes. The following command can be used to install all the requirements:  ``` $ pip install -r /path/to/requirements.txt ```
3) The data cleaning script is found under the src folder, and is titled `speedoc_clean.py`. Explanations for the steps taken in cleaning and feature engineering is described below and in the script. 

### Folder Structure
```
project
│   README.md
│   requirements.txt    
│
└───src
│   │   speedoc_clean.py
│   │   speedoc_viz.ipynb
│   │   speedoc_viz.pdf
│
│   
└───data
    │   austin_bikeshare_stations.csv
    │   austin_bikeshare_trips.csv
```
1) The project directory should contain 2 folders - src and data. 
2) The src file contains all scripts and notebooks, and the data file should contain the csv data. 
3) The current working directory would be the src folder. 


### Cleaning and Feature Engineering Process 
- To run the cleaning data script, please run the following command `python speedoc_clean.py`. Please also ensure that the 2 raw csv files from `https://www.kaggle.com/datasets/jboysen/austin-bike` are located in your local data folder. The output of `speedoc_clean.py` is the prepared data for both trips and stations, found in your data folder.  
- Summary of cleaning steps here:
    - Check for duplicates: None 
    - Check for NA values:
        - `bikeid`: We can't do much about the NAs as each bike id is unique, we can replace the missing bike id's with -1 to indicate that it is a missing bike id. 
        - `month` & `year`: Extract month and year from the start_time column.  
        - `subscriber_type` - Replace missing subscriber types with mode. We may think of predicting this value in the future using the other columns. 
        - `start_station_id` & `end_station_id`: the station names are all there but the id is not given to them. After looking through the data, it seems as if the names have been recorded down incorrectly in the trips dataset. Let us use fuzzy matching to find these strings and draw out the correct mappings for them. 
    - Check for outliers:
        - `duration_minutes`: The duration of a trip cannot be 0, neither can it be the max value of 10981 minutes. That's 180 hours! Furthemore, the average bike trip in Austin, including these outliers is approximately 28 minutes. To settle this, let's say on a given day, a person uses the bike to travel to work in the morning for 1 hr + 8 hrs of work + 1 hr travel back = 10 hours. I will assume that it takes a maximum of 10 hours for a cycle trip in Austin. Anything longer than that means the cycle was either not returned or there was an error in recording. 

- Summary of feature engineering steps to help with viualizations later:
    - We add the following columns to our trips dataset: 
        - `day`: The day of the month. 
        - `dayofweek`: The day of the week. E.g Monday, Tuesday, etc. 
        - `isweekend`: Boolean, whether the `start_time` is a weekend or weekday. 
        - `hour`: The hour of the day
    - We add the following columns to our stations dataset:
        - `days_active`: The number of days the station had at least 1 trip. 
        - `total_traffic`: The total number of trips where the station acted as a start station or and end station. 
        - `traffic_density`: Given by the formula: `total_traffic`/`days_active`. This is because we care about the traffic each station sees per day on average for the days they were active. This is a better gauge of station popularity compared to a station which was open since 2013, and it's due to that that the have a large trip count. 

### Key Findings: Please see speedoc_viz.ipynb or speedoc_viz.pdf for vizualizations and key findings explanations







