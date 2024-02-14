import sys
import requests
import json

def search_repository(query):
    url = "http://localhost:8900/repositories/default/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "index": "papers.embedding",
        "query": query,
        "k": 1
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search.py '<query>'")
        sys.exit(1)
    query = sys.argv[1]
    result = search_repository(query)
    print(json.dumps(result, indent=4))