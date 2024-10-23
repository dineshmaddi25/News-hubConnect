
# api/mock_data.py
import random
from faker import Faker

fake = Faker()

def generate_mock_articles(num_articles=5):
    articles = []
    for _ in range(num_articles):
        articles.append({
            'title': fake.sentence(),
            'author': fake.name(),
            'publishedAt': fake.date_time_this_year().isoformat(),
            'source': {'name': fake.company()},
            'description': fake.paragraph(),
            'content': fake.paragraphs(nb=3, join=True),
            'urlToImage': fake.image_url(),
            'url': fake.url()
        })
    return articles
