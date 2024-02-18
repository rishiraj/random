import requests

def bind_extractor_to_repository():
    url = "http://localhost:8900/namespaces/default/extraction_policies"
    headers = {"Content-Type": "application/json"}
    data = {
        "extractor": "pdf-extractor",
        "name": "pdfs"
    }

    response = requests.post(url, json=data, headers=headers)

    # Check for successful request
    if response.status_code != 200:
        print(f"Failed to bind extractor: {response.status_code}")

bind_extractor_to_repository()