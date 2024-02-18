import time
import os
import requests
import re
from pypdf import PdfReader

def split_long_strings(string_list, max_words=128):
    new_list = []
    for string in string_list:
        words = string.split()  # Split the string into words
        if len(words) > max_words:
            # Split into chunks based on max_words
            for i in range(0, len(words), max_words):
                chunk = ' '.join(words[i:i + max_words])
                new_list.append(chunk)
        else:
            new_list.append(string)
    return new_list

def monitor_folder(folder_path):
    """Monitors a folder for new files and add them to namescape.

    Args:
        folder_path (str): The path to the folder to monitor.
    """
    # URL of the endpoint
    url = "http://localhost:8900/namespaces/default/add_texts"
    
    # Headers for the request
    headers = {"Content-Type": "application/json"}

    # Print the contents of existing files
    for existing_file in os.listdir(folder_path):
        file = os.path.join(folder_path, existing_file)
        print(file)
        reader = PdfReader(file)
        texts = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text)
        
        texts = split_long_strings(texts)

        for chunk in texts:
            # Prepare the data payload as a dictionary
            payload = {"documents": [{"text": chunk}]}
            
            # Make the POST request
            response = requests.post(url, json=payload, headers=headers)
            
            # Check for successful request
            if response.status_code != 200:
                print(f"Failed to add document: {response.text}")

    before = dict([(f, None) for f in os.listdir(folder_path)])
    while True:
        after = dict([(f, None) for f in os.listdir(folder_path)])
        added = [f for f in after if not f in before]

        if added:
            for new_file in added:
                file = os.path.join(folder_path, new_file)
                print(file)
                reader = PdfReader(file)
                texts = []

                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    texts.append(text)
                
                texts = split_long_strings(texts)

                for chunk in texts:
                    # Prepare the data payload as a dictionary
                    payload = {"documents": [{"text": chunk}]}
                    
                    # Make the POST request
                    response = requests.post(url, json=payload, headers=headers)
                    
                    # Check for successful request
                    if response.status_code != 200:
                        print(f"Failed to add document: {response.text}")

        before = after
        time.sleep(1)  # Check for new files every second

# Customize the folder to monitor
folder_to_watch = "/Users/rishiraj/tensorlake/test/papers"  # Replace with the actual folder path

if __name__ == "__main__":
    monitor_folder(folder_to_watch) 
