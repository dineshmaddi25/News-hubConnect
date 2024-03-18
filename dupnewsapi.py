import streamlit as st
import sqlite3
from PIL import Image
import requests
from urllib.request import urlopen
import io
from streamlit_card import card as st_card
from applg import user_exists
from dotenv import load_dotenv
import os

load_dotenv(".env")
apikey = os.getenv("API_KEY")
category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic']


def add_notes():
    st.sidebar.subheader("Notes")
    user_notes = st.sidebar.text_area("Make Notes Here:")
    if st.sidebar.button("Save Notes"):
        save_notes(user_notes)


def add_interesting_facts():
    # Add interesting facts to the right sidebar
    st.sidebar.subheader("Interesting Facts 💡")
    fact_1 = "Did you know? The first email was sent by Ray Tomlinson in 1971."
    fact_2 = "The average person spends around 6 years of their life dreaming."
    fact_3 = "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible."
    st.sidebar.markdown("- " + fact_1)
    st.sidebar.markdown("- " + fact_2)
    st.sidebar.markdown("- " + fact_3)

    # Add link to see more interesting facts
    st.sidebar.markdown("[See more interesting facts](https://www.rd.com/list/interesting-facts/)")


def save_notes(notes):
    # This function could save the notes to a file or database
    st.sidebar.write("Notes saved successfully!")


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
    site = f"https://newsapi.org/v2/everything?q=general&language={language_code}&apiKey={apikey}"
    return site


def fetch_category_news(topic, country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/everything?q={topic}&language={language_code}&apiKey={apikey}"
    return site


def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, use_column_width=True)


