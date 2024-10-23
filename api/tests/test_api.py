# api/tests/test_api.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_news(client):
    """Test the /api/news endpoint"""
    response = client.get('/api/news')
    assert response.status_code in [200, 500]  # Check if it returns a success or fallback response
    json_data = response.get_json()
    assert 'articles' in json_data
