# api/app.py
from flask import Flask, jsonify
from data_fetcher import fetch_news_from_sources
from mock_data import generate_mock_articles

app = Flask(__name__)

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        articles = fetch_news_from_sources()
        return jsonify({'articles': articles}), 200
    except Exception as e:
        # Fallback to mock data in case of an error
        return jsonify({'articles': generate_mock_articles()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
