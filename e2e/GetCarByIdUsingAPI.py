import requests
import argparse,os

API_GTW=os.getenv('API_GTW')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    response = requests.get(f"{API_GTW}/cars/{args.id}")
    print(response.json())