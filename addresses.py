import requests
import os

def address(latitude, longitude):
    print(os.environ)
    MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_API_KEY") #accessing API key from environment variables
    print(MAPBOX_ACCESS_TOKEN)
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json"
    params = {"access_token": MAPBOX_ACCESS_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # Extracting relevant information from the response
        features = data["features"]
        if features:
            first_result = features[0]
            place_name = first_result["place_name"]
            
            print(f"Location: {place_name}")
        else:
            print("No results found.")
    else:
        print(f"Request failed with status code: {response.status_code}")



address(-122.04084960054918,37.94288574409289)