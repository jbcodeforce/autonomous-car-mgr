import requests
import os,json

API_GTW=os.getenv('API_GTW')

if __name__ == '__main__':
    response = requests.get(f"{API_GTW}/cars")
    print(json.dumps(response.json(),indent=2))