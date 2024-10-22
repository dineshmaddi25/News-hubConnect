import streamlit as st
import sqlite3
from PIL import Image
import requests
from urllib.request import urlopen
import io
from streamlit_card import card as st_card
import os
import nltk
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Your existing API Key
apikey = str(os.environ.get("API_KEY"))
category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic']

# Function to add notes in the sidebar
def add_notes():
    st.sidebar.subheader("Notes")
    user_notes = st.sidebar.text_area("Make Notes Here:")
    if st.sidebar.button("Save Notes"):
        save_notes(user_notes)

# Function to display interesting facts
def add_interesting_facts():
    st.sidebar.subheader("Interesting Facts 💡")
    facts = [
        "Did you know? The first email was sent by Ray Tomlinson in 1971.",
        "The average person spends around 6 years of their life dreaming.",
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible."
    ]
    for fact in facts:
        st.sidebar.markdown("- " + fact)

    st.sidebar.markdown("[See more interesting facts](https://www.rd.com/list/interesting-facts/)")

def save_notes(notes):
    st.sidebar.write("Notes saved successfully!")

# Map countries to language codes
countries = {
    'Saudi Arabia': 'ar',
    'Germany': 'de',
    'United States': 'en',
    'Spain': 'es',
    'France': 'fr',
    'India': 'hi',
    'Italy': 'it',
    'Netherlands': 'nl',
    'Norway': 'no',
    'Portugal': 'pt',
    'Russia': 'ru',
    'Sweden': 'sv',
    'Unknown Country': 'ud',
    'China': 'zh'
}

