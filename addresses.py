import requests
import os

def address(latitude, longitude):
    MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_API_KEY") #accessing API key from environment variables
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json"
    params = {"access_token": MAPBOX_ACCESS_TOKEN}
    response = requests.get(url, params=params)
           
    if response.status_code == 200:
        data = response.json()
        
        # Extracting relevant information from the response
        features = data["features"]
        try:
            place_name = features[0]["place_name"]
            return place_name            
        except KeyError:
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")


print(address(37.8331415, -121.9827142))