def initialize_database():
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    # Create articles table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS articles 
                 (id INTEGER PRIMARY KEY, email TEXT, title TEXT, author TEXT, publishedAt TEXT, source TEXT, description TEXT, content TEXT, imageUrl TEXT,url TEXT)''')
    # Create users table if not exist
    conn.commit()
    conn.close()


# Function to insert email into the database

def insert_email(email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()
    c.execute("INSERT INTO articles (email) VALUES (?)", (email,))
    conn.commit()
    conn.close()
    st.success("Email saved successfully")


# Function to save article to the database
def save_article_to_database(article, email):
    conn = sqlite3.connect('news_articles.db')
    c = conn.cursor()

    # Check if the email exists in the table
    c.execute("SELECT * FROM articles WHERE email=?", (email,))
    existing_row = c.fetchone()

    if existing_row:
        # Update the existing row
        c.execute("""UPDATE articles 
                     SET title=?, author=?, publishedAt=?, source=?, description=?, content=?, imageUrl=?, url=?
                     WHERE email=?""",
                  (article.get('title'), article.get('author'), article.get('publishedAt'), article['source']['name'],
                   article.get('description'), article.get('content', ''), article.get('urlToImage', ''),
                   article.get('url', ''), email))
        st.success(f"Article '{article['title']}' updated successfully for user '{email}'")
    else:
        # Insert a new row
        c.execute(
            "INSERT INTO articles (email, title, author, publishedAt, source, description, content, imageUrl) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (email, article.get('title'), article.get('author'), article.get('publishedAt'), article['source']['name'],
             article.get('description'), article.get('content', ''), article.get('urlToImage', ''),
             article.get('url', '')))
        st.success(f"Article '{article['title']}' saved successfully for user '{email}'")

    conn.commit()
    conn.close()


# Add authentication
def display_saved_articles_as_cards(title, text, image_url, url, key=None):
    """
    Display a custom card for a saved article.

    Parameters:
        title (str): The title of the article.
        text (str): The text content of the card.
        image_url (str): The URL of the image associated with the article.
        url (str): The URL to which the card links.
        key (str or None): An optional key to make the widget unique.
    """
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
        st.warning("No saved articles found for this email.")
        return

    st.subheader("Saved Articles:")
    for i, article in enumerate(saved_articles):
        # Generate a unique key for each card
        card_key = f"saved_article_{i}"
        display_saved_articles_as_cards(article[2], article[6], article[8], article[9], key=card_key)


# Function to display news articles
def display_news(url, country, email):
    count = country
    st.write(count)
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
        try:
            image_url = article.get('urlToImage')
            if image_url:
                image_data = requests.get(image_url).content
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption='Image', use_column_width=True)
        except Exception as e:
            st.error("Error loading image: " + str(e))
            st.image(Image.open('./Meta/no_image.jpg'), use_column_width=True)

        # Add button to display full content
        button_key = f"article_{i}_button"
        if st.button("Read Full Article", key=button_key):
            content = article.get('content')
            if content:
                st.write("Content:")
                st.write(content)
            st.markdown(f"[Read more at {article['source']['name']}...]({article['url']})")
        save_button_key = f"save_article_{i}"

        if st.button(f"Save Article {i + 1}", key=save_button_key):
            save_article_to_database(article, email)


def main():
    initialize_database()
    email = st.text_input('Enter Email Address to save articles ')
    if email:
        insert_email(email)  # Insert email into the databas

    add_notes()
    add_interesting_facts()
    # Display the selected option

    image = Image.open('./Meta/newspaper.png')
    image1 = Image.open('./Meta/image.jpg')
    col2, col3 = st.columns([1000, 1])
    cat_op = ''

    with col2:
        st.markdown('''
            # Introducing News Hub Connect: Your Personalized News Experience 🌐📰

            Welcome to **News Hub Connect** — your gateway to a personalized news experience like never before! Say goodbye to information overload and hello to curated, insightful content tailored just for you.

            ''', unsafe_allow_html=True)

        st.markdown('''
            <p style="color: #555; font-size: 18px;">Headline Highlights:</p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="color: #007bff;"><strong>Stay Informed:</strong> Get the latest updates from around the globe, right at your fingertips.</li>
                <li style="color: #007bff;"><strong>Curated Selection:</strong> Dive into a curated selection of trending news, favorite topics, and custom searches.</li>
                <li style="color: #007bff;"><strong>Save & Scroll:</strong> Save articles of interest and scroll endlessly through captivating reads.</li>
            </ul>

            ''', unsafe_allow_html=True)

        st.markdown('''
            <p style="color: #555; font-size: 18px;">Your News, Your Way:</p>
            <p style="color: #333;">News Hub Connect empowers you to customize your news consumption experience according to your preferences and interests. Whether you're a tech enthusiast, a sports fanatic, or a news junkie, there's something here for everyone.</p>

            ''', unsafe_allow_html=True)

        st.markdown('''
            <p style="color: #555; font-size: 18px;">Discover, Save, Share:</p>
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="color: #007bff;"><strong>Discover:</strong> Explore trending news stories or dive deep into your favorite topics with ease.</li>
                <li style="color: #007bff;"><strong>Save:</strong> Bookmark articles for later reading, ensuring you never miss out on captivating content.</li>
                <li style="color: #007bff;"><strong>Share:</strong> Spread the knowledge! Share noteworthy articles with friends and family effortlessly.</li>
            </ul>

            ''', unsafe_allow_html=True)

        st.markdown('''
            <p style="color: #555; font-size: 18px;">How it Works:</p>
            <ol style="list-style-type: decimal; padding-left: 20px;">
                <li style="color: #333;"><strong>Select your Country:</strong> Choose your country to receive relevant, location-based news updates.</li>
                <li style="color: #333;"><strong>Choose a Category:</strong> Explore trending news, favorite topics, or conduct custom searches based on your interests.</li>
                <li style="color: #333;"><strong>Enjoy Seamless Reading:</strong> Dive into articles, save your favorites, and share insights with the world.</li>
            </ol>

            ''', unsafe_allow_html=True)

        st.markdown('''
            <p style="color: #555; font-size: 18px;">Elevate Your News Experience:</p>
            <p style="color: #333;">With News Hub Connect, the world's latest happenings are just a click away. Stay informed, stay engaged, and stay connected with News Hub Connect today!</p>
            ''', unsafe_allow_html=True)
    with col3:
        st.image(image, use_column_width=False)

    Countname = st.selectbox('Select your Country', list(countries.keys()))
    cat_op = st.selectbox('Select your Category', category)
    if cat_op == '--Select--':
        st.warning('Please Select Type!!')
    elif cat_op == category[1]:
        news_list = fetch_top_news(Countname)
        display_news(news_list, Countname, email)
        # Pass Countname as the country argument

    elif cat_op == category[2]:

        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE',
                     'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            news_list = fetch_category_news(chosen_topic, Countname)
            if news_list:

                st.subheader("✅ Here are the some {} News for you".format(chosen_topic))
                display_news(news_list, Countname, email)
            # Pass Countname as the country argument
            else:
                st.error("No News found for {}".format(chosen_topic))
    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(user_topic_pr, Countname)
            if news_list:
                st.subheader("✅ Here are some news articles for {}".format(user_topic.capitalize()))

                r = requests.get(news_list)
                if r.status_code != 200:
                    st.error(f"Failed to fetch news. Status code: {r.status_code}")
                else:
                    news_data = r.json()
                    articles = news_data.get('articles', [])
                    if not articles:
                        st.warning("No articles found.")
                    else:
                        for i, article in enumerate(articles):
                            st.header(article['title'])
                            st.write(article['publishedAt'])
                            if article['author']:
                                st.write("Author:", article['author'])
                            st.write("Source:", article['source']['name'])
                            st.write("Description:", article['description'])
                            try:
                                image_url = article.get('urlToImage')
                                if image_url:
                                    st.image(image_url, caption='Image', use_column_width=True)
                            except Exception as e:
                                st.error("Error loading image: " + str(e))
                                st.image(Image.open('./Meta/no_image.jpg'), use_column_width=True)

                            content = article.get('content')
                            if content:
                                st.write("Content:")
                                st.write(content)
                            st.markdown(f"[Read more at {article['source']['name']}...]({article['url']})")
            else:
                st.error("No News found for {}".format(user_topic))

    else:
        st.warning("Please write Topic Name to Search🔍")
