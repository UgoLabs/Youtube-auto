import requests

def fetch_trending_data():
    url = "https://www.reddit.com/r/popular.json"
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; RedditTrendFetcher/1.0)'}
    response = requests.get(url, headers=headers)
    
    # Debug: Print response details
    print("Response Status Code:", response.status_code)
    print("Response Content (first 500 chars):", response.text[:500])
    
    try:
        data = response.json()
        trending_topics = [post['data']['title'] for post in data['data']['children']]
        return trending_topics
    except Exception as e:
        print(f"⚠️ Error parsing JSON: {e}")
        return []

if __name__ == "__main__":
    topics = fetch_trending_data()
    print("Trending topics from Reddit r/popular:")
    for topic in topics:
        print("-", topic)


