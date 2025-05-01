from flask import Flask, jsonify
import os
from flask_cors import CORS
import pandas as pd
import googlemaps
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

df = pd.DataFrame()
df_grouped = pd.DataFrame()

load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set")

# Initialize Google Maps API client
# Note: You should set the GOOGLE_MAPS_API_KEY environment variable in your system
# or use a .env file to load it
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

businesses = []

@app.route('/businesses', methods=['GET'])
def get_businesses():
    return jsonify(businesses)

def fetch_lat_long_for_business(row):
    # fetch the coordinates using Google Maps API
    address = f"{row['BUILDING']} {row['STREET']}, {row['BORO']}, NY {row['ZIPCODE']}"
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        print(f"Fetched coordinates for address: {address} - latitude: {latitude}, longitude: {longitude} - business name: {row['DBA']}")
    else:
        print(f"Could not find coordinates for address: {address} - skipping business name: {row['DBA']}")
        return 0, 0
    return latitude, longitude

def init_businesses_for_whole_dataframe():
    # iterate over the rows and create a list of dictionaries
    for uniqueId, row in df_grouped.iterrows():
        latitude = row['LATITUDE']
        longitude = row['LONGITUDE']
        if latitude == 0 and longitude == 0:
            latitude, longitude = fetch_lat_long_for_business(row) 
            if latitude == 0 and longitude == 0:
                # if we STILL couldn't find the coordinates, just skip this business
                continue
            # update the dataframe with the fetched coordinates
            df_grouped.at[uniqueId, 'LATITUDE'] = latitude
            df_grouped.at[uniqueId, 'LONGITUDE'] = longitude
        business = {
            "uniqueId": uniqueId,
            "name": row['DBA'],
            "address": f"{row['BUILDING']} {row['STREET']}, {row['BORO']}, NY {row['ZIPCODE']}",
            "violationSummary": row['VIOLATIONDESCRIPTION'],
            "inspectionDate": row['INSPECTIONDATE'],
            "violationCount": row['VIOLATIONCOUNTS'],
            "cuisineDescription": row['CUISINEDESCRIPTION'],
            "score": row['SCORE'],
            "latitude": latitude,
            "longitude": longitude,
            "grade": row['GRADE'],
        }
        businesses.append(business)

if __name__ == '__main__':
    # TODO fetch this dynamically from the NYC Open Data API
    # (https://data.cityofnewyork.us/Health/DOHMH-New-York-City-Restaurant-Inspection-Results/43nn-pn8j/about_data)
    df = pd.read_csv('./input/DOHMH_New_York_City_Restaurant_Inspection_Results_20250428.csv')
    df.drop_duplicates()

    # Just select the columns we care about for this analysis
    df = df[[
        'CAMIS','DBA','BORO',
        'BUILDING','STREET','ZIPCODE',
        'CUISINE DESCRIPTION','VIOLATION DESCRIPTION',
        'INSPECTION DATE','SCORE','GRADE',
        'Latitude','Longitude'
    ]]

    df = df.set_index('CAMIS')
    df = df.sort_values(by=['CAMIS', 'INSPECTION DATE'], ascending=[True, False])

    # Replace NaN values with 0 for latitude and longitude
    df['Latitude'] = df['Latitude'].fillna(0)
    df['Longitude'] = df['Longitude'].fillna(0)

    # replace nan with empty string for violationSummary
    df['VIOLATION DESCRIPTION'] = df['VIOLATION DESCRIPTION'].fillna('')
    print(df.dtypes)
    print(df.head(20))
    print(df.shape)

    # optionally filter by zip code
    # df = df[df['ZIPCODE'] == 11101]

    # create a new dataframe that groups all violations by CAMIS
    df_grouped = df.groupby(by="CAMIS").agg(
        DBA=('DBA', 'first'),
        BORO=('BORO', 'first'),
        BUILDING=('BUILDING', 'first'),
        STREET=('STREET', 'first'),
        ZIPCODE=('ZIPCODE', 'first'),
        CUISINEDESCRIPTION=pd.NamedAgg(column='CUISINE DESCRIPTION', aggfunc='first'),
        VIOLATIONDESCRIPTION=pd.NamedAgg(column='VIOLATION DESCRIPTION', aggfunc=lambda x: '\n-'.join(x)),
        INSPECTIONDATE=pd.NamedAgg(column='INSPECTION DATE', aggfunc='first'),
        SCORE=('SCORE', 'mean'),
        LATITUDE=('Latitude', 'mean'), # really should be first ha, just curious if they're ever different
        LONGITUDE=('Longitude', 'mean'),
        GRADE=('GRADE', lambda x: ','.join(str(x) for x in x.unique()))
    )

    df_grouped['VIOLATIONCOUNTS'] = df_grouped['VIOLATIONDESCRIPTION'].apply(lambda x: len(x.split('\n-')) - 1)

    # sort by most violations
    df_grouped = df_grouped.sort_values(by='VIOLATIONCOUNTS', ascending=False)

    # filter out businesses with x+ violations
    numViolations = 30
    df_grouped = df_grouped[df_grouped['VIOLATIONCOUNTS'] >= numViolations]
    print(f"Filtered businesses with {numViolations} or more violations: {df_grouped.shape[0]}")
    print(df_grouped.head(20))

    init_businesses_for_whole_dataframe()

    df.to_csv('./output/DOHMH_New_York_City_Restaurant_Inspection_Results_20250428_CLEANED.csv')
    df_grouped.to_csv('./output/DOHMH_New_York_City_Restaurant_Inspection_Results_20250428_SORTED.csv')

    app.run(host="0.0.0.0", port=50000, debug=True)

