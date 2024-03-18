import streamlit as st
import sqlite3
from functools import wraps
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Functions
def create_table(conn, cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT, title TEXT, article TEXT, postdate DATE)')
    conn.commit()


def add_data(conn, cursor, author, title, article, postdate):
    cursor.execute('INSERT INTO blogtable(author, title, article, postdate) VALUES (?, ?, ?, ?)',
                   (author, title, article, postdate))
    conn.commit()


def view_all_notes(conn, cursor):
    cursor.execute('SELECT * FROM blogtable')
    data = cursor.fetchall()
    return data


def view_all_titles(conn, cursor):
    cursor.execute('SELECT DISTINCT title FROM blogtable')
    data = cursor.fetchall()
    return data


def get_blog_by_title(conn, cursor, title):
    cursor.execute('SELECT * FROM blogtable WHERE title=?', (title,))
    data = cursor.fetchall()
    return data


def get_blog_by_author(conn, cursor, author):
    cursor.execute('SELECT * FROM blogtable WHERE author=?', (author,))
    data = cursor.fetchall()
    return data


def delete_data(conn, cursor, title):
    cursor.execute('DELETE FROM blogtable WHERE title=?', (title,))
    conn.commit()


def readingTime(article):
    words = article.split()
    reading_time = len(words) / 200.0  # Assuming 200 words per minute
    return round(reading_time, 2)
# Layout Templates
html_temp = """
<div style="background-color:{};padding:10px;border-radius:10px">
<h1 style="color:{};text-align:center;">Simple Blog</h1>
</div>
"""
title_temp = """
<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6>
<br/><br/> 
<p style="text-align:justify">{}</p>
</div>
"""
head_message_temp = """
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h1>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author:{}</h6>
<h6>Post Date: {}</h6>
</div>
"""
full_message_temp = """
<div style="background-color:silver;overflow-x: auto; padding:10px;border-radius:5px;margin:10px;">
<p style="text-align:justify;color:black;padding:10px">{}</p>
</div>
"""


# Session State



# Login


# Main function
def main():
    """A Simple CRUD Blog"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    create_table(conn, cursor)  # Ensure the table is created
    st.markdown(html_temp.format('royalblue', 'white'), unsafe_allow_html=True)

    menu = ["Home", "View Posts", "Add Posts", "Search", "Manage Blog"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        st.subheader("Home")
        result = view_all_notes(conn, cursor)
        for i in result:
            b_author, b_title, b_article, b_post_date = i
            st.markdown(title_temp.format(b_title, b_author, b_article), unsafe_allow_html=True)

    elif choice == "View Posts":
        st.subheader("View Articles")
        all_titles = [i[0] for i in view_all_titles(conn, cursor)]
        postlist = st.sidebar.selectbox("View Posts", all_titles)
        post_result = get_blog_by_title(conn, cursor, postlist)
        for i in post_result:
            b_author, b_title, b_article, b_post_date = i
            st.text("Reading Time:{}".format(readingTime(b_article)))
            st.markdown(head_message_temp.format(b_title, b_author, b_post_date), unsafe_allow_html=True)
            st.markdown(full_message_temp.format(b_article), unsafe_allow_html=True)

    elif choice == "Add Posts":
        st.subheader("Add Articles")
        add_posts(conn, cursor)

    elif choice == "Search":
        st.subheader("Search Articles")
        search_term = st.text_input('Enter Search Term')
        search_choice = st.radio("Field to Search By", ("title", "author"))

        if st.button("Search"):
            if search_choice == "title":
                article_result = get_blog_by_title(conn, cursor, search_term)
            elif search_choice == "author":
                article_result = get_blog_by_author(conn, cursor, search_term)

            for i in article_result:
                b_author, b_title, b_article, b_post_date = i
                st.text("Reading Time:{}".format(readingTime(b_article)))
                st.markdown(head_message_temp.format(b_title, b_author, b_post_date), unsafe_allow_html=True)
                st.markdown(full_message_temp.format(b_article), unsafe_allow_html=True)

    elif choice == "Manage Blog":
        st.subheader("Manage Articles")
        result = view_all_notes(conn, cursor)
        clean_db = pd.DataFrame(result, columns=["Author", "Title", "Articles", "Post Date"])
        st.dataframe(clean_db)

        unique_titles = [i[0] for i in view_all_titles(conn, cursor)]
        delete_blog_by_title = st.selectbox("Unique Title", unique_titles)
        new_df = clean_db
        if st.button("Delete"):
            delete_data(conn, cursor, delete_blog_by_title)
            st.warning("Deleted: '{}'".format(delete_blog_by_title))

        if st.checkbox("Metrics"):
            new_df['Length'] = new_df['Articles'].str.len()
            st.dataframe(new_df)

            st.subheader("Author Stats")
            new_df["Author"].value_counts().plot(kind='bar')
            st.pyplot()

            st.subheader("Author Stats")
            new_df['Author'].value_counts().plot.pie(autopct="%1.1f%%")
            st.pyplot()

        if st.checkbox("Word Cloud"):
            st.subheader("Generate Word Cloud")
            text = ','.join(new_df['Articles'])
            wordcloud = WordCloud().generate(text)
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            st.pyplot()

        if st.checkbox("BarH Plot"):
            st.subheader("Length of Articles")
            new_df['Length'] = new_df['Articles'].str.len()
            barh_plot = new_df.plot.barh(x='Author', y='Length', figsize=(20, 10))
            st.pyplot()


# Add posts (Requires login)
def add_posts(conn, cursor):
    blog_author = st.text_input("Enter Author Name", max_chars=50)
    blog_title = st.text_input("Enter Post Title")
    blog_article = st.text_area("Post Article Here", height=200)
    blog_post_date = st.date_input("Date")
    if st.button("Add"):
        add_data(conn, cursor, blog_author, blog_title, blog_article, blog_post_date)
        st.success("Post:'{}' saved".format(blog_title))


# Check if login is required and redirect accordingly

