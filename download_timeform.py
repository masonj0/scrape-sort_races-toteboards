import requests

url = "https://www.timeform.com/horse-racing/racecards"
file_name = "timeform.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status() # Raise an exception for bad status codes
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(response.text)
    print(f"SUCCESS: Saved HTML from {url} to {file_name}")
except Exception as e:
    print(f"FAILURE: Could not fetch HTML. Error: {e}")
