import requests

def bind_extractor_to_repository():
    url = "http://localhost:8900/repositories/default/extractor_bindings"
    headers = {"Content-Type": "application/json"}
    data = {
        "extractor": "tensorlake/minilm-l6",
        "name": "papers"
    }

    response = requests.post(url, json=data, headers=headers)

    # Check for successful request
    if response.status_code != 200:
        print(f"Failed to bind extractor: {response.text}")
    
    print("Ready! Use extractor name: papers")

bind_extractor_to_repository()