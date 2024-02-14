import requests
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('id', type=str)
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    response = requests.get(f"https://dcoy1ihhwa.execute-api.us-west-2.amazonaws.com/dev/cars/{args.id}")
    print(response.json())