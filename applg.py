import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import test1
import json

json_data = json.loads(vars.GET_JSON_CONTENTS)
cred = credentials.Certificate(json_data)


def initialize_firebase_app():
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)


# Function to authenticate user with Firebase
def authenticate_with_firebase(email, password):
    try:
        user = auth.get_user_by_email(email)
        if user:
            return user.uid
    except auth.AuthError as e:
        st.warning(f'Authentication failed: {e}')


# Function to create a new user account with Firebase
def create_firebase_user(email, password, username):
    try:
        user = auth.create_user(email=email, password=password, uid=username)
        st.success('Account created successfully!')
        st.markdown('Please login using your email and password')
        st.balloons()
        return user.uid
    except ValueError:
        st.warning('Account creation failed. Please try again.')
        return None


# Function to change the password of an existing user
def change_password(uid, email, new_password):
    try:
        user = auth.update_user(
            uid=uid,
            email=email,
            password=new_password
        )
        st.success('Password changed successfully Login to your authenticate!')
        return True
    except ValueError as e:
        st.warning(f'Password change failed: {e}')
        return False


# Function to check if user is authenticated
def is_authenticated():
    return 'user_id' in st.session_state and st.session_state.user_id


# Function to check if cookie has expired
def cookie_has_expired():
    if 'expiry_timestamp' in st.session_state:
        expiry_timestamp = st.session_state.expiry_timestamp
        if datetime.utcnow() > expiry_timestamp:
            return True
    return False


# Function to initialize database table if not exists
def create_table(conn, cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS blogtable(author TEXT, title TEXT, article TEXT, postdate DATE)')
    conn.commit()


# Function to check if user is authenticated and redirect accordingly
def check_authentication():
    if is_authenticated() and not cookie_has_expired():
        return True
    else:
        return False


def user_exists(email):
    try:
        auth.get_user_by_email(email)
        return True
    except:
        return False


# Main function
# Main function
# Main function
def main():
    """A Simple CRUD Blog"""
    initialize_firebase_app()  # Initialize Firebase app

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    create_table(conn, cursor)  # Ensure the table is created

    st.title('Welcome to News-Hub Connect')

    if check_authentication():
        # User is authenticated and cookie has not expired
        test1.main()
    else:
        # User is not authenticated or cookie has expired
        # Login/Signup choice
        choice = st.selectbox('Login/Signup', ['Login', 'Sign Up', 'Forgot Password'], key='login_signup')

        if choice == 'Login':
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')
            if st.button('Login'):
                user_id = authenticate_with_firebase(email, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.expiry_timestamp = datetime.utcnow() + timedelta(days=30)
                    st.success('You are logged in!')
                    test1.main()  # Assuming blog.run() does something after successful login
                else:
                    st.warning(
                        'Authentication failed. dont worry Change your password through forgot password enjoy!!!!.')
        elif choice == 'Sign Up':
            email = st.text_input('Email Address')
            password = st.text_input('Password', type='password')
            username = st.text_input('Enter your unique username')
            if st.button('Register for your Blog'):
                user_id = create_firebase_user(email, password, username)
                if user_id:
                    st.session_state.user_id = user_id
                    st.session_state.expiry_timestamp = datetime.utcnow() + timedelta(days=30)
        elif choice == 'Forgot Password':
            email = st.text_input('Enter your email')
            old_password = st.text_input('Enter your new password', type='password')
            new_password = st.text_input('New Password', type='password')
            if st.button('Change'):
                user_id = authenticate_with_firebase(email, old_password)
                if user_id:
                    if change_password(user_id, email, new_password):
                        st.success('Password changed successfully!')
                    else:
                        st.warning('Password change failed. Please try again.')
                else:
                    st.warning('User not found. Please check your email.')

# Check if the app is run directly
