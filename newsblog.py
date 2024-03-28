import pycountry
import streamlit as st
from PIL import Image
import requests
from urllib.request import urlopen
import io
from streamlit_option_menu import option_menu

st.set_page_config(page_title='News-Hub: Connect📰 Portal', page_icon='./Meta/newspaper.ico')


category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic']
def add_notes():
    # Add a notes section to the right sidebar
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
add_notes()
add_interesting_facts()
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
    site = f"https://newsapi.org/v2/everything?q={topic}&language={language_code}&apiKey="
    return site

def fetch_top_news(country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/everything?q=general&language={language_code}&apiKey="
    return site

def fetch_category_news(topic, country):
    language_code = countries[country]
    site = f"https://newsapi.org/v2/everything?q={topic}&language={language_code}&apiKey="
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

def display_news(url, country):
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
                st.image(image_url, caption='Image', use_column_width=True)
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

# Create the navbar
def app():
    selected = option_menu(
        menu_title=None,
        options=["News Blog", "Saved Articles", "Read news", "Login/Sign_UP"],
        default_index=0,
        orientation="horizontal",
    )

    # Display the selected option
    st.write("You selected:", selected)
    image = Image.open('./Meta/newspaper.png')
    image1=Image.open('./Meta/image.jpg')
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
        st.subheader("Here is the Trending🔥 news for you")
        news_list = fetch_top_news(Countname)
        display_news(news_list, Countname)  # Pass Countname as the country argument

    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            news_list = fetch_category_news(chosen_topic, Countname)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(chosen_topic))
                display_news(news_list, Countname)  # Pass Countname as the country argument
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

