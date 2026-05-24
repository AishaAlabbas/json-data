import requests
import json

url = "https://raw.githubusercontent.com/wimalen/jsonproducten/refs/heads/main/landen.json"

response = requests.get(url)

data = response.json()

print("Lijst van landen:\n")

for land in data:
    print(land)