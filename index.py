import json
import csv
import pandas as pd
import collections
from haversine import haversine, Unit

# Load the required cities and get the zip code prefixes

df = pd.read_csv (r'unique_city_zip.csv')
df["Zip"] = df["Zip"].astype(str).apply(lambda x: x.zfill(5))
df["prefix"] =  df["Zip"].astype(str).str[:-2]
df["state"] = ""

# Open all of the zip codes in the US

with open('USCities.json') as json_file:
    data = json.load(json_file)

# Get only one zone for each prefix

filtered_areas = []

prefix = "000"

for d in data:
    if str(d["zip_code"])[:-2].zfill(3) != prefix and d["latitude"]:
        d["prefix"] = str(d["zip_code"])[:-2].zfill(3)
        filtered_areas.append(d)
        prefix = str(d["zip_code"])[:-2].zfill(3)
    
# Generate the final document

final_result = []

cbsa_file = pd.read_csv (r'ZIP_CBSA_122020.csv')

# For each main ZIP

for index, row in df.iterrows():
    state = None  # Get the zip code state
    for k in filtered_areas:
        if k['prefix'] == row["prefix"]:
            df.loc[index,'state'] = k["state"]
            break

# Get the CBSA

    cbsa = None
    for cbsa_index, cbsa_row in cbsa_file.iterrows():
        if int(cbsa_row["ZIP"]) == int(row["Zip"]):
            # print("Found it!")
            # print(index)
            cbsa = int(cbsa_row["CBSA"])
            # print(cbsa)
            break
    print(cbsa)
# Get the validated zips

    validated_zips = []
    main_area_latitude = None
    main_area_longitude = None
    for k in filtered_areas:
        if k["prefix"] == row["prefix"]:
            main_area_latitude = k["latitude"]
            main_area_longitude = k["longitude"]
            break
    main_area_coordinates = (float(main_area_latitude), float(main_area_longitude))
    for k in filtered_areas:
        test_area_coordinates = (float(k["latitude"]), float(k["longitude"]))
        if row["state"] == k["state"] and haversine(main_area_coordinates, test_area_coordinates, unit=Unit.MILES) < 100:
            validated_zips.append(k["prefix"])

# Append the result

    final_result.append(     
        {
            'Zip Code' : row["Zip"],
            'State' : row["state"],
            'CBSA' : cbsa,
            'validated_3_digit_zips' : validated_zips
        }
        )
    
# Save as JSON
print("Successfully Hacked CIA")
print(final_result[2])

with open('results.json', 'w') as result_file:
    json.dump(final_result, result_file)
    print("dumped")
