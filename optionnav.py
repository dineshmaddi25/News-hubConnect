from dupnewsapi import display_saved_articles
import dupnewsapi
import applg
from streamlit_card import card as st_card
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

st.set_page_config(page_title='InNews🇮🇳: A Summarised News📰 Portal', page_icon='./Meta/newspaper.ico')
image = Image.open('./Meta/newspaper.png')
selected = option_menu(
    menu_title=None,
    options=["Home", "News Blog", "Saved Articles", "Login/Sign_UP"],
    default_index=0,
    orientation="horizontal",
)
is_loggin = True
if selected == "Home":
    st.image(image, use_column_width=False)
    st.write("""
       🌟 **Welcome to News Hub!**

       News Hub is your ultimate destination for staying informed and up-to-date with the latest news, trends, 
       and stories from around the world. Whether you're interested in politics, technology, entertainment, 
       or sports, News Hub has you covered!

       **Discover:** Explore trending news stories or dive deep into your favorite topics with ease.
       **Save:** Bookmark articles for later reading, ensuring you never miss out on captivating content.
       **Share:** Spread the knowledge! Share noteworthy articles with friends and family effortlessly.
       """)

    st.write("""
       📌 **How it Works:**
       1. **Select your Country:** Choose your country to receive relevant, location-based news updates.
       2. **Choose a Category:** Explore trending news, favorite topics, or conduct custom searches based on your interests.
       3. **Enjoy Seamless Reading:** Dive into articles, save your favorites, and share insights with the world.
       """)
    # Example usage

    # Read the image file

    import streamlit as st
    import base64


    def display_cards():
        # Define the details for each card
        card_details = [
            {
                "title": "My LinkedIn Profile",
                "text": "Connect with me on LinkedIn!",
                "image_path": r"DSC05985-2.jpg",
                "url": "https://www.linkedin.com/in/dinesh-maddi/"
            },
            {
                "title": "My GitHub Profile",
                "text": "Check out my GitHub!",
                "image_path": r"wp3082259-github-wallpapers.png",
                "url": "https://github.com/dineshmaddi25"
            },
            {
                "title": "Check Out My Portfolio",
                "text": "Read my latest blog posts!",
                "image_path": r"Screenshot 2024-03-17 100835.png",
                "url": "https://dineshmaddiportfolio.netlify.app/"  # Replace with your blog URL
            }
        ]

        # Display each card in the sidebar
        for i, details in enumerate(card_details, start=1):
            with st.sidebar:
                st.subheader(f"Card {i}")
                with open(details["image_path"], "rb") as f:
                    data = f.read()
                    encoded = base64.b64encode(data)

                # Create the base64 encoded data URI
                data_uri = "data:image/jpeg;base64," + encoded.decode("utf-8")

                st_card(
                    title=details['title'],
                    text=details['text'],
                    image=data_uri,
                    url=details['url']
                )


    # Call the function to display the cards in the sidebar
    display_cards()
elif selected == "News Blog":
    dupnewsapi.main()
elif selected == "Saved Articles":
    user_email = st.text_input("Enter your Email to Validate??")
    display_saved_articles(user_email)
elif selected == "Login/Sign_UP":
    applg.main()