def fetch_news_search_topic(topic, country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/everything?q={topic}&language={language_code}&apiKey={apikey}"
    return site

def fetch_top_news(country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/top-headlines?country={language_code}&apiKey={apikey}"
    return site

def fetch_category_news(topic, country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/everything?q={topic}&language={language_code}&apiKey={apikey}"
    return site

def initialize_database():
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles 
                 (id INTEGER PRIMARY KEY, email TEXT, title TEXT, author TEXT, publishedAt TEXT, source TEXT, description TEXT, content TEXT, imageUrl TEXT, url TEXT)''')
    conn.commit()
    conn.close()

def insert_email(email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute("INSERT INTO articles (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    st.success("Email saved successfully! You can now save articles.")

def save_article_to_database(article, email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE email=?", (email,))
    existing_row = c.fetchone()

    if existing_row:
        c.execute("""UPDATE articles 
                     SET title=?, author=?, publishedAt=?, source=?, description=?, content=?, imageUrl=?, url=?
                     WHERE email=?""",
                  (article.get('title'), article.get('author'), article.get('publishedAt'), article['source']['name'],
                   article.get('description'), article.get('content', ''), article.get('urlToImage', ''), article.get('url', ''), email))
        st.success(f"Article '{article['title']}' updated successfully for user '{email}'")
    else:
        c.execute(
            "INSERT INTO articles (email, title, author, publishedAt, source, description, content, imageUrl, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (email, article.get('title'), article.get('author'), article.get('publishedAt'), article['source']['name'],
             article.get('description'), article.get('content', ''), article.get('urlToImage', ''),
             article.get('url', '')))
        st.success(f"Article '{article['title']}' saved successfully for user '{email}'")

    conn.commit()
    conn.close()

def display_saved_articles_as_cards(title, text, image_url, url, key=None):
    st_card(
        title=title,
        text=text,
        image=image_url,
        url=url,
        key=key
    )

def display_saved_articles(email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE email=?", (email,))
    saved_articles = c.fetchall()
    conn.close()

    if not saved_articles:
        st.warning("No saved articles found for this email. Start saving your favorite articles!")
        return

    st.subheader("Saved Articles:")
    for i, article in enumerate(saved_articles):
        card_key = f"saved_article_{i}"
        display_saved_articles_as_cards(article[2], article[6], article[8], article[9], key=card_key)

def preprocess_text(text):
    # Tokenize and remove stop words
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalnum()]  # Keep only alphanumeric tokens
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stop words
    return tokens

def get_article_vectors(articles):
    # Create a list of tokenized articles
    tokenized_articles = [preprocess_text(article[6]) for article in articles]  # Assuming column 6 is 'description'

    # Train Word2Vec model
    model = Word2Vec(sentences=tokenized_articles, vector_size=100, window=5, min_count=1, workers=4)
    
    # Create a vector for each article
    article_vectors = []
    for tokens in tokenized_articles:
        if tokens:  # Ensure we don't process empty lists
            vector = np.mean([model.wv[token] for token in tokens if token in model.wv], axis=0)
            article_vectors.append(vector)
        else:
            article_vectors.append(np.zeros(100))  # Return zero vector for empty articles

    return np.array(article_vectors)

def suggest_articles(user_input, email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute("SELECT * FROM articles WHERE email=?", (email,))
    saved_articles = c.fetchall()
    conn.close()

    if not saved_articles:
        st.warning("No saved articles found for suggestion. Save some articles first!")
        return

    # Preprocess saved articles and get their vectors
    article_vectors = get_article_vectors(saved_articles)

    # Preprocess user input
    user_tokens = preprocess_text(user_input)
    if not user_tokens:
        st.warning("No valid tokens found in your input. Please try again.")
        return

    # Get vector for user input
    user_vector = np.mean([model.wv[token] for token in user_tokens if token in model.wv], axis=0)

    # Calculate similarity with saved articles
    similarities = cosine_similarity([user_vector], article_vectors).flatten()

    # Get the top 3 most similar articles
    similar_indices = similarities.argsort()[-3:][::-1]

    st.subheader("Suggested Articles Based on Your Input:")
    for index in similar_indices:
        article = saved_articles[index]
        display_saved_articles_as_cards(article[2], article[6], article[8], article[9])

def display_news(url, country, email):
    r = requests.get(url)
    if r.status_code != 200:
        st.error(f"Failed to fetch news. Status code: {r.status_code}")
        return
    news_data = r.json()
    articles = news_data.get('articles', [])
    if not articles:
        st.warning("No articles found.")
        return

    for i, article in enumerate(articles):
        st.header(article['title'])
        st.write(article['publishedAt'])
        if article['author']:
            st.write("Author:", article['author'])
        st.write("Source:", article['source']['name'])
        st.write("Description:", article['description'])

        # Load and display image
        image_url = article.get('urlToImage')
        if image_url:
            st.image(image_url, caption='Image', use_column_width=True)

        # Full content button
        button_key = f"article_{i}_button"
        if st.button("Read Full Article", key=button_key):
            content = article.get('content')
            if content:
                st.write("Content:")
                st.write(content)
            st.markdown(f"[Read more at {article['source']['name']}...]({article['url']})")
        
        # Save article button
        save_button_key = f"save_article_{i}"
        if st.button(f"Save Article {i + 1}", key=save_button_key):
            save_article_to_database(article, email)

def main():
    initialize_database()
    email = st.text_input('Enter Email Address to save articles ')
    if email:
        insert_email(email)

    add_notes()
    add_interesting_facts()

    image = Image.open('./Meta/newspaper.png')
    image1 = Image.open('./Meta/image.jpg')
    col2, col3 = st.columns([1000, 1])

    with col2:
        st.markdown('''# Introducing News Hub Connect: Your Personalized News Experience 🌐📰
            Welcome to **News Hub Connect** — your gateway to a personalized news experience like never before! 
            Say goodbye to information overload and hello to curated, insightful content tailored just for you.
            ''', unsafe_allow_html=True)

    with col3:
        st.image(image, use_column_width=False)

    country = st.selectbox("Select your Country", list(countries.keys()))
    selected_category = st.selectbox("Select News Category", category)

    if selected_category == 'Search🔍 Topic':
        search_topic = st.text_input("Enter Topic to Search")
        if search_topic and country:
            news_url = fetch_news_search_topic(search_topic, country)
            display_news(news_url, country, email)
            suggest_articles(search_topic, email)  # Suggest based on search topic

    elif selected_category == 'Trending🔥 News':
        if country:
            news_url = fetch_top_news(country)
            display_news(news_url, country, email)

    elif selected_category == 'Favourite💙 Topics':
        display_saved_articles(email)

# Run the app
if __name__ == "__main__":
    main()
