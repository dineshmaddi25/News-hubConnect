# api/data_fetcher.py
import requests

def fetch_news_from_sources():
    news_sources = [
        {
            'name': 'NewsAPI',
            'url': 'https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY'  # Replace YOUR_API_KEY
        },
        {
            'name': 'Another Source',
            'url': 'https://example.com/api/news'  # Add another news source URL if needed
        }
    ]
    
    articles = []
    
    for source in news_sources:
        try:
            response = requests.get(source['url'])
            if response.status_code == 200:
                articles.extend(response.json().get('articles', []))
            else:
                print(f"Failed to fetch from {source['name']}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from {source['name']}: {e}")

    if not articles:
        raise ValueError("No articles found from the specified sources.")
    
    return articles
