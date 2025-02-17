import requests

url = "https://www.reddit.com/r/popular.json"
headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyRedditScript/0.1)'}
response = requests.get(url, headers=headers)
print(response.json())
