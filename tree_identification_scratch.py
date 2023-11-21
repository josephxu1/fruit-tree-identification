# %%
import requests
import json
from pprint import pprint
import os

API_KEY = os.getenv("PLANTNET_API_KEY")
print(API_KEY)
PROJECT = 'namerica'  # try "weurope" or "canada"
api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"


image_path_1 = "./cropped tree images/tree3.jpg"
image_data_1 = open(image_path_1, 'rb')

data = {
    'organs': ['entire']
}

files = [
    ('images', (image_path_1, image_data_1)),
    # ('images', (image_path_2, image_data_2))
]

req = requests.Request('POST', url=api_endpoint, files=files, data=data)
prepared = req.prepare()

s = requests.Session()
response = s.send(prepared)
json_result = json.loads(response.text)

pprint(response.status_code)
# %%
json_result['results'][:3]
# %%
